//! Commit and push from the Desktop review flow.
//!
//! The review screen already turns the working-tree diff into a deterministic
//! digest with guardrail flags (`review_submit`). This module adds the two
//! mutations that follow a review: create one commit with the message the human
//! typed, then optionally push it. Both are guarded by the same review state, so
//! a truncated diff, a protected path or an empty message can never reach git.
//!
//! The commit/push state machine is pure and unit-tested; the git calls are the
//! thin edge, and a failing hook or a rejected push surfaces the real stderr in
//! the returned document instead of a generic error.

use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

use crate::review_submit;

pub const COMMIT_SCHEMA: &str = "simplicio.desktop-review-commit/v1";
pub const PUSH_SCHEMA: &str = "simplicio.desktop-review-push/v1";
/// A commit message longer than this is refused instead of truncated.
pub const MAX_MESSAGE_CHARS: usize = 4_096;
/// Git stderr is bounded and redacted before it leaves the process.
pub const MAX_STDERR_CHARS: usize = 8_192;
const RECEIPT_DIR: &str = ".simplicio/review-commits";
const CREATE_REMOTE: &str = "origin";
const DEFAULT_BRANCHES: [&str; 2] = ["main", "master"];

const REVIEW_UNAVAILABLE: &str = "review_unavailable";
const DIGEST_INVALID: &str = "review_digest_invalid";

fn sha256_hex(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

/// `sha256:` followed by exactly 64 hexadecimal characters.
fn digest_hex(digest: &str) -> Result<String, String> {
    let value = digest.trim().to_ascii_lowercase();
    if !review_submit::valid_digest(&value) {
        return Err(DIGEST_INVALID.to_string());
    }
    Ok(value[7..].to_string())
}

/// The canonical `sha256:<64 hex>` form used in every document and path.
fn canonical_digest(digest: &str) -> Result<String, String> {
    Ok(format!("sha256:{}", digest_hex(digest)?))
}

/// Full object id, lowercase or uppercase, as printed by `git rev-parse`.
pub fn valid_sha(sha: &str) -> bool {
    let value = sha.trim();
    (value.len() == 40 || value.len() == 64) && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

/// The message is the human's, not a template: it is never rewritten, only
/// trimmed and bounded. Empty or oversized input is refused before git runs.
pub fn bounded_message(message: &str) -> Result<&str, String> {
    let trimmed = message.trim();
    if trimmed.is_empty() {
        return Err("review_message_empty".to_string());
    }
    if trimmed.chars().count() > MAX_MESSAGE_CHARS {
        return Err("review_message_too_large".to_string());
    }
    if trimmed.chars().any(|character| character == '\0') {
        return Err("review_message_invalid".to_string());
    }
    Ok(trimmed)
}

/// `main` and `master` are never committed to implicitly: the caller has to be
/// on an explicit worktree branch.
pub fn is_default_branch(branch: &str) -> bool {
    let name = branch.trim().trim_start_matches("refs/heads/");
    DEFAULT_BRANCHES.iter().any(|default| name.eq_ignore_ascii_case(default))
}

/// A changed path from the diff is used as a `git commit -- <path>` argument, so
/// it must stay repository-relative and never look like an option.
pub fn safe_relative_path(path: &str) -> bool {
    if path.is_empty() || path.len() > 1024 || path.chars().any(|c| c == '\0') {
        return false;
    }
    if path.starts_with('-') || path.starts_with('/') || path.starts_with('\\') {
        return false;
    }
    if path.len() > 1 && path.as_bytes()[1] == b':' {
        return false;
    }
    !path.split(['/', '\\']).any(|part| part == ".." || part == ".")
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommitPlan {
    pub digest: String,
    pub branch: String,
    pub paths: Vec<String>,
    pub message: String,
    pub message_digest: String,
}

fn review_string<'a>(review: &'a Value, key: &str) -> Result<&'a str, String> {
    review
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| REVIEW_UNAVAILABLE.to_string())
}

/// Everything that can be decided before touching git. Order is fixed so the
/// reported refusal is deterministic: truncation, base, changes, protected
/// paths, message, branch.
pub fn plan_commit(repo: &Path, review: &Value, message: &str) -> Result<CommitPlan, String> {
    if review.get("schema").and_then(Value::as_str) != Some(review_submit::REVIEW_SCHEMA) {
        return Err(REVIEW_UNAVAILABLE.to_string());
    }
    if review
        .get("truncated")
        .and_then(Value::as_bool)
        .ok_or_else(|| REVIEW_UNAVAILABLE.to_string())?
    {
        return Err("review_truncated".to_string());
    }
    // With a base, the diff also contains already-committed work, so "what was
    // reviewed" and "what gets committed" would differ.
    if review.get("base").is_some_and(|base| !base.is_null()) {
        return Err("review_commit_base_unsupported".to_string());
    }
    let digest = canonical_digest(review_string(review, "digest")?)?;
    let diff = review_string(review, "diff")?;
    let paths = review_submit::changed_paths(diff);
    if paths.is_empty() {
        return Err("review_changes_empty".to_string());
    }
    if paths.iter().any(|path| !safe_relative_path(path)) {
        return Err("review_path_invalid".to_string());
    }
    if paths
        .iter()
        .any(|path| review_submit::is_protected_path(path))
    {
        return Err("review_protected_path".to_string());
    }
    let message = bounded_message(message)?;
    let branch = current_branch(repo)?;
    if is_default_branch(&branch) {
        return Err("review_branch_protected".to_string());
    }
    in_progress_operation(repo)?;
    Ok(CommitPlan {
        digest,
        branch,
        paths,
        message: message.to_string(),
        message_digest: format!("sha256:{}", sha256_hex(message.as_bytes())),
    })
}

/// A merge, rebase, cherry-pick, revert or bisect in progress would make the
/// commit something other than the reviewed diff.
fn in_progress_operation(repo: &Path) -> Result<(), String> {
    let directory = git_stdout(repo, &["rev-parse", "--git-dir"])
        .map_err(|_| "git_unavailable".to_string())?;
    let directory = PathBuf::from(directory.trim());
    let directory = if directory.is_absolute() {
        directory
    } else {
        repo.join(directory)
    };
    for marker in [
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "BISECT_LOG",
    ] {
        if directory.join(marker).exists() {
            return Err("review_commit_in_progress".to_string());
        }
    }
    Ok(())
}

fn current_branch(repo: &Path) -> Result<String, String> {
    let branch = git_stdout(repo, &["rev-parse", "--abbrev-ref", "HEAD"])
        .map_err(|_| "review_branch_unavailable".to_string())?;
    let branch = branch.trim().to_string();
    if branch == "HEAD" {
        return Err("review_branch_detached".to_string());
    }
    Ok(branch)
}

/// The configured upstream, split into `(remote, remote_branch)`. A missing
/// upstream is data (`None`), not an error: push decides what to do with it.
pub fn upstream_of(repo: &Path) -> Option<(String, String)> {
    let value = git_stdout(
        repo,
        &["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
    )
    .ok()?;
    split_upstream(value.trim())
}

fn split_upstream(value: &str) -> Option<(String, String)> {
    let value = value.trim();
    let (remote, branch) = value.split_once('/')?;
    if remote.is_empty() || branch.is_empty() {
        return None;
    }
    Some((remote.to_string(), branch.to_string()))
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PushMode {
    /// The branch already tracks a remote branch with the same name.
    Existing { remote: String, branch: String },
    /// No upstream yet; the caller asked explicitly to create one.
    Create { remote: String, branch: String },
}

impl PushMode {
    /// `git push <remote> <branch>:<branch>` — never a `+`/force refspec, and
    /// never an omitted refspec that could push something else.
    pub fn refspec(&self) -> String {
        match self {
            PushMode::Existing { branch, .. } | PushMode::Create { branch, .. } => {
                format!("{branch}:{branch}")
            }
        }
    }

    pub fn remote(&self) -> &str {
        match self {
            PushMode::Existing { remote, .. } | PushMode::Create { remote, .. } => remote,
        }
    }

    pub fn creates_upstream(&self) -> bool {
        matches!(self, PushMode::Create { .. })
    }

    pub fn document(&self) -> Value {
        json!({
            "remote": self.remote(),
            "branch": match self {
                PushMode::Existing { branch, .. } | PushMode::Create { branch, .. } => branch,
            },
            "creates_upstream": self.creates_upstream(),
            "refspec": self.refspec(),
            "force": false,
        })
    }
}

/// Push is offered only for a branch with an upstream, or when the caller asks
/// explicitly to create one. There is no force path at all.
pub fn plan_push(
    branch: &str,
    upstream: Option<(&str, &str)>,
    create_upstream: bool,
) -> Result<PushMode, String> {
    if is_default_branch(branch) {
        return Err("review_branch_protected".to_string());
    }
    match upstream {
        Some((remote, remote_branch)) => {
            if remote.trim().is_empty() || remote_branch.trim().is_empty() {
                return Err("review_push_upstream_invalid".to_string());
            }
            if remote_branch != branch {
                // Pushing `branch` to a differently named remote branch is a
                // decision nobody made in the review screen.
                return Err("review_push_upstream_mismatch".to_string());
            }
            Ok(PushMode::Existing {
                remote: remote.to_string(),
                branch: branch.to_string(),
            })
        }
        None if create_upstream => Ok(PushMode::Create {
            remote: CREATE_REMOTE.to_string(),
            branch: branch.to_string(),
        }),
        None => Err("review_push_no_upstream".to_string()),
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Step {
    Commit,
    Push,
}

impl Step {
    fn name(self) -> &'static str {
        match self {
            Step::Commit => "commit",
            Step::Push => "push",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Phase {
    /// Guards passed; git has not run yet.
    Ready,
    /// One commit exists and its sha is recorded.
    Committed,
    /// The commit is on the remote.
    Pushed,
    /// The last attempted step failed; the phase names that step.
    Failed,
}

impl Phase {
    pub fn name(self) -> &'static str {
        match self {
            Phase::Ready => "ready",
            Phase::Committed => "committed",
            Phase::Pushed => "pushed",
            Phase::Failed => "failed",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GitFailure {
    pub step: Step,
    pub code: String,
    pub exit_code: Option<i32>,
    pub stderr: String,
}

/// The commit/push machine. A transition is only legal from the phase that can
/// produce it, so a push can never happen before a recorded commit and a
/// success can never be claimed after a failure.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommitPushState {
    phase: Phase,
    sha: Option<String>,
    upstream: Option<String>,
    failure: Option<GitFailure>,
}

impl CommitPushState {
    pub fn ready() -> Self {
        Self {
            phase: Phase::Ready,
            sha: None,
            upstream: None,
            failure: None,
        }
    }

    pub fn phase(&self) -> Phase {
        self.phase
    }

    pub fn sha(&self) -> Option<&str> {
        self.sha.as_deref()
    }

    pub fn upstream(&self) -> Option<&str> {
        self.upstream.as_deref()
    }

    pub fn failure(&self) -> Option<&GitFailure> {
        self.failure.as_ref()
    }

    fn illegal(&self, transition: &str) -> String {
        format!("review_git_transition_invalid:{transition}:{}", self.phase.name())
    }

    pub fn commit_succeeded(mut self, sha: &str) -> Result<Self, String> {
        if self.phase != Phase::Ready || !valid_sha(sha) {
            return Err(self.illegal("commit_succeeded"));
        }
        self.phase = Phase::Committed;
        self.sha = Some(sha.trim().to_ascii_lowercase());
        Ok(self)
    }

    pub fn commit_failed(mut self, failure: GitFailure) -> Result<Self, String> {
        if self.phase != Phase::Ready || failure.step != Step::Commit {
            return Err(self.illegal("commit_failed"));
        }
        self.phase = Phase::Failed;
        self.failure = Some(failure);
        Ok(self)
    }

    pub fn push_succeeded(mut self, upstream: &str) -> Result<Self, String> {
        if self.phase != Phase::Committed || upstream.trim().is_empty() {
            return Err(self.illegal("push_succeeded"));
        }
        self.phase = Phase::Pushed;
        self.upstream = Some(upstream.trim().to_string());
        Ok(self)
    }

    pub fn push_failed(mut self, failure: GitFailure) -> Result<Self, String> {
        if self.phase != Phase::Committed || failure.step != Step::Push {
            return Err(self.illegal("push_failed"));
        }
        self.phase = Phase::Failed;
        self.failure = Some(failure);
        Ok(self)
    }

    pub fn document(&self) -> Value {
        json!({
            "phase": self.phase.name(),
            "sha": self.sha,
            "upstream": self.upstream,
            "failed_step": self.failure.as_ref().map(|failure| failure.step.name()),
        })
    }
}

fn git(repo: &Path, args: &[String]) -> Result<Output, GitFailure> {
    Command::new("git")
        .arg("-C")
        .arg(repo)
        .args(args)
        .env("GIT_TERMINAL_PROMPT", "0")
        .stdin(Stdio::null())
        .output()
        .map_err(|_| GitFailure {
            step: Step::Commit,
            code: "git_unavailable".to_string(),
            exit_code: None,
            stderr: String::new(),
        })
}

fn git_stdout(repo: &Path, args: &[&str]) -> Result<String, String> {
    let args = args.iter().map(|arg| arg.to_string()).collect::<Vec<_>>();
    let output = git(repo, &args).map_err(|_| "git_unavailable".to_string())?;
    if !output.status.success() {
        return Err("git_unavailable".to_string());
    }
    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

/// Real git stderr, redacted and bounded. Never replaced by a generic sentence:
/// a failing hook or a rejected push has to be readable in the UI.
fn bounded_stderr(stderr: &[u8], stdout: &[u8]) -> String {
    let text = if String::from_utf8_lossy(stderr).trim().is_empty() {
        String::from_utf8_lossy(stdout).into_owned()
    } else {
        String::from_utf8_lossy(stderr).into_owned()
    };
    let redacted = review_submit::redact_comments(&text);
    redacted.chars().take(MAX_STDERR_CHARS).collect()
}

fn failure(step: Step, code: &str, output: &Output) -> GitFailure {
    GitFailure {
        step,
        code: code.to_string(),
        exit_code: output.status.code(),
        stderr: bounded_stderr(&output.stderr, &output.stdout),
    }
}

/// `git commit -m <message> -- <reviewed paths>`. Only the reviewed paths are
/// committed: untracked or unrelated staged work stays out of the commit.
fn run_commit(repo: &Path, plan: &CommitPlan) -> Result<String, GitFailure> {
    let mut args = vec![
        "commit".to_string(),
        "-m".to_string(),
        plan.message.clone(),
        "--".to_string(),
    ];
    args.extend(plan.paths.iter().cloned());
    let output = git(repo, &args).map_err(|mut failure| {
        failure.step = Step::Commit;
        failure
    })?;
    if !output.status.success() {
        return Err(failure(Step::Commit, "review_commit_failed", &output));
    }
    let sha = git_stdout(repo, &["rev-parse", "HEAD"])
        .map_err(|_| GitFailure {
            step: Step::Commit,
            code: "review_commit_sha_unavailable".to_string(),
            exit_code: None,
            stderr: String::new(),
        })?;
    let sha = sha.trim().to_ascii_lowercase();
    if !valid_sha(&sha) {
        return Err(GitFailure {
            step: Step::Commit,
            code: "review_commit_sha_unavailable".to_string(),
            exit_code: None,
            stderr: String::new(),
        });
    }
    Ok(sha)
}

fn run_push(repo: &Path, mode: &PushMode) -> Result<String, GitFailure> {
    // A refspec is built here, never accepted from a caller, and it can never
    // start with `+` (force) or be empty.
    let refspec = mode.refspec();
    if refspec.starts_with('+') || refspec.starts_with("--") || refspec.contains('\0') {
        return Err(GitFailure {
            step: Step::Push,
            code: "review_push_refspec_invalid".to_string(),
            exit_code: None,
            stderr: String::new(),
        });
    }
    let mut args = vec!["push".to_string()];
    if mode.creates_upstream() {
        args.push("--set-upstream".to_string());
    }
    args.push(mode.remote().to_string());
    args.push(refspec);
    let output = git(repo, &args).map_err(|mut failure| {
        failure.step = Step::Push;
        failure
    })?;
    if !output.status.success() {
        return Err(failure(Step::Push, "review_push_failed", &output));
    }
    let upstream = git_stdout(
        repo,
        &["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
    )
    .map_err(|_| GitFailure {
        step: Step::Push,
        code: "review_push_upstream_unavailable".to_string(),
        exit_code: None,
        stderr: String::new(),
    })?;
    let upstream = upstream.trim().to_string();
    if upstream.is_empty() {
        return Err(GitFailure {
            step: Step::Push,
            code: "review_push_upstream_unavailable".to_string(),
            exit_code: None,
            stderr: String::new(),
        });
    }
    Ok(upstream)
}

fn receipt_relative_path(digest: &str, sha: &str) -> Result<String, String> {
    let digest = digest_hex(digest)?;
    let sha = sha.trim().to_ascii_lowercase();
    if !valid_sha(&sha) {
        return Err("review_commit_sha_invalid".to_string());
    }
    Ok(format!("{RECEIPT_DIR}/{digest}--{sha}.json"))
}

fn commit_receipt(plan: &CommitPlan, sha: &str, now_epoch_ms: u64) -> Value {
    json!({
        "schema": COMMIT_SCHEMA,
        "status": "committed",
        "receipt_id": format!("commit-{}", &sha[..24.min(sha.len())]),
        "digest": plan.digest,
        "sha": sha,
        "branch": plan.branch,
        "paths": plan.paths,
        "message_chars": plan.message.chars().count(),
        "message_digest": plan.message_digest,
        "protected_paths": Vec::<String>::new(),
        "truncated": false,
        "upstream": Value::Null,
        "pushed": false,
        "pushed_at_epoch_ms": Value::Null,
        "redacted": true,
        "committed_at_epoch_ms": now_epoch_ms,
    })
}

fn write_receipt(
    repo: &Path,
    digest: &str,
    sha: &str,
    receipt: &Value,
) -> Result<String, String> {
    let relative = receipt_relative_path(digest, sha)?;
    review_submit::ensure_state_dir(repo, RECEIPT_DIR, "review_commit_state_unavailable")?;
    let path = repo.join(&relative);
    review_submit::reject_symlink(&path, "review_commit_state_unavailable")?;
    let bytes = serde_json::to_vec_pretty(receipt)
        .map_err(|_| "review_commit_receipt_invalid".to_string())?;
    let temporary = path.with_file_name(format!(
        ".{}.tmp-{}",
        path.file_name()
            .and_then(|value| value.to_str())
            .unwrap_or("commit"),
        std::process::id()
    ));
    fs::write(&temporary, &bytes)
        .map_err(|_| "review_commit_state_unavailable".to_string())?;
    if fs::rename(&temporary, &path).is_err() {
        let _ = fs::remove_file(&temporary);
        return Err("review_commit_state_unavailable".to_string());
    }
    Ok(relative)
}

fn read_receipt(repo: &Path, digest: &str, sha: &str) -> Result<Value, String> {
    let relative = receipt_relative_path(digest, sha)?;
    let path = repo.join(&relative);
    review_submit::reject_symlink(&path, "review_commit_state_unavailable")?;
    let bytes = fs::read(&path).map_err(|_| "review_commit_missing".to_string())?;
    let receipt: Value =
        serde_json::from_slice(&bytes).map_err(|_| "review_commit_receipt_invalid".to_string())?;
    let expected_digest = format!("sha256:{}", digest_hex(digest)?);
    if receipt.get("schema").and_then(Value::as_str) != Some(COMMIT_SCHEMA)
        || receipt.get("sha").and_then(Value::as_str) != Some(sha.trim().to_ascii_lowercase().as_str())
        || receipt.get("digest").and_then(Value::as_str) != Some(expected_digest.as_str())
        || receipt.get("redacted").and_then(Value::as_bool) != Some(true)
    {
        return Err("review_commit_receipt_invalid".to_string());
    }
    Ok(receipt)
}

/// Creates the reviewed commit and records a receipt with the real sha. A git
/// failure (hook, index, pathspec) returns a `commit_failed` document with the
/// real stderr instead of a bare error code.
pub fn commit(repo: &Path, review: &Value, message: &str, now_epoch_ms: u64) -> Result<Value, String> {
    let plan = plan_commit(repo, review, message)?;
    let state = CommitPushState::ready();
    match run_commit(repo, &plan) {
        Ok(sha) => {
            let state = state.commit_succeeded(&sha)?;
            let receipt = commit_receipt(&plan, &sha, now_epoch_ms);
            let path = write_receipt(repo, &plan.digest, &sha, &receipt)?;
            Ok(json!({
                "schema": COMMIT_SCHEMA,
                "status": "committed",
                "receipt_id": receipt.get("receipt_id").cloned().unwrap_or(Value::Null),
                "path": path,
                "digest": plan.digest,
                "sha": sha,
                "branch": plan.branch,
                "paths": plan.paths,
                "message_chars": receipt.get("message_chars").cloned().unwrap_or(Value::Null),
                "message_digest": plan.message_digest,
                "upstream": Value::Null,
                "pushed": false,
                "phase": state.phase().name(),
                "state": state.document(),
                "stderr": Value::Null,
                "redacted": true,
            }))
        }
        Err(failure) => {
            let state = state.commit_failed(failure.clone())?;
            Ok(json!({
                "schema": COMMIT_SCHEMA,
                "status": "commit_failed",
                "receipt_id": Value::Null,
                "path": Value::Null,
                "digest": plan.digest,
                "sha": Value::Null,
                "branch": plan.branch,
                "paths": plan.paths,
                "message_chars": plan.message.chars().count(),
                "message_digest": plan.message_digest,
                "upstream": Value::Null,
                "pushed": false,
                "phase": state.phase().name(),
                "state": state.document(),
                "code": failure.code,
                "exit_code": failure.exit_code,
                "stderr": failure.stderr,
                "redacted": true,
            }))
        }
    }
}

fn receipt_flag(receipt: &Value, key: &str) -> Result<bool, String> {
    receipt
        .get(key)
        .and_then(Value::as_bool)
        .ok_or_else(|| "review_commit_receipt_invalid".to_string())
}

fn receipt_string<'a>(receipt: &'a Value, key: &str) -> Result<&'a str, String> {
    receipt
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| "review_commit_receipt_invalid".to_string())
}

/// Pushes only a commit that this repository recorded from an approved review.
/// The receipt is the authorization: no protected path, no truncation.
pub fn push(
    repo: &Path,
    digest: &str,
    sha: &str,
    create_upstream: bool,
    now_epoch_ms: u64,
) -> Result<Value, String> {
    let sha = sha.trim().to_ascii_lowercase();
    if !valid_sha(&sha) {
        return Err("review_commit_sha_invalid".to_string());
    }
    let receipt = read_receipt(repo, digest, &sha)?;
    if receipt_flag(&receipt, "truncated")?
        || receipt
            .get("protected_paths")
            .and_then(Value::as_array)
            .is_none_or(|paths| !paths.is_empty())
    {
        return Err("review_protected_path".to_string());
    }
    let receipt_branch = receipt_string(&receipt, "branch")?.to_string();
    let branch = current_branch(repo)?;
    if branch != receipt_branch {
        return Err("review_commit_branch_changed".to_string());
    }
    let head = git_stdout(repo, &["rev-parse", "HEAD"])
        .map_err(|_| "git_unavailable".to_string())?;
    if head.trim().to_ascii_lowercase() != sha {
        return Err("review_commit_not_head".to_string());
    }
    let state = CommitPushState::ready().commit_succeeded(&sha)?;
    let recorded_upstream = receipt
        .get("upstream")
        .and_then(Value::as_str)
        .map(str::to_string);
    if receipt_flag(&receipt, "pushed")? {
        let upstream = recorded_upstream.unwrap_or_default();
        let state = state.push_succeeded(&upstream)?;
        return Ok(json!({
            "schema": PUSH_SCHEMA,
            "status": "pushed",
            "sha": sha,
            "branch": branch,
            "upstream": upstream,
            "mode": Value::Null,
            "idempotent": true,
            "phase": state.phase().name(),
            "state": state.document(),
            "code": Value::Null,
            "exit_code": Value::Null,
            "stderr": Value::Null,
            "redacted": true,
        }));
    }

    let existing = upstream_of(repo);
    let mode = plan_push(
        &branch,
        existing
            .as_ref()
            .map(|(remote, branch)| (remote.as_str(), branch.as_str())),
        create_upstream,
    )?;
    match run_push(repo, &mode) {
        Ok(upstream) => {
            let state = state.push_succeeded(&upstream)?;
            let mut updated = receipt.as_object().cloned().unwrap_or_else(Map::new);
            updated.insert("upstream".to_string(), Value::String(upstream.clone()));
            updated.insert("pushed".to_string(), json!(true));
            updated.insert("pushed_at_epoch_ms".to_string(), json!(now_epoch_ms));
            updated.insert("status".to_string(), json!("pushed"));
            let _ = write_receipt(repo, digest, &sha, &Value::Object(updated));
            Ok(json!({
                "schema": PUSH_SCHEMA,
                "status": "pushed",
                "sha": sha,
                "branch": branch,
                "upstream": upstream,
                "mode": mode.document(),
                "idempotent": false,
                "phase": state.phase().name(),
                "state": state.document(),
                "code": Value::Null,
                "exit_code": Value::Null,
                "stderr": Value::Null,
                "redacted": true,
            }))
        }
        Err(failure) => {
            let state = state.push_failed(failure.clone())?;
            Ok(json!({
                "schema": PUSH_SCHEMA,
                "status": "push_failed",
                "sha": sha,
                "branch": branch,
                "upstream": Value::Null,
                "mode": mode.document(),
                "idempotent": false,
                "phase": state.phase().name(),
                "state": state.document(),
                "code": failure.code,
                "exit_code": failure.exit_code,
                "stderr": failure.stderr,
                "redacted": true,
            }))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};

    const DIGEST: &str = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    const SHA: &str = "1111111111111111111111111111111111111111";
    const OTHER_SHA: &str = "2222222222222222222222222222222222222222";

    static NEXT_FIXTURE: AtomicU64 = AtomicU64::new(1);

    struct Fixture {
        root: PathBuf,
        repo: PathBuf,
        remote: PathBuf,
    }

    impl Fixture {
        fn git(&self, directory: &Path, args: &[&str]) -> String {
            let output = Command::new("git")
                .arg("-C")
                .arg(directory)
                .args(args)
                .env("GIT_TERMINAL_PROMPT", "0")
                .env("GIT_CONFIG_NOSYSTEM", "1")
                .output()
                .unwrap();
            assert!(
                output.status.success(),
                "git {args:?} failed: {}",
                String::from_utf8_lossy(&output.stderr)
            );
            String::from_utf8_lossy(&output.stdout).into_owned()
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    /// A scratch repository on `work`, with a bare `origin` remote that already
    /// has the initial commit.
    fn fixture(tag: &str) -> Fixture {
        let root = std::env::temp_dir().join(format!(
            "simplicio-review-git-{tag}-{}-{}",
            std::process::id(),
            NEXT_FIXTURE.fetch_add(1, Ordering::Relaxed)
        ));
        let repo = root.join("repo");
        let remote = root.join("remote.git");
        fs::create_dir_all(&repo).unwrap();
        let fixture = Fixture {
            root,
            repo: repo.clone(),
            remote: remote.clone(),
        };
        fixture.git(&repo, &["init", "-q"]);
        fixture.git(&repo, &["config", "user.email", "review@example.com"]);
        fixture.git(&repo, &["config", "user.name", "Review Flow"]);
        fixture.git(&repo, &["config", "commit.gpgsign", "false"]);
        fixture.git(&repo, &["checkout", "-q", "-b", "work"]);
        fs::write(repo.join("a.txt"), "one\n").unwrap();
        // `.simplicio` is repository state, not content: the real repository
        // ignores it and so does this fixture.
        fs::write(repo.join(".gitignore"), ".simplicio/\n").unwrap();
        fixture.git(&repo, &["add", "a.txt", ".gitignore"]);
        fixture.git(&repo, &["commit", "-q", "-m", "initial"]);
        fixture.git(&fixture.root, &["init", "-q", "--bare", "remote.git"]);
        fixture.git(&repo, &["remote", "add", "origin", remote.to_str().unwrap()]);
        fixture.git(&repo, &["push", "-q", "-u", "origin", "work"]);
        fixture
    }

    fn diff_for(paths: &[&str]) -> String {
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

    fn review(diff: &str, base: Value, truncated: bool) -> Value {
        json!({
            "schema": review_submit::REVIEW_SCHEMA,
            "repo": "/tmp/repo",
            "base": base,
            "status": " M src/a.txt",
            "diff": diff,
            "digest": DIGEST,
            "truncated": truncated,
            "redacted": true,
        })
    }

    fn write_change(fixture: &Fixture) {
        fs::write(fixture.repo.join("a.txt"), "one\ntwo\n").unwrap();
    }

    fn real_review(fixture: &Fixture) -> Value {
        // The same shape the native review command produces for this fixture.
        let diff = fixture.git(&fixture.repo, &["diff", "--no-ext-diff", "--unified=3", "HEAD"]);
        review(&diff, Value::Null, false)
    }

    #[test]
    fn state_machine_only_allows_commit_then_push() {
        let ready = CommitPushState::ready();
        assert_eq!(ready.phase(), Phase::Ready);

        let committed = ready
            .clone()
            .commit_succeeded(SHA)
            .expect("commit from ready");
        assert_eq!(committed.phase(), Phase::Committed);
        assert_eq!(committed.sha(), Some(SHA));

        let pushed = committed
            .clone()
            .push_succeeded("origin/work")
            .expect("push from committed");
        assert_eq!(pushed.phase(), Phase::Pushed);
        assert_eq!(pushed.upstream(), Some("origin/work"));

        // A push can never be claimed before a commit exists.
        assert!(ready.clone().push_succeeded("origin/work").is_err());
        assert!(ready.clone().push_failed(GitFailure {
            step: Step::Push,
            code: "review_push_failed".into(),
            exit_code: Some(1),
            stderr: "rejected".into(),
        }).is_err());
        // A second commit from the committed phase is illegal.
        assert!(committed.clone().commit_succeeded(OTHER_SHA).is_err());
        // Nor after a failure.
        let failed = ready
            .commit_failed(GitFailure {
                step: Step::Commit,
                code: "review_commit_failed".into(),
                exit_code: Some(1),
                stderr: "hook: lint failed".into(),
            })
            .unwrap();
        assert_eq!(failed.phase(), Phase::Failed);
        assert_eq!(failed.failure().unwrap().stderr, "hook: lint failed");
        assert!(failed.clone().push_succeeded("origin/work").is_err());
        assert!(failed.commit_succeeded(SHA).is_err());
        // A failure attributed to the wrong step is refused.
        assert!(CommitPushState::ready()
            .commit_failed(GitFailure {
                step: Step::Push,
                code: "review_push_failed".into(),
                exit_code: None,
                stderr: String::new(),
            })
            .is_err());
        // The upper-case sha is normalised, garbage is refused.
        assert_eq!(
            CommitPushState::ready()
                .commit_succeeded(&SHA.to_ascii_uppercase())
                .unwrap()
                .sha(),
            Some(SHA)
        );
        assert!(CommitPushState::ready().commit_succeeded("not-a-sha").is_err());
    }

    #[test]
    fn message_and_paths_are_bounded_before_git() {
        assert_eq!(bounded_message("  fix the guardrail  "), Ok("fix the guardrail"));
        assert_eq!(
            bounded_message("   \n "),
            Err("review_message_empty".to_string())
        );
        assert_eq!(
            bounded_message(&"a".repeat(MAX_MESSAGE_CHARS + 1)),
            Err("review_message_too_large".to_string())
        );
        assert!(bounded_message(&"a".repeat(MAX_MESSAGE_CHARS)).is_ok());
        assert!(bounded_message("multi\nline\nmessage").is_ok());
        assert_eq!(
            bounded_message("bad\0message"),
            Err("review_message_invalid".to_string())
        );

        for good in ["src/a.ts", "docs/x/y.md", "a-b/c d.ts", "install.sh.md"] {
            assert!(safe_relative_path(good), "{good} should be accepted");
        }
        for bad in [
            "",
            "-flag",
            "/abs/path",
            "\\abs\\path",
            "C:/escape",
            "../escape",
            "a/../../escape",
        ] {
            assert!(!safe_relative_path(bad), "{bad} should be refused");
        }
    }

    #[test]
    fn plan_commit_refuses_every_guardrail() {
        let fixture = fixture("guards");
        let clean = diff_for(&["a.txt"]);
        assert_eq!(
            plan_commit(&fixture.repo, &review(&clean, Value::Null, true), "msg"),
            Err("review_truncated".to_string())
        );
        assert_eq!(
            plan_commit(&fixture.repo, &review(&clean, json!("main"), false), "msg"),
            Err("review_commit_base_unsupported".to_string())
        );
        assert_eq!(
            plan_commit(&fixture.repo, &review("", Value::Null, false), "msg"),
            Err("review_changes_empty".to_string())
        );
        assert_eq!(
            plan_commit(&fixture.repo, &review(&diff_for(&["install.sh"]), Value::Null, false), "msg"),
            Err("review_protected_path".to_string())
        );
        assert_eq!(
            plan_commit(
                &fixture.repo,
                &review(&diff_for(&[".github/workflows/ci.yml"]), Value::Null, false),
                "msg"
            ),
            Err("review_protected_path".to_string())
        );
        assert_eq!(
            plan_commit(&fixture.repo, &review(&clean, Value::Null, false), "  "),
            Err("review_message_empty".to_string())
        );
        let plan = plan_commit(&fixture.repo, &review(&clean, Value::Null, false), "fix: thing").unwrap();
        assert_eq!(plan.branch, "work");
        assert_eq!(plan.paths, ["a.txt"]);
        assert_eq!(plan.digest, DIGEST);
        assert!(plan.message_digest.starts_with("sha256:"));
    }

    #[test]
    fn plan_commit_refuses_the_default_branches() {
        let fixture = fixture("branches");
        assert!(is_default_branch("main"));
        assert!(is_default_branch("refs/heads/master"));
        assert!(is_default_branch("MAIN"));
        assert!(!is_default_branch("feat/main-nav"));
        fixture.git(&fixture.repo, &["checkout", "-q", "-b", "main"]);
        write_change(&fixture);
        let review = real_review(&fixture);
        assert_eq!(
            plan_commit(&fixture.repo, &review, "msg"),
            Err("review_branch_protected".to_string())
        );
        assert_eq!(
            plan_push("main", None, true),
            Err("review_branch_protected".to_string())
        );
    }

    #[test]
    fn push_requires_an_upstream_or_an_explicit_creation() {
        assert_eq!(
            plan_push("work", None, false),
            Err("review_push_no_upstream".to_string())
        );
        assert_eq!(
            plan_push("work", None, true),
            Ok(PushMode::Create {
                remote: "origin".into(),
                branch: "work".into()
            })
        );
        let existing = plan_push("work", Some(("origin", "work")), false).unwrap();
        assert_eq!(existing.refspec(), "work:work");
        assert!(!existing.creates_upstream());
        assert_eq!(existing.remote(), "origin");
        // A differently named upstream is never pushed to implicitly.
        assert_eq!(
            plan_push("work", Some(("origin", "main")), false),
            Err("review_push_upstream_mismatch".to_string())
        );
        // There is no force mode at all.
        assert!(!existing.refspec().starts_with('+'));
        assert_eq!(
            plan_push("work", Some(("", "work")), false),
            Err("review_push_upstream_invalid".to_string())
        );
    }

    #[test]
    fn commit_writes_a_receipt_with_the_real_sha() {
        let fixture = fixture("commit");
        write_change(&fixture);
        let review = real_review(&fixture);
        let document = commit(&fixture.repo, &review, "feat: reviewed change", 1_000).unwrap();
        assert_eq!(document["schema"], COMMIT_SCHEMA);
        assert_eq!(document["status"], "committed");
        let sha = document["sha"].as_str().unwrap().to_string();
        assert!(valid_sha(&sha));
        assert_eq!(
            fixture
                .git(&fixture.repo, &["rev-parse", "HEAD"])
                .trim(),
            sha
        );
        assert_eq!(
            fixture
                .git(&fixture.repo, &["log", "-1", "--pretty=%s"])
                .trim(),
            "feat: reviewed change"
        );
        // Nothing else was swept into the commit.
        assert_eq!(
            fixture
                .git(&fixture.repo, &["status", "--porcelain"])
                .trim(),
            ""
        );
        let path = document["path"].as_str().unwrap();
        assert!(path.starts_with(".simplicio/review-commits/"));
        let stored: Value =
            serde_json::from_slice(&fs::read(fixture.repo.join(path)).unwrap()).unwrap();
        assert_eq!(stored["sha"], sha);
        assert_eq!(stored["digest"], DIGEST);
        assert_eq!(stored["pushed"], json!(false));
        assert_eq!(stored["redacted"], json!(true));
        assert!(!stored.to_string().contains("feat: reviewed change"));
    }

    #[test]
    fn a_second_commit_with_the_same_review_is_refused_by_git_not_claimed() {
        let fixture = fixture("twice");
        write_change(&fixture);
        let review = real_review(&fixture);
        let first = commit(&fixture.repo, &review, "first", 1).unwrap();
        assert_eq!(first["status"], "committed");
        let head = fixture.git(&fixture.repo, &["rev-parse", "HEAD"]);
        // The same stale review cannot produce a second commit: git says there
        // is nothing to commit and that real stderr is what the caller sees.
        let second = commit(&fixture.repo, &review, "second", 2).unwrap();
        assert_eq!(second["status"], "commit_failed");
        assert_eq!(second["sha"], Value::Null);
        assert!(second["receipt_id"].is_null());
        assert_eq!(fixture.git(&fixture.repo, &["rev-parse", "HEAD"]), head);
    }

    #[cfg(unix)]
    #[test]
    fn a_failing_hook_surfaces_the_real_stderr() {
        use std::os::unix::fs::PermissionsExt;
        let fixture = fixture("hook");
        write_change(&fixture);
        let hook = fixture.repo.join(".git/hooks/pre-commit");
        fs::write(&hook, "#!/bin/sh\necho 'pre-commit: lint failed on a.txt' >&2\nexit 1\n").unwrap();
        fs::set_permissions(&hook, fs::Permissions::from_mode(0o755)).unwrap();
        let review = real_review(&fixture);
        let head_before = fixture.git(&fixture.repo, &["rev-parse", "HEAD"]);
        let document = commit(&fixture.repo, &review, "should not land", 1).unwrap();
        assert_eq!(document["status"], "commit_failed");
        assert_eq!(document["phase"], "failed");
        assert_eq!(document["state"]["failed_step"], "commit");
        assert_eq!(document["sha"], Value::Null);
        assert_eq!(document["path"], Value::Null);
        let stderr = document["stderr"].as_str().unwrap();
        assert!(
            stderr.contains("pre-commit: lint failed on a.txt"),
            "real stderr missing: {stderr:?}"
        );
        // No commit and no receipt were created.
        assert_eq!(
            fixture.git(&fixture.repo, &["rev-parse", "HEAD"]),
            head_before
        );
        assert!(!fixture.repo.join(".simplicio/review-commits").exists());
    }

    #[test]
    fn push_creates_the_upstream_then_is_idempotent() {
        let fixture = fixture("push-create");
        write_change(&fixture);
        let review = real_review(&fixture);
        let committed = commit(&fixture.repo, &review, "feat: push me", 1).unwrap();
        let sha = committed["sha"].as_str().unwrap().to_string();
        assert_eq!(upstream_of(&fixture.repo), Some(("origin".into(), "work".into())));

        // Drop the upstream: `git branch --unset-upstream` keeps the remote ref.
        fixture.git(&fixture.repo, &["branch", "--unset-upstream"]);
        assert_eq!(upstream_of(&fixture.repo), None);
        assert_eq!(
            push(&fixture.repo, DIGEST, &sha, false, 2),
            Err("review_push_no_upstream".to_string())
        );

        let document = push(&fixture.repo, DIGEST, &sha, true, 3).unwrap();
        assert_eq!(document["schema"], PUSH_SCHEMA);
        assert_eq!(document["status"], "pushed");
        assert_eq!(document["upstream"], "origin/work");
        assert_eq!(document["mode"]["creates_upstream"], json!(true));
        assert_eq!(document["mode"]["force"], json!(false));
        assert_eq!(document["idempotent"], json!(false));
        assert_eq!(
            fixture
                .git(&fixture.remote, &["rev-parse", "refs/heads/work"])
                .trim(),
            sha
        );

        let repeat = push(&fixture.repo, DIGEST, &sha, false, 4).unwrap();
        assert_eq!(repeat["status"], "pushed");
        assert_eq!(repeat["idempotent"], json!(true));
        let stored: Value = serde_json::from_slice(
            &fs::read(fixture.repo.join(committed["path"].as_str().unwrap())).unwrap(),
        )
        .unwrap();
        assert_eq!(stored["pushed"], json!(true));
        assert_eq!(stored["upstream"], "origin/work");
    }

    #[test]
    fn push_refuses_a_commit_that_is_not_the_recorded_head() {
        let fixture = fixture("push-head");
        write_change(&fixture);
        let review = real_review(&fixture);
        let committed = commit(&fixture.repo, &review, "feat: head", 1).unwrap();
        let sha = committed["sha"].as_str().unwrap().to_string();
        // A later commit moves HEAD; the receipt no longer describes what would
        // be pushed.
        fs::write(fixture.repo.join("b.txt"), "later\n").unwrap();
        fixture.git(&fixture.repo, &["add", "b.txt"]);
        fixture.git(&fixture.repo, &["commit", "-q", "-m", "later"]);
        assert_eq!(
            push(&fixture.repo, DIGEST, &sha, false, 2),
            Err("review_commit_not_head".to_string())
        );
        // A sha with no receipt is never guessed.
        assert_eq!(
            push(&fixture.repo, DIGEST, OTHER_SHA, false, 3),
            Err("review_commit_missing".to_string())
        );
        assert_eq!(
            push(&fixture.repo, "sha256:short", &sha, false, 3),
            Err("review_digest_invalid".to_string())
        );
        assert_eq!(
            push(&fixture.repo, DIGEST, "not-a-sha", false, 3),
            Err("review_commit_sha_invalid".to_string())
        );
    }

    #[test]
    fn a_rejected_push_surfaces_the_real_stderr() {
        let fixture = fixture("push-reject");
        write_change(&fixture);
        let review = real_review(&fixture);
        let committed = commit(&fixture.repo, &review, "feat: rejected", 1).unwrap();
        let sha = committed["sha"].as_str().unwrap().to_string();

        // A second clone advances the remote, so this push is not a fast-forward.
        let other = fixture.root.join("other");
        fixture.git(
            &fixture.root,
            &["clone", "-q", "-b", "work", fixture.remote.to_str().unwrap(), "other"],
        );
        fixture.git(&other, &["config", "user.email", "other@example.com"]);
        fixture.git(&other, &["config", "user.name", "Other"]);
        fixture.git(&other, &["config", "commit.gpgsign", "false"]);
        fs::write(other.join("a.txt"), "remote wins\n").unwrap();
        fixture.git(&other, &["commit", "-q", "-am", "remote change"]);
        fixture.git(&other, &["push", "-q", "origin", "work"]);

        let document = push(&fixture.repo, DIGEST, &sha, false, 2).unwrap();
        assert_eq!(document["status"], "push_failed");
        assert_eq!(document["code"], "review_push_failed");
        assert_eq!(document["state"]["failed_step"], "push");
        let stderr = document["stderr"].as_str().unwrap();
        assert!(
            stderr.to_ascii_lowercase().contains("reject")
                || stderr.to_ascii_lowercase().contains("fast-forward")
                || stderr.to_ascii_lowercase().contains("non-fast-forward"),
            "real rejection stderr missing: {stderr:?}"
        );
        assert_ne!(document["stderr"], Value::Null);
        // The recorded receipt still says the commit is local-only.
        let stored: Value = serde_json::from_slice(
            &fs::read(fixture.repo.join(committed["path"].as_str().unwrap())).unwrap(),
        )
        .unwrap();
        assert_eq!(stored["pushed"], json!(false));
    }

    #[test]
    fn commit_and_push_against_a_scratch_repository_end_to_end() {
        let fixture = fixture("e2e");
        write_change(&fixture);
        let review = real_review(&fixture);
        let committed = commit(&fixture.repo, &review, "feat(desktop): reviewed change", 1_700_000_000_000).unwrap();
        let sha = committed["sha"].as_str().unwrap().to_string();
        let pushed = push(&fixture.repo, DIGEST, &sha, false, 1_700_000_001_000).unwrap();
        assert_eq!(pushed["status"], "pushed");
        assert_eq!(pushed["upstream"], "origin/work");
        assert_eq!(pushed["mode"]["force"], json!(false));
        // The bare remote really holds the commit the receipt recorded.
        assert_eq!(
            fixture.git(&fixture.remote, &["rev-parse", "refs/heads/work"]).trim(),
            sha
        );
        assert_eq!(
            fixture
                .git(&fixture.remote, &["log", "-1", "--pretty=%s", "refs/heads/work"])
                .trim(),
            "feat(desktop): reviewed change"
        );
        // The reviewer's tree is clean: only the reviewed path was committed.
        assert_eq!(fixture.git(&fixture.repo, &["status", "--porcelain"]).trim(), "");
        if std::env::var_os("SIMPLICIO_REVIEW_GIT_TRANSCRIPT").is_some() {
            eprintln!(
                "repo={}\nremote={}\ncommit_status={}\nsha={}\nreceipt={}\npush_status={}\nupstream={}\nremote_sha={}\nremote_log={}",
                fixture.repo.display(),
                fixture.remote.display(),
                committed["status"],
                sha,
                committed["path"].as_str().unwrap_or("-"),
                pushed["status"],
                pushed["upstream"],
                fixture.git(&fixture.remote, &["rev-parse", "refs/heads/work"]).trim(),
                fixture
                    .git(&fixture.remote, &["log", "-1", "--pretty=%H %s", "refs/heads/work"])
                    .trim()
            );
        }
    }

    #[test]
    fn a_commit_in_progress_blocks_the_mutation() {
        let fixture = fixture("progress");
        write_change(&fixture);
        let review = real_review(&fixture);
        fs::write(fixture.repo.join(".git/MERGE_HEAD"), "0".repeat(40)).unwrap();
        assert_eq!(
            plan_commit(&fixture.repo, &review, "msg"),
            Err("review_commit_in_progress".to_string())
        );
    }
}
