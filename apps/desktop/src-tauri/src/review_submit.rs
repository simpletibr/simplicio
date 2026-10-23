//! Desktop review submission inbox.
//!
//! A submission is the verified local handoff between the Desktop review surface
//! and the owning agent. The Desktop writes one idempotent queue entry under
//! `.simplicio/review-inbox/` and returns a receipt. Nothing here notifies or
//! starts an agent session; the agent reads the inbox on its next turn.

use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

pub const SUBMISSION_SCHEMA: &str = "simplicio.review-submission/v1";
pub const RECEIPT_SCHEMA: &str = "simplicio.review-receipt/v1";
pub const REVIEW_SCHEMA: &str = "simplicio.desktop-review/v1";
pub const MAX_COMMENTS_CHARS: usize = 20_000;
const INBOX_RELATIVE: &str = ".simplicio/review-inbox";
const PLAN_DIGEST_RELATIVE: &str = ".simplicio/plan-digest";
const MAX_PLAN_DIGEST_BYTES: u64 = 4_096;

static TEMP_SEQUENCE: AtomicU64 = AtomicU64::new(1);

fn sha256_hex(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

/// `sha256:` followed by exactly 64 hexadecimal characters.
pub fn valid_digest(value: &str) -> bool {
    let value = value.trim();
    value.len() == 71
        && value
            .get(..7)
            .is_some_and(|prefix| prefix.eq_ignore_ascii_case("sha256:"))
        && value
            .get(7..)
            .is_some_and(|hex| hex.bytes().all(|byte| byte.is_ascii_hexdigit()))
}

fn canonical_digest(value: &str) -> Option<String> {
    let value = value.trim();
    valid_digest(value).then(|| value.to_ascii_lowercase())
}

/// Windows forbids `:` in file names, so the canonical file name replaces the
/// scheme separator: `sha256:<hex>` becomes `sha256-<hex>.json`.
pub fn entry_relative_path(digest: &str) -> Result<String, String> {
    let digest = canonical_digest(digest).ok_or_else(|| "review_digest_invalid".to_string())?;
    Ok(format!(
        "{INBOX_RELATIVE}/{}.json",
        digest.replace(':', "-")
    ))
}

/// A base is one revision argument, never an option or a second command.
pub fn valid_base_revision(base: &str) -> bool {
    let base = base.trim();
    !base.is_empty()
        && base.len() <= 256
        && !base.starts_with('-')
        && !base
            .chars()
            .any(|character| matches!(character, '\0' | '\n' | '\r'))
}

/// Paths reported by `git diff --git a/... b/...` headers.
pub fn changed_paths(diff: &str) -> Vec<String> {
    diff.lines()
        .filter_map(|line| line.strip_prefix("diff --git "))
        .filter_map(|rest| rest.find(" b/").map(|index| rest[index + 3..].to_string()))
        .collect()
}

pub fn is_protected_path(path: &str) -> bool {
    let normalized = path.replace('\\', "/");
    let name = normalized.rsplit('/').next().unwrap_or(normalized.as_str());
    matches!(
        name,
        "Cargo.toml"
            | "Cargo.lock"
            | "package-lock.json"
            | "install.sh"
            | "install.ps1"
            | "simplicio-update-manifest.json"
            | "SHA256SUMS"
    ) || normalized
        .split('/')
        .any(|segment| matches!(segment, ".github" | "schemas" | "migrations"))
}

/// Deterministic plan-lane gate. Precedence is fixed so the UI and the native
/// receipt never disagree: truncation, protected paths, missing plan digest,
/// plan digest mismatch, eligible.
pub fn auto_merge(
    review_digest: &str,
    truncated: bool,
    protected_path: bool,
    plan_digest: Option<&str>,
) -> Value {
    let review_digest = review_digest.trim().to_ascii_lowercase();
    let reason = if truncated {
        "truncated"
    } else if protected_path {
        "protected_path"
    } else {
        match plan_digest.map(str::trim).filter(|value| !value.is_empty()) {
            None => "plan_digest_missing",
            Some(value) => match canonical_digest(value) {
                Some(candidate) if candidate == review_digest => "eligible",
                _ => "plan_digest_mismatch",
            },
        }
    };
    json!({ "eligible": reason == "eligible", "reason": reason })
}

/// A Tauri argument wins; otherwise the first non-empty line of
/// `.simplicio/plan-digest`. Missing or oversized files count as missing.
pub fn resolve_plan_digest(repo: &Path, requested: Option<&str>) -> Option<String> {
    if let Some(value) = requested.map(str::trim).filter(|value| !value.is_empty()) {
        return Some(value.to_string());
    }
    let path = repo.join(PLAN_DIGEST_RELATIVE);
    let metadata = fs::metadata(&path).ok()?;
    if !metadata.is_file() || metadata.len() > MAX_PLAN_DIGEST_BYTES {
        return None;
    }
    let text = fs::read_to_string(path).ok()?;
    text.lines()
        .map(str::trim)
        .find(|line| !line.is_empty())
        .map(str::to_string)
}

pub fn bounded_comments(comments: &str) -> Result<&str, String> {
    let trimmed = comments.trim();
    if trimmed.is_empty() {
        return Err("review_comments_empty".to_string());
    }
    if trimmed.chars().count() > MAX_COMMENTS_CHARS {
        return Err("review_comments_too_large".to_string());
    }
    Ok(trimmed)
}

fn redact_token(token: &str) -> String {
    let lower = token.to_ascii_lowercase();
    for key in [
        "password=",
        "passwd=",
        "secret=",
        "token=",
        "api_key=",
        "apikey=",
        "access_key=",
    ] {
        if let Some(position) = lower.find(key) {
            let boundary = position + key.len();
            if token[boundary..].trim().is_empty() {
                continue;
            }
            return format!("{}[redacted]", &token[..boundary]);
        }
    }
    if let Some(position) = lower.find("bearer") {
        let boundary = position + "bearer".len();
        let remainder = token[boundary..].trim_start_matches([':', '-', '_']);
        if !remainder.trim().is_empty() {
            return format!("{}[redacted]", &token[..boundary]);
        }
    }
    let core = token.trim_matches(|character: char| {
        matches!(
            character,
            '"' | '\'' | '`' | '(' | ')' | '[' | ']' | '{' | '}' | ',' | ';' | '.'
        )
    });
    let vendor_prefix = [
        "sk-",
        "sk_",
        "ghp_",
        "gho_",
        "ghu_",
        "ghs_",
        "ghr_",
        "github_pat_",
    ]
    .iter()
    .any(|prefix| core.starts_with(prefix) && core.len() > prefix.len() + 8);
    let slack = core.starts_with("xox")
        && core.len() > 12
        && core[3..].starts_with(|character| "aboprs".contains(character));
    let aws = core.starts_with("AKIA")
        && core.len() == 20
        && core[4..]
            .chars()
            .all(|character| character.is_ascii_uppercase() || character.is_ascii_digit());
    if vendor_prefix || slack || aws {
        return "[redacted]".to_string();
    }
    token.to_string()
}

fn bearer_marker(token: &str) -> bool {
    token
        .trim_matches(|character: char| !character.is_ascii_alphabetic())
        .eq_ignore_ascii_case("bearer")
}

fn redact_line(line: &str) -> String {
    let mut result = String::with_capacity(line.len());
    let mut token = String::new();
    let mut redact_next = false;
    for character in line.chars() {
        if character.is_whitespace() {
            if !token.is_empty() {
                if redact_next {
                    result.push_str("[redacted]");
                    redact_next = false;
                } else {
                    result.push_str(&redact_token(&token));
                    redact_next = bearer_marker(&token);
                }
                token.clear();
            }
            result.push(character);
        } else {
            token.push(character);
        }
    }
    if !token.is_empty() {
        if redact_next {
            result.push_str("[redacted]");
        } else {
            result.push_str(&redact_token(&token));
        }
    }
    result
}

/// Removes obvious credential material before the comments are persisted.
/// Comment text is still untrusted input for the agent; redaction is a safety
/// net, not an instruction to execute anything found in the file.
pub fn redact_comments(comments: &str) -> String {
    let mut output = Vec::new();
    let mut inside_private_key = false;
    for line in comments.split('\n') {
        if line.contains("-----BEGIN") && line.contains("PRIVATE KEY") {
            inside_private_key = true;
            output.push("-----BEGIN PRIVATE KEY-----".to_string());
            continue;
        }
        if inside_private_key {
            if line.contains("-----END") && line.contains("PRIVATE KEY") {
                inside_private_key = false;
                output.push("-----END PRIVATE KEY-----".to_string());
            } else {
                output.push("[redacted]".to_string());
            }
            continue;
        }
        output.push(redact_line(line));
    }
    output.join("\n")
}

pub struct PreparedSubmission {
    pub entry: Value,
    pub path: PathBuf,
    pub relative_path: String,
}

fn review_string<'a>(review: &'a Value, key: &str) -> Result<&'a str, String> {
    review
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| "review_unavailable".to_string())
}

/// Rejects a submission unless the caller still holds the exact diff digest.
pub fn validate_digest(review: &Value, expected: &str) -> Result<(), String> {
    if !valid_digest(expected) {
        return Err("review_digest_invalid".to_string());
    }
    match review.get("digest").and_then(Value::as_str) {
        Some(actual) if actual.eq_ignore_ascii_case(expected.trim()) => Ok(()),
        _ => Err("review_digest_mismatch".to_string()),
    }
}

pub fn prepare(
    repo: &Path,
    review: &Value,
    comments: &str,
    plan_digest: Option<&str>,
    now_epoch_ms: u64,
) -> Result<PreparedSubmission, String> {
    if review.get("schema").and_then(Value::as_str) != Some(REVIEW_SCHEMA) {
        return Err("review_unavailable".to_string());
    }
    let digest = review_string(review, "digest")?;
    let digest = canonical_digest(digest).ok_or_else(|| "review_digest_invalid".to_string())?;
    let truncated = review
        .get("truncated")
        .and_then(Value::as_bool)
        .ok_or_else(|| "review_unavailable".to_string())?;
    let diff = review_string(review, "diff")?;
    let base = match review.get("base") {
        Some(Value::String(value)) => Value::String(value.clone()),
        _ => Value::Null,
    };
    let protected_paths = changed_paths(diff)
        .into_iter()
        .filter(|path| is_protected_path(path))
        .collect::<Vec<_>>();
    let plan_digest = plan_digest
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(str::to_string);
    let comments = bounded_comments(comments)?;
    let comments = redact_comments(comments);
    let comments_digest = format!("sha256:{}", sha256_hex(comments.as_bytes()));
    let comments_bytes = comments.len();
    let auto_merge = auto_merge(
        &digest,
        truncated,
        !protected_paths.is_empty(),
        plan_digest.as_deref(),
    );

    let mut canonical = Map::new();
    canonical.insert("digest".to_string(), Value::String(digest.clone()));
    canonical.insert(
        "repo".to_string(),
        Value::String(repo.display().to_string()),
    );
    canonical.insert("base".to_string(), base.clone());
    canonical.insert(
        "plan_digest".to_string(),
        plan_digest
            .clone()
            .map(Value::String)
            .unwrap_or(Value::Null),
    );
    canonical.insert(
        "comments_digest".to_string(),
        Value::String(comments_digest.clone()),
    );
    canonical.insert("comments_bytes".to_string(), json!(comments_bytes));
    canonical.insert("truncated".to_string(), json!(truncated));
    canonical.insert("protected_paths".to_string(), json!(protected_paths));
    canonical.insert("auto_merge".to_string(), auto_merge.clone());
    let canonical = Value::Object(canonical);
    let canonical_text =
        serde_json::to_string(&canonical).map_err(|_| "review_submission_invalid".to_string())?;
    let entry_digest = format!("sha256:{}", sha256_hex(canonical_text.as_bytes()));
    let receipt_id = format!("review-{}", &entry_digest[7..31]);

    let entry = json!({
        "schema": SUBMISSION_SCHEMA,
        "receipt_id": receipt_id,
        "entry_digest": entry_digest,
        "repo": repo.display().to_string(),
        "digest": digest,
        "base": base,
        "plan_digest": plan_digest,
        "comments": comments,
        "comments_digest": comments_digest,
        "comments_bytes": comments_bytes,
        "truncated": truncated,
        "protected_paths": protected_paths,
        "auto_merge": auto_merge,
        "redacted": true,
        "submitted_at_epoch_ms": now_epoch_ms
    });
    let relative_path = entry_relative_path(&digest)?;
    Ok(PreparedSubmission {
        entry,
        path: repo.join(&relative_path),
        relative_path,
    })
}

fn reject_symlink(path: &Path) -> Result<(), String> {
    match fs::symlink_metadata(path) {
        Ok(metadata) if metadata.file_type().is_symlink() => {
            Err("review_inbox_unavailable".to_string())
        }
        Ok(_) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(_) => Err("review_inbox_unavailable".to_string()),
    }
}

/// Review state is repository-local. A symlinked `.simplicio` or inbox could
/// redirect the write outside the repository, so both levels are rejected.
fn ensure_inbox_directory(repo: &Path) -> Result<(), String> {
    let state = repo.join(".simplicio");
    reject_symlink(&state)?;
    fs::create_dir_all(&state).map_err(|_| "review_inbox_unavailable".to_string())?;
    let inbox = repo.join(INBOX_RELATIVE);
    reject_symlink(&inbox)?;
    fs::create_dir_all(&inbox).map_err(|_| "review_inbox_unavailable".to_string())?;
    let metadata = fs::metadata(&inbox).map_err(|_| "review_inbox_unavailable".to_string())?;
    if !metadata.is_dir() {
        return Err("review_inbox_unavailable".to_string());
    }
    Ok(())
}

fn receipt(entry: &Value, relative_path: &str, idempotent: bool) -> Value {
    json!({
        "schema": RECEIPT_SCHEMA,
        "receipt_id": entry.get("receipt_id").cloned().unwrap_or(Value::Null),
        "path": relative_path,
        "entry_digest": entry.get("entry_digest").cloned().unwrap_or(Value::Null),
        "digest": entry.get("digest").cloned().unwrap_or(Value::Null),
        "comments_digest": entry.get("comments_digest").cloned().unwrap_or(Value::Null),
        "comments_bytes": entry.get("comments_bytes").cloned().unwrap_or(Value::Null),
        "plan_digest": entry.get("plan_digest").cloned().unwrap_or(Value::Null),
        "auto_merge": entry.get("auto_merge").cloned().unwrap_or(Value::Null),
        "idempotent": idempotent,
        "redacted": true
    })
}

/// Writes the queue entry once. Repeating the exact submission returns the
/// existing entry and receipt without rewriting the file.
pub fn submit(
    repo: &Path,
    review: &Value,
    comments: &str,
    plan_digest: Option<&str>,
    now_epoch_ms: u64,
) -> Result<Value, String> {
    let prepared = prepare(repo, review, comments, plan_digest, now_epoch_ms)?;
    ensure_inbox_directory(repo)?;
    reject_symlink(&prepared.path)?;

    if let Ok(bytes) = fs::read(&prepared.path) {
        if let Ok(existing) = serde_json::from_slice::<Value>(&bytes) {
            if existing.get("schema").and_then(Value::as_str) == Some(SUBMISSION_SCHEMA)
                && existing.get("redacted").and_then(Value::as_bool) == Some(true)
                && existing.get("entry_digest").and_then(Value::as_str)
                    == prepared.entry.get("entry_digest").and_then(Value::as_str)
            {
                return Ok(receipt(&existing, &prepared.relative_path, true));
            }
        }
    }

    let bytes = serde_json::to_vec_pretty(&prepared.entry)
        .map_err(|_| "review_submission_invalid".to_string())?;
    let sequence = TEMP_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    let temporary = prepared.path.with_file_name(format!(
        ".{}.tmp-{}-{sequence}",
        prepared
            .path
            .file_name()
            .and_then(|value| value.to_str())
            .unwrap_or("review"),
        std::process::id()
    ));
    fs::write(&temporary, &bytes).map_err(|_| "review_inbox_unavailable".to_string())?;
    if fs::rename(&temporary, &prepared.path).is_err() {
        let _ = fs::remove_file(&temporary);
        return Err("review_inbox_unavailable".to_string());
    }
    Ok(receipt(&prepared.entry, &prepared.relative_path, false))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicU64;

    const DIGEST: &str = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    const OTHER_DIGEST: &str =
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

    static NEXT_FIXTURE: AtomicU64 = AtomicU64::new(1);

    fn diff_with(paths: &[&str]) -> String {
        paths
            .iter()
            .flat_map(|path| {
                [
                    format!("diff --git a/{path} b/{path}"),
                    format!("--- a/{path}"),
                    format!("+++ b/{path}"),
                    "@@ -1 +1 @@".to_string(),
                    "-old".to_string(),
                    "+new".to_string(),
                ]
            })
            .collect::<Vec<_>>()
            .join("\n")
    }

    fn review(diff: &str, truncated: bool) -> Value {
        json!({
            "schema": REVIEW_SCHEMA,
            "repo": "C:/repo",
            "base": Value::Null,
            "status": "",
            "diff": diff,
            "digest": DIGEST,
            "truncated": truncated,
            "redacted": true
        })
    }

    fn reason(truncated: bool, protected: bool, plan: Option<&str>) -> String {
        auto_merge(DIGEST, truncated, protected, plan)["reason"]
            .as_str()
            .unwrap()
            .to_string()
    }

    fn temporary_repo(tag: &str) -> PathBuf {
        let sequence = NEXT_FIXTURE.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "simplicio-review-{tag}-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir_all(&path).unwrap();
        path
    }

    fn remove(path: &Path) {
        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn auto_merge_matrix_uses_a_fixed_precedence() {
        assert_eq!(reason(true, false, Some(DIGEST)), "truncated");
        assert_eq!(reason(true, true, Some(DIGEST)), "truncated");
        assert_eq!(reason(true, true, None), "truncated");
        assert_eq!(reason(false, true, Some(DIGEST)), "protected_path");
        assert_eq!(reason(false, true, None), "protected_path");
        assert_eq!(reason(false, false, None), "plan_digest_missing");
        assert_eq!(reason(false, false, Some("")), "plan_digest_missing");
        assert_eq!(
            reason(false, false, Some(OTHER_DIGEST)),
            "plan_digest_mismatch"
        );
        assert_eq!(
            reason(false, false, Some("not-a-digest")),
            "plan_digest_mismatch"
        );
        assert_eq!(reason(false, false, Some(DIGEST)), "eligible");
        assert_eq!(
            auto_merge(DIGEST, false, false, Some(&DIGEST.to_ascii_uppercase()))["eligible"],
            json!(true)
        );
    }

    #[test]
    fn protected_paths_cover_manifests_lockfiles_and_guardrail_directories() {
        for path in [
            "Cargo.toml",
            "Cargo.lock",
            "package-lock.json",
            "install.sh",
            "install.ps1",
            "simplicio-update-manifest.json",
            "SHA256SUMS",
            ".github/workflows/ci.yml",
            "schemas/review.json",
            "migrations/001.sql",
            "packages/app/package-lock.json",
        ] {
            assert!(is_protected_path(path), "{path} should be protected");
        }
        for path in [
            "src/Cargo.toml.md",
            "docs/install.sh.md",
            "src/SHA256SUMS.txt",
            "src/review.ts",
        ] {
            assert!(!is_protected_path(path), "{path} should not be protected");
        }
        let diff = diff_with(&["src/a.ts", ".github/workflows/ci.yml"]);
        assert_eq!(
            changed_paths(&diff),
            ["src/a.ts", ".github/workflows/ci.yml"]
        );
    }

    #[test]
    fn base_must_be_one_revision_not_an_option() {
        assert!(valid_base_revision("main"));
        assert!(valid_base_revision(" origin/main...HEAD "));
        assert!(!valid_base_revision(""));
        assert!(!valid_base_revision("--output=C:/escape"));
        assert!(!valid_base_revision("main\nrm"));
        assert!(!valid_base_revision(&"a".repeat(257)));
    }

    #[test]
    fn plan_digest_argument_overrides_the_repository_file() {
        let repo = temporary_repo("plan");
        assert_eq!(
            resolve_plan_digest(&repo, Some(" arg ")),
            Some("arg".into())
        );
        assert_eq!(resolve_plan_digest(&repo, None), None);
        fs::create_dir_all(repo.join(".simplicio")).unwrap();
        fs::write(
            repo.join(".simplicio/plan-digest"),
            format!("\n  {DIGEST}  \n"),
        )
        .unwrap();
        assert_eq!(resolve_plan_digest(&repo, None), Some(DIGEST.to_string()));
        assert_eq!(
            resolve_plan_digest(&repo, Some(" ")),
            Some(DIGEST.to_string())
        );
        remove(&repo);
    }

    #[test]
    fn comments_are_bounded_and_redacted() {
        assert_eq!(bounded_comments("  fix it  "), Ok("fix it"));
        assert_eq!(bounded_comments("   "), Err("review_comments_empty".into()));
        let too_long = "a".repeat(MAX_COMMENTS_CHARS + 1);
        assert_eq!(
            bounded_comments(&too_long),
            Err("review_comments_too_large".into())
        );
        assert_eq!(
            bounded_comments(&"a".repeat(MAX_COMMENTS_CHARS)).is_ok(),
            true
        );

        let redacted =
            redact_comments("token=supersecret\nghp_abcdefghijklmnop\nBearer abc.def\nnormal line");
        assert!(!redacted.contains("supersecret"));
        assert!(!redacted.contains("ghp_abcdefghijklmnop"));
        assert!(!redacted.contains("abc.def"));
        assert!(redacted.contains("token=[redacted]"));
        assert!(redacted.contains("normal line"));

        let key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEsecret\n-----END RSA PRIVATE KEY-----";
        let redacted = redact_comments(key);
        assert!(!redacted.contains("MIIEsecret"));
        assert!(redacted.contains("[redacted]"));
    }

    #[test]
    fn submission_is_idempotent_and_keeps_one_entry_per_digest() {
        let repo = temporary_repo("submit");
        let review = review(&diff_with(&["src/a.ts"]), false);
        let first = submit(&repo, &review, "fix this", Some(DIGEST), 1_000).unwrap();
        assert_eq!(first["schema"], RECEIPT_SCHEMA);
        assert_eq!(first["idempotent"], json!(false));
        assert_eq!(first["auto_merge"]["eligible"], json!(true));
        assert_eq!(
            first["path"],
            ".simplicio/review-inbox/sha256-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json"
        );

        let path = repo.join(first["path"].as_str().unwrap());
        let bytes = fs::read(&path).unwrap();
        let entry: Value = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(entry["schema"], SUBMISSION_SCHEMA);
        assert_eq!(entry["comments"], "fix this");
        assert_eq!(entry["redacted"], json!(true));

        let repeat = submit(&repo, &review, "fix this", Some(DIGEST), 2_000).unwrap();
        assert_eq!(repeat["receipt_id"], first["receipt_id"]);
        assert_eq!(repeat["idempotent"], json!(true));
        assert_eq!(fs::read(&path).unwrap(), bytes);

        let changed = submit(&repo, &review, "different", Some(DIGEST), 3_000).unwrap();
        assert_eq!(changed["idempotent"], json!(false));
        assert_ne!(changed["receipt_id"], first["receipt_id"]);
        assert_eq!(
            fs::read_dir(repo.join(".simplicio/review-inbox"))
                .unwrap()
                .count(),
            1
        );
        remove(&repo);
    }

    #[test]
    fn submission_refuses_a_file_in_place_of_review_state() {
        let repo = temporary_repo("state-file");
        fs::write(repo.join(".simplicio"), b"not a directory").unwrap();
        let result = submit(
            &repo,
            &review(&diff_with(&["src/a.ts"]), false),
            "comments",
            Some(DIGEST),
            1,
        );
        assert_eq!(result, Err("review_inbox_unavailable".into()));
        remove(&repo);
    }

    #[test]
    fn submission_persists_the_protected_and_missing_plan_reasons() {
        let repo = temporary_repo("reasons");
        let protected_review = review(&diff_with(&["install.sh"]), false);
        let receipt = submit(&repo, &protected_review, "guardrail", None, 1).unwrap();
        assert_eq!(receipt["auto_merge"]["reason"], "protected_path");
        assert_eq!(receipt["auto_merge"]["eligible"], json!(false));

        let clean_review = review(&diff_with(&["src/a.ts"]), false);
        let receipt = submit(&repo, &clean_review, "no plan", None, 1).unwrap();
        assert_eq!(receipt["auto_merge"]["reason"], "plan_digest_missing");
        remove(&repo);
    }

    #[test]
    fn submission_rejects_a_stale_digest_and_never_uses_it_as_a_path() {
        let review = review(&diff_with(&["src/a.ts"]), false);
        assert_eq!(
            validate_digest(&review, OTHER_DIGEST),
            Err("review_digest_mismatch".into())
        );
        assert_eq!(
            validate_digest(&review, "sha256:short"),
            Err("review_digest_invalid".into())
        );
        assert!(validate_digest(&review, DIGEST).is_ok());
        assert_eq!(
            entry_relative_path("../../escape"),
            Err("review_digest_invalid".into())
        );
        assert!(!valid_digest(&format!("{}a", "é".repeat(35))));
        let path = entry_relative_path(DIGEST).unwrap();
        assert!(path.starts_with(".simplicio/review-inbox/"));
        assert!(!path.contains(':'));
    }

    #[test]
    fn prepared_submission_redacts_comments_before_disk_and_receipt_reporting() {
        let repo = temporary_repo("redact");
        let receipt = submit(
            &repo,
            &review(&diff_with(&["src/a.ts"]), false),
            "token=abc123",
            Some(DIGEST),
            1,
        )
        .unwrap();
        let path = repo.join(receipt["path"].as_str().unwrap());
        let entry: Value = serde_json::from_slice(&fs::read(path).unwrap()).unwrap();
        assert!(!entry["comments"].as_str().unwrap().contains("abc123"));
        assert_eq!(entry["redacted"], json!(true));
        remove(&repo);
    }
}
