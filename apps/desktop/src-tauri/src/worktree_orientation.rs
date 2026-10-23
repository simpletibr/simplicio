//! Worktree orientation: consume the Runtime's shared default-branch baseline
//! (#6594) and measure the first orientation instead of guessing it.
//!
//! The Runtime owns the map. This module never remaps a repository: it asks
//! `simplicio map --repo <worktree> --json` for the checkout's map and reads
//! the receipt it returns. `cache_state` is the honest discriminator:
//!
//! - `hit` — the map was served from the stored baseline (plus the worktree's
//!   delta) and nothing was mapped again. That is a real orientation *from the
//!   baseline* and its measured duration becomes `orientation_ms`.
//! - `written` / `miss` — this call built the baseline. The build is reported
//!   as `baseline_missing`, because a first orientation that had to remap is
//!   not the criterion the issue asks for.
//! - `stale` — the Runtime served another generation; reported as `stale`.
//!
//! A number is never synthesized. When a measurement cannot be taken the
//! receipt carries `orientation_ms: null` and an explicit `error` code.

use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::time::Instant;

pub const SCHEMA: &str = "simplicio.desktop-worktree-orientation/v1";
pub const MAP_SCHEMA: &str = "simplicio.map-result/v1";
/// Shared baseline store inside `<git-common-dir>` (#6594).
pub const BASELINE_STORE: &str = "simplicio/map";
/// The 2 s acceptance budget of #433, used by the tests and the UI.
pub const ORIENTATION_BUDGET_MS: u64 = 2_000;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Orientation {
    /// `baseline` (clean checkout) or `baseline+delta` (worktree changes).
    pub generation: String,
    pub orientation_ms: u64,
    /// Build time stored with the baseline. On a `hit` this is the cost of the
    /// one build that produced the baseline, not the duration of this call, so
    /// it is reported under its own name and never as `orientation_ms`.
    pub baseline_build_ms: Option<u64>,
    pub mapped_files: Option<u64>,
    pub cache_state: String,
}

impl Orientation {
    pub fn to_json(&self) -> Value {
        json!({
            "schema": SCHEMA,
            "status": "measured",
            "generation": self.generation,
            "orientation_ms": self.orientation_ms,
            "baseline_build_ms": self.baseline_build_ms,
            "mapped_files": self.mapped_files,
            "cache_state": self.cache_state,
            "baseline_reused": true,
            "budget_ms": ORIENTATION_BUDGET_MS,
            "within_budget": self.orientation_ms < ORIENTATION_BUDGET_MS,
        })
    }
}

/// Explicit, number-free receipt for every path where no orientation was taken.
pub fn failure(code: &str) -> Value {
    let (status, hint) = match code {
        "orientation_baseline_missing" => (
            "baseline_missing",
            "Nenhum baseline do default branch está no store compartilhado; rode `simplicio map --repo <repo> --json` no default branch antes de abrir a tarefa.",
        ),
        "orientation_baseline_stale" => (
            "stale",
            "O Runtime serviu outra geração; rode `simplicio map --repo <repo> --json` e abra a tarefa novamente.",
        ),
        "orientation_timeout" => (
            "timeout",
            "A orientação passou do limite de tempo; o worktree continua válido e a tarefa pode ser aberta de novo.",
        ),
        "orientation_runtime_unavailable" | "orientation_unavailable" => (
            "unavailable",
            "O Runtime empacotado não está disponível; instale/o Runtime antes de medir a orientação.",
        ),
        "orientation_map_failed" => (
            "map_failed",
            "O Runtime não devolveu um mapa válido para este worktree; a orientação não foi medida.",
        ),
        _ => ("invalid", "A resposta de orientação do Runtime não pôde ser lida."),
    };
    json!({
        "schema": SCHEMA,
        "status": status,
        "error": code,
        "orientation_ms": null,
        "baseline_build_ms": null,
        "mapped_files": null,
        "cache_state": null,
        "baseline_reused": false,
        "budget_ms": ORIENTATION_BUDGET_MS,
        "within_budget": false,
        "hint": hint,
    })
}

/// The Runtime prints a progress line before the result, so parse the last
/// non-empty stdout line instead of requiring a single JSON document.
pub fn parse_runtime_json(stdout: &[u8]) -> Result<Value, String> {
    let text = std::str::from_utf8(stdout).map_err(|_| "orientation_invalid".to_string())?;
    let line = text
        .lines()
        .rev()
        .map(str::trim)
        .find(|line| line.starts_with('{'))
        .ok_or_else(|| "orientation_invalid".to_string())?;
    serde_json::from_str(line).map_err(|_| "orientation_invalid".to_string())
}

/// True when `<git-common-dir>/simplicio/map` already holds a stored baseline.
/// This is a read-only existence probe so a checkout without a baseline is
/// reported as missing *before* anything is mapped again.
pub fn baseline_store_ready(common_dir: &Path) -> bool {
    let store = common_dir.join(BASELINE_STORE);
    let Ok(entries) = std::fs::read_dir(store) else {
        return false;
    };
    entries.flatten().any(|entry| {
        let name = entry.file_name();
        let name = name.to_string_lossy();
        name.starts_with("baseline-") && name.ends_with(".json")
    })
}

/// Classify one `simplicio.map-result/v1` receipt. `orientation_ms` is the wall
/// time the caller measured around the invocation; it is never derived here.
pub fn classify(map: &Value, orientation_ms: u64) -> Result<Orientation, String> {
    if map.get("schema").and_then(Value::as_str) != Some(MAP_SCHEMA) {
        return Err("orientation_invalid".to_string());
    }
    match map.get("status").and_then(Value::as_str) {
        Some("native") => {}
        Some("blocked" | "failed") => return Err("orientation_map_failed".to_string()),
        _ => return Err("orientation_invalid".to_string()),
    }
    let receipt = map
        .get("native_mapper")
        .and_then(|value| value.get("receipt"))
        .filter(|value| value.is_object())
        .ok_or_else(|| "orientation_invalid".to_string())?;
    let cache_state = receipt
        .get("cache_state")
        .and_then(Value::as_str)
        .ok_or_else(|| "orientation_invalid".to_string())?;
    match cache_state {
        // Served from the stored baseline; no file was mapped again.
        "hit" => {}
        "written" | "miss" => return Err("orientation_baseline_missing".to_string()),
        "stale" => return Err("orientation_baseline_stale".to_string()),
        _ => return Err("orientation_invalid".to_string()),
    }
    let generation = receipt
        .get("source_generation")
        .and_then(|value| value.get("kind"))
        .and_then(Value::as_str)
        .ok_or_else(|| "orientation_invalid".to_string())?;
    if !matches!(generation, "baseline" | "baseline+delta") {
        return Err("orientation_invalid".to_string());
    }
    Ok(Orientation {
        generation: generation.to_string(),
        orientation_ms,
        baseline_build_ms: receipt.get("elapsed_ms").and_then(Value::as_u64),
        mapped_files: receipt.get("mapped_count").and_then(Value::as_u64),
        cache_state: cache_state.to_string(),
    })
}

/// Measure one orientation. `baseline_ready` is the cheap store probe: when it
/// is false the runtime is not invoked at all, so the Desktop never triggers a
/// remap and never reports a build as an orientation.
pub fn orient(
    repo: &Path,
    baseline_ready: bool,
    run: impl FnOnce(&Path) -> Result<Value, String>,
) -> Result<Orientation, String> {
    if !baseline_ready {
        return Err("orientation_baseline_missing".to_string());
    }
    let started = Instant::now();
    let map = run(repo)?;
    let elapsed_ms = started.elapsed().as_millis().try_into().unwrap_or(u64::MAX);
    classify(&map, elapsed_ms)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::fs;

    fn temp_dir(name: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "simplicio-worktree-orientation-{name}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&path).unwrap();
        path
    }

    fn receipt(cache_state: &str, kind: &str, elapsed_ms: u64) -> Value {
        json!({
            "schema": MAP_SCHEMA,
            "status": "native",
            "native_mapper": {
                "receipt": {
                    "schema": "simplicio.mapper-map-receipt/v1",
                    "cache_state": cache_state,
                    "elapsed_ms": elapsed_ms,
                    "mapped_count": 673,
                    "source_generation": {"kind": kind, "revision": "abc"}
                }
            }
        })
    }

    #[test]
    fn baseline_hit_is_measured_from_the_shared_store() {
        let found = classify(&receipt("hit", "baseline+delta", 380), 412).unwrap();
        assert_eq!(found.generation, "baseline+delta");
        assert_eq!(found.orientation_ms, 412);
        assert_eq!(found.baseline_build_ms, Some(380));
        assert_eq!(found.mapped_files, Some(673));
        let value = found.to_json();
        assert_eq!(value["status"], "measured");
        assert_eq!(value["orientation_ms"], 412);
        assert_eq!(value["baseline_reused"], true);
        assert_eq!(value["within_budget"], true);
    }

    #[test]
    fn a_built_baseline_is_never_reported_as_an_orientation() {
        for state in ["written", "miss"] {
            let error = classify(&receipt(state, "baseline", 31_000), 31_120).unwrap_err();
            assert_eq!(error, "orientation_baseline_missing", "state {state}");
        }
        let failure = failure("orientation_baseline_missing");
        assert_eq!(failure["status"], "baseline_missing");
        assert!(failure["orientation_ms"].is_null());
        assert_eq!(failure["baseline_reused"], false);
        assert_eq!(failure["within_budget"], false);
    }

    #[test]
    fn stale_and_malformed_receipts_are_explicit() {
        assert_eq!(
            classify(&receipt("stale", "baseline", 10), 11).unwrap_err(),
            "orientation_baseline_stale"
        );
        assert_eq!(
            classify(&json!({"schema": "other/v1"}), 1).unwrap_err(),
            "orientation_invalid"
        );
        assert_eq!(
            classify(&json!({"schema": MAP_SCHEMA, "status": "native"}), 1).unwrap_err(),
            "orientation_invalid"
        );
        assert_eq!(
            classify(&receipt("hit", "unknown", 1), 1).unwrap_err(),
            "orientation_invalid"
        );
        assert_eq!(
            classify(&json!({"schema": MAP_SCHEMA, "status": "blocked"}), 1).unwrap_err(),
            "orientation_map_failed"
        );
    }

    #[test]
    fn a_missing_baseline_skips_the_runtime_entirely() {
        let mut called = false;
        let result = orient(Path::new("/repo"), false, |_| {
            called = true;
            Ok(receipt("hit", "baseline", 1))
        });
        assert_eq!(result.unwrap_err(), "orientation_baseline_missing");
        assert!(
            !called,
            "a checkout without a baseline must not be remapped"
        );
    }

    #[test]
    fn orientation_ms_is_the_measured_wall_time_not_a_guess() {
        let found = orient(Path::new("/repo"), true, |_| {
            std::thread::sleep(std::time::Duration::from_millis(60));
            Ok(receipt("hit", "baseline", 5))
        })
        .unwrap();
        assert!(
            found.orientation_ms >= 50,
            "measured {} ms must include the work",
            found.orientation_ms
        );
        assert_eq!(found.baseline_build_ms, Some(5));
    }

    #[test]
    fn store_probe_only_accepts_a_stored_baseline() {
        let root = temp_dir("probe");
        assert!(!baseline_store_ready(&root));
        let store = root.join(BASELINE_STORE);
        fs::create_dir_all(&store).unwrap();
        fs::write(store.join("baseline-latest.ptr"), b"{}").unwrap();
        assert!(
            !baseline_store_ready(&root),
            "the pointer alone is not a baseline"
        );
        fs::write(store.join("baseline-deadbeef.json"), b"{}").unwrap();
        assert!(baseline_store_ready(&root));
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn runtime_output_with_a_progress_line_is_parsed_from_the_last_json_line() {
        let stdout = b"{\"schema\":\"simplicio.progress/v1\",\"event\":\"progress\"}\n{\"schema\":\"simplicio.map-result/v1\",\"status\":\"native\"}\n";
        let parsed = parse_runtime_json(stdout).unwrap();
        assert_eq!(parsed["schema"], MAP_SCHEMA);
        assert_eq!(
            parse_runtime_json(b"\n").unwrap_err(),
            "orientation_invalid"
        );
        assert_eq!(
            parse_runtime_json(b"not json").unwrap_err(),
            "orientation_invalid"
        );
    }

    /// Real integration measurement of #433: a repository whose default-branch
    /// baseline already exists, and two fresh worktrees of that commit. Both
    /// must be served from the baseline (`cache_state: hit`) and the wall time
    /// must be measured, not inferred.
    ///
    /// Ignored by default because it needs the Simplicio Runtime binary.
    /// Run: `SIMPLICIO_RUNTIME_BIN=$(command -v simplicio) cargo test --lib \
    ///   measured_worktree_orientation -- --ignored --nocapture`
    /// Set `SIMPLICIO_ORIENTATION_SOURCE_REPO` to measure a shared clone of a
    /// real repository instead of the synthetic fixture.
    #[test]
    #[ignore = "requires the Simplicio Runtime binary"]
    fn measured_worktree_orientation_reuses_the_baseline() {
        let binary = match std::env::var("SIMPLICIO_RUNTIME_BIN") {
            Ok(value) if !value.trim().is_empty() => PathBuf::from(value),
            _ => panic!("set SIMPLICIO_RUNTIME_BIN to the simplicio binary"),
        };
        let root = temp_dir("integration");
        let repo = root.join("repo");
        let git = |dir: &Path, args: &[&str]| {
            let status = std::process::Command::new("git")
                .arg("-C")
                .arg(dir)
                .args(args)
                .status()
                .unwrap();
            assert!(status.success(), "git {args:?} failed");
        };
        let source = std::env::var("SIMPLICIO_ORIENTATION_SOURCE_REPO")
            .ok()
            .map(|value| value.trim().to_string())
            .filter(|value| !value.is_empty());
        match source {
            Some(source) => {
                // A shared clone keeps the real content (and size) while the
                // baseline store stays inside the clone, so nothing is written
                // into the repository under measurement.
                let status = std::process::Command::new("git")
                    .args(["clone", "--shared", "--no-checkout", &source])
                    .arg(&repo)
                    .status()
                    .unwrap();
                assert!(status.success(), "clone of the source repository failed");
                git(&repo, &["checkout", "-q"]);
            }
            None => {
                fs::create_dir_all(&repo).unwrap();
                git(&repo, &["init", "-q"]);
                git(&repo, &["checkout", "-q", "-b", "main"]);
                for index in 0..40 {
                    fs::write(
                        repo.join(format!("src_{index}.rs")),
                        format!("pub fn f{index}() -> u8 {{ {index} }}\n"),
                    )
                    .unwrap();
                }
                git(&repo, &["add", "-A"]);
                git(
                    &repo,
                    &[
                        "-c",
                        "user.email=a@b",
                        "-c",
                        "user.name=a",
                        "commit",
                        "-qm",
                        "init",
                    ],
                );
            }
        }

        let run = |dir: &Path| -> Result<Value, String> {
            let output = std::process::Command::new(&binary)
                .args(["map", "--repo"])
                .arg(dir)
                .arg("--json")
                .output()
                .map_err(|_| "orientation_runtime_unavailable".to_string())?;
            if !output.status.success() {
                return Err("orientation_map_failed".to_string());
            }
            parse_runtime_json(&output.stdout)
        };

        // Prime the default-branch baseline once, outside the measurement:
        // the first call is the one that builds it, so it is not an
        // orientation from the baseline and must not be measured as one.
        let priming = run(&repo).expect("priming the baseline");
        let priming_state = priming["native_mapper"]["receipt"]["cache_state"]
            .as_str()
            .unwrap_or("unknown");
        eprintln!(
            "repo={} priming cache_state={priming_state}",
            repo.display()
        );

        let mut measured = Vec::new();
        for name in ["wt-a", "wt-b"] {
            let path = root.join(name);
            git(
                &repo,
                &[
                    "worktree",
                    "add",
                    "-q",
                    "--detach",
                    path.to_str().unwrap(),
                    "HEAD",
                ],
            );
            let common = repo.join(".git");
            let found = orient(&path, baseline_store_ready(&common), run)
                .unwrap_or_else(|error| panic!("{name} orientation failed: {error}"));
            eprintln!(
                "{name} orientation_ms={} baseline_build_ms={:?} generation={} cache_state={} mapped={:?}",
                found.orientation_ms,
                found.baseline_build_ms,
                found.generation,
                found.cache_state,
                found.mapped_files
            );
            assert_eq!(found.cache_state, "hit", "{name} must reuse the baseline");
            assert_eq!(found.generation, "baseline");
            measured.push(found.orientation_ms);
        }
        eprintln!(
            "measured orientation_ms first={} second={}",
            measured[0], measured[1]
        );
        assert!(
            measured[0] < ORIENTATION_BUDGET_MS,
            "first orientation {} ms exceeds the 2 s budget",
            measured[0]
        );
        assert!(
            measured[1] < ORIENTATION_BUDGET_MS,
            "second orientation {} ms exceeds the 2 s budget",
            measured[1]
        );
        fs::remove_dir_all(root).ok();
    }
}
