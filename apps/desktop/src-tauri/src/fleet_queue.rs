//! Fleet queue persistence: one versioned file per repo (or per user), with
//! validated tasks, per-track WIP admission and an atomic rename write.
//!
//! Orientation measurements are never synthesized here: `started_at` and
//! `orientation_ms` are only serialized when the caller provides a real value.

use chrono::{SecondsFormat, Utc};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

pub const SCHEMA: &str = "simplicio.fleet-queue/v1";
pub const STATUSES: [&str; 5] = ["queued", "running", "blocked", "needs_review", "done"];
pub const DEFAULT_WIP: u32 = 5;
const MAX_TASKS: usize = 512;
const MAX_BYTES: usize = 2 * 1024 * 1024;
const MAX_ORIENTATION_MS: u64 = 86_400_000;

static QUEUE_LOCK: Mutex<()> = Mutex::new(());
static NEXT_TEMP: AtomicU64 = AtomicU64::new(1);

/// Repo-selected queues live inside the repo; otherwise the user home is used.
pub fn state_path(repo_path: Option<&str>) -> Result<PathBuf, String> {
    if let Some(repo) = repo_path.map(str::trim).filter(|value| !value.is_empty()) {
        let repo = validate_repo(repo)?;
        return Ok(repo.join(".simplicio").join("fleet-queue.json"));
    }
    let home = std::env::var_os("HOME")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .map(PathBuf::from)
        .ok_or_else(|| "fleet_queue_home_unavailable".to_string())?;
    Ok(home.join(".simplicio").join("fleet-queue.json"))
}

fn validate_repo(repo_path: &str) -> Result<PathBuf, String> {
    let path = PathBuf::from(repo_path)
        .canonicalize()
        .map_err(|_| "repo_path_invalid".to_string())?;
    if !path.is_dir() {
        return Err("repo_path_invalid".to_string());
    }
    Ok(path)
}

pub fn read_at(path: &Path) -> Result<Value, String> {
    let _guard = QUEUE_LOCK
        .lock()
        .map_err(|_| "fleet_queue_unavailable".to_string())?;
    let (limits, tasks) = load(path)?;
    Ok(queue_value(&limits, &tasks))
}

/// Validate, enforce WIP per track and persist atomically. Rejected writes keep the old file.
pub fn upsert_at(
    path: &Path,
    task: &Value,
    wip_per_track: Option<&Value>,
) -> Result<Value, String> {
    let _guard = QUEUE_LOCK
        .lock()
        .map_err(|_| "fleet_queue_unavailable".to_string())?;
    let (mut limits, mut tasks) = load(path)?;
    merge_limits(&mut limits, wip_per_track)?;

    let candidate = normalize_task(task, true)?;
    let id = candidate["id"].as_str().unwrap_or_default().to_string();
    let track = candidate["track"].as_str().unwrap_or_default().to_string();
    let status = candidate["status"].as_str().unwrap_or_default().to_string();

    tasks.retain(|item| item["id"].as_str() != Some(id.as_str()));
    tasks.push(candidate);
    sort_tasks(&mut tasks);
    if tasks.len() > MAX_TASKS {
        return Err("task_limit_reached".to_string());
    }
    validate_hierarchy(&tasks)?;

    let limit = u64::from(*limits.get(&track).unwrap_or(&DEFAULT_WIP));
    let active = tasks
        .iter()
        .filter(|item| {
            item["track"].as_str() == Some(track.as_str())
                && item["id"].as_str() != Some(id.as_str())
                && item["status"].as_str() != Some("done")
        })
        .count() as u64;
    if status != "done" && active >= limit {
        return Err(format!("wip_limit_reached:{track}"));
    }

    let queue = queue_value(&limits, &tasks);
    write_atomic(path, &queue)?;
    Ok(queue)
}

fn load(path: &Path) -> Result<(BTreeMap<String, u32>, Vec<Value>), String> {
    if !path.exists() {
        return Ok((BTreeMap::new(), Vec::new()));
    }
    let metadata = fs::metadata(path).map_err(|_| "fleet_queue_unavailable".to_string())?;
    if metadata.len() > MAX_BYTES as u64 {
        return Err("fleet_queue_invalid".to_string());
    }
    let bytes = fs::read(path).map_err(|_| "fleet_queue_unavailable".to_string())?;
    let value: Value =
        serde_json::from_slice(&bytes).map_err(|_| "fleet_queue_invalid".to_string())?;
    let source = value
        .as_object()
        .ok_or_else(|| "fleet_queue_invalid".to_string())?;
    if source.get("schema").and_then(Value::as_str) != Some(SCHEMA) {
        return Err("fleet_queue_invalid".to_string());
    }
    let mut limits = BTreeMap::new();
    merge_limits(&mut limits, source.get("wip_per_track"))?;
    let raw = source
        .get("tasks")
        .and_then(Value::as_array)
        .ok_or_else(|| "fleet_queue_invalid".to_string())?;
    if raw.len() > MAX_TASKS {
        return Err("task_limit_reached".to_string());
    }
    let mut tasks = Vec::with_capacity(raw.len());
    for task in raw {
        tasks.push(normalize_task(task, false)?);
    }
    validate_hierarchy(&tasks)?;
    sort_tasks(&mut tasks);
    Ok((limits, tasks))
}

fn queue_value(limits: &BTreeMap<String, u32>, tasks: &[Value]) -> Value {
    json!({
        "schema": SCHEMA,
        "wip_per_track": limits,
        "tasks": tasks,
    })
}

fn normalize_task(value: &Value, stamp: bool) -> Result<Value, String> {
    let source = value
        .as_object()
        .ok_or_else(|| "task_invalid".to_string())?;
    let id = text(source, "id", "task_id_invalid")?;
    if !valid_slug(id) {
        return Err("task_id_invalid".to_string());
    }
    let issue = integer(source, "issue", "issue_invalid", 1, 10_000_000)?;
    let worktree = text(source, "worktree", "worktree_invalid").or_else(|_| {
        // An empty worktree means the queue entry exists before the worktree is created.
        match source.get("worktree").and_then(Value::as_str) {
            Some("") => Ok(""),
            _ => Err("worktree_invalid".to_string()),
        }
    })?;
    if worktree.chars().count() > 4096 || worktree.chars().any(char::is_control) {
        return Err("worktree_invalid".to_string());
    }
    let agent = text(source, "agent", "agent_invalid")?;
    if agent.len() > 64
        || !agent
            .chars()
            .all(|value| value.is_ascii_alphanumeric() || "-_. ".contains(value))
    {
        return Err("agent_invalid".to_string());
    }
    let track = text(source, "track", "track_invalid")?;
    if !valid_track(track) {
        return Err("track_invalid".to_string());
    }
    let wave = integer(source, "wave", "wave_invalid", 1, 9999)?;
    let status = text(source, "status", "status_invalid")?;
    if !STATUSES.contains(&status) {
        return Err("status_invalid".to_string());
    }
    let lane = match source.get("lane") {
        None | Some(Value::Null) => status,
        Some(Value::String(value)) if value.is_empty() => status,
        Some(Value::String(value)) => {
            if !STATUSES.contains(&value.as_str()) {
                return Err("status_invalid".to_string());
            }
            if value.as_str() != status {
                return Err("lane_status_mismatch".to_string());
            }
            value.as_str()
        }
        _ => return Err("status_invalid".to_string()),
    };
    let parent = match source.get("parent") {
        None | Some(Value::Null) => None,
        Some(Value::String(value)) if value.is_empty() => None,
        Some(Value::String(value)) => {
            if !valid_slug(value) {
                return Err("parent_invalid".to_string());
            }
            Some(value.clone())
        }
        _ => return Err("parent_invalid".to_string()),
    };
    let updated_at = match source.get("updated_at") {
        Some(Value::String(value)) if !value.is_empty() => {
            if !valid_timestamp(value) {
                return Err("updated_at_invalid".to_string());
            }
            value.clone()
        }
        None if stamp => Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true),
        _ => return Err("updated_at_invalid".to_string()),
    };
    let started_at = match source.get("started_at") {
        None | Some(Value::Null) => None,
        Some(Value::String(value)) if valid_timestamp(value) => Some(value.clone()),
        _ => return Err("started_at_invalid".to_string()),
    };
    let orientation = match source.get("orientation_ms") {
        None | Some(Value::Null) => None,
        Some(Value::Number(value)) => Some(
            value
                .as_u64()
                .filter(|value| *value <= MAX_ORIENTATION_MS)
                .ok_or_else(|| "orientation_invalid".to_string())?,
        ),
        _ => return Err("orientation_invalid".to_string()),
    };

    let mut task = json!({
        "id": id,
        "issue": issue,
        "worktree": worktree,
        "agent": agent,
        "track": track,
        "lane": lane,
        "wave": wave,
        "status": status,
        "parent": parent,
        "updated_at": updated_at,
    });
    let object = task
        .as_object_mut()
        .ok_or_else(|| "task_invalid".to_string())?;
    if let Some(started_at) = started_at {
        object.insert("started_at".to_string(), Value::String(started_at));
    }
    if let Some(orientation) = orientation {
        object.insert("orientation_ms".to_string(), json!(orientation));
    }
    Ok(task)
}

fn text<'a>(source: &'a Map<String, Value>, key: &str, code: &str) -> Result<&'a str, String> {
    source
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| code.to_string())
}

fn integer(
    source: &Map<String, Value>,
    key: &str,
    code: &str,
    minimum: u64,
    maximum: u64,
) -> Result<u64, String> {
    source
        .get(key)
        .and_then(Value::as_u64)
        .filter(|value| *value >= minimum && *value <= maximum)
        .ok_or_else(|| code.to_string())
}

fn valid_slug(value: &str) -> bool {
    value.len() <= 128
        && value
            .chars()
            .next()
            .is_some_and(|first| first.is_ascii_alphanumeric())
        && value
            .chars()
            .all(|item| item.is_ascii_alphanumeric() || "._:-".contains(item))
}

fn valid_track(value: &str) -> bool {
    value.len() <= 64
        && value
            .chars()
            .next()
            .is_some_and(|first| first.is_ascii_alphanumeric())
        && value
            .chars()
            .all(|item| item.is_ascii_alphanumeric() || "._-".contains(item))
}

fn valid_timestamp(value: &str) -> bool {
    !value.is_empty() && value.len() <= 40 && chrono::DateTime::parse_from_rfc3339(value).is_ok()
}

fn merge_limits(limits: &mut BTreeMap<String, u32>, value: Option<&Value>) -> Result<(), String> {
    let Some(value) = value else {
        return Ok(());
    };
    let source = value
        .as_object()
        .ok_or_else(|| "wip_limit_invalid".to_string())?;
    for (track, limit) in source {
        if !valid_track(track) {
            return Err("wip_limit_invalid".to_string());
        }
        let normalized = limit
            .as_u64()
            .filter(|value| (1..=64).contains(value))
            .ok_or_else(|| "wip_limit_invalid".to_string())?;
        limits.insert(track.clone(), normalized as u32);
    }
    Ok(())
}

fn validate_hierarchy(tasks: &[Value]) -> Result<(), String> {
    let mut by_id: BTreeMap<String, Option<String>> = BTreeMap::new();
    for task in tasks {
        let id = task["id"]
            .as_str()
            .ok_or_else(|| "task_invalid".to_string())?
            .to_string();
        if by_id.contains_key(&id) {
            return Err("task_duplicate".to_string());
        }
        let parent = task
            .get("parent")
            .and_then(Value::as_str)
            .filter(|value| !value.is_empty())
            .map(str::to_string);
        by_id.insert(id, parent);
    }
    for (id, parent) in &by_id {
        if let Some(parent) = parent {
            if parent == id {
                return Err("task_cycle".to_string());
            }
            if !by_id.contains_key(parent) {
                return Err(format!("parent_unknown:{parent}"));
            }
        }
    }
    for id in by_id.keys() {
        let mut seen = BTreeSet::new();
        seen.insert(id.clone());
        let mut cursor = by_id.get(id).cloned().flatten();
        while let Some(next) = cursor {
            if !seen.insert(next.clone()) {
                return Err("task_cycle".to_string());
            }
            cursor = by_id.get(&next).cloned().flatten();
        }
    }
    Ok(())
}

fn sort_tasks(tasks: &mut [Value]) {
    tasks.sort_by(|left, right| {
        let left_key = (
            left["wave"].as_u64().unwrap_or(0),
            left["track"].as_str().unwrap_or_default(),
            left["id"].as_str().unwrap_or_default(),
        );
        let right_key = (
            right["wave"].as_u64().unwrap_or(0),
            right["track"].as_str().unwrap_or_default(),
            right["id"].as_str().unwrap_or_default(),
        );
        left_key.cmp(&right_key)
    });
}

fn reject_symlink(path: &Path) -> Result<(), String> {
    match fs::symlink_metadata(path) {
        Ok(metadata) if metadata.file_type().is_symlink() => {
            Err("fleet_queue_unavailable".to_string())
        }
        Ok(_) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(_) => Err("fleet_queue_unavailable".to_string()),
    }
}

fn write_atomic(path: &Path, value: &Value) -> Result<(), String> {
    let parent = path
        .parent()
        .ok_or_else(|| "fleet_queue_unavailable".to_string())?;
    fs::create_dir_all(parent).map_err(|_| "fleet_queue_unavailable".to_string())?;
    reject_symlink(path)?;

    let file_name = path
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or("fleet-queue.json");
    let nonce = NEXT_TEMP.fetch_add(1, Ordering::Relaxed);
    let temporary = parent.join(format!(".{file_name}.tmp-{}-{nonce}", std::process::id()));
    let backup = parent.join(format!(".{file_name}.bak-{}-{nonce}", std::process::id()));
    reject_symlink(&temporary)?;
    reject_symlink(&backup)?;
    let _ = fs::remove_file(&temporary);

    let mut encoded =
        serde_json::to_vec_pretty(value).map_err(|_| "fleet_queue_unavailable".to_string())?;
    encoded.push(b'\n');
    if encoded.len() > MAX_BYTES {
        return Err("fleet_queue_invalid".to_string());
    }
    {
        let mut file = OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(&temporary)
            .map_err(|_| "fleet_queue_unavailable".to_string())?;
        file.write_all(&encoded)
            .and_then(|()| file.sync_all())
            .map_err(|_| "fleet_queue_unavailable".to_string())?;
    }

    if path.exists() {
        let _ = fs::remove_file(&backup);
        fs::rename(path, &backup).map_err(|_| "fleet_queue_unavailable".to_string())?;
    }
    if fs::rename(&temporary, path).is_err() {
        let _ = fs::remove_file(&temporary);
        if !path.exists() && backup.exists() {
            let _ = fs::rename(&backup, path);
        }
        return Err("fleet_queue_unavailable".to_string());
    }
    let _ = fs::remove_file(&backup);
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = fs::set_permissions(path, fs::Permissions::from_mode(0o600));
    }
    if let Ok(directory) = File::open(parent) {
        let _ = directory.sync_all();
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    static NEXT_FIXTURE: AtomicU64 = AtomicU64::new(1);

    fn temp_queue(label: &str) -> PathBuf {
        let root = std::env::temp_dir().join(format!(
            "simplicio-fleet-queue-{}-{}-{label}",
            std::process::id(),
            NEXT_FIXTURE.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(&root).unwrap();
        root.join("fleet-queue.json")
    }

    fn task(id: &str, track: &str, status: &str) -> Value {
        json!({
            "id": id,
            "issue": 433,
            "worktree": "C:/wt/issue-433",
            "agent": "claude",
            "track": track,
            "lane": status,
            "wave": 1,
            "status": status,
            "parent": null,
            "updated_at": "2026-10-23T12:00:00.000Z",
        })
    }

    #[test]
    fn defaults_to_an_empty_queue_and_rejects_malformed_state() {
        let path = temp_queue("default");
        let queue = read_at(&path).unwrap();
        assert_eq!(queue["schema"], SCHEMA);
        assert_eq!(queue["tasks"].as_array().unwrap().len(), 0);

        fs::write(&path, b"{}").unwrap();
        assert_eq!(read_at(&path).unwrap_err(), "fleet_queue_invalid");
    }

    #[test]
    fn rejects_invalid_status_and_lane_mismatch() {
        let path = temp_queue("status");
        assert_eq!(
            upsert_at(&path, &task("a", "desktop", "paused"), None).unwrap_err(),
            "status_invalid"
        );
        let mut mismatched = task("a", "desktop", "running");
        mismatched["lane"] = json!("queued");
        assert_eq!(
            upsert_at(&path, &mismatched, None).unwrap_err(),
            "lane_status_mismatch"
        );
        assert!(!path.exists());
    }

    #[test]
    fn enforces_wip_per_track_without_touching_the_file_on_rejection() {
        let path = temp_queue("wip");
        let limits = json!({ "desktop": 2 });
        upsert_at(&path, &task("a", "desktop", "running"), Some(&limits)).unwrap();
        upsert_at(&path, &task("b", "desktop", "running"), Some(&limits)).unwrap();
        let before = fs::read(&path).unwrap();

        assert_eq!(
            upsert_at(&path, &task("c", "desktop", "running"), Some(&limits)).unwrap_err(),
            "wip_limit_reached:desktop"
        );
        assert_eq!(fs::read(&path).unwrap(), before);

        // Queued work already consumes the track slot.
        assert_eq!(
            upsert_at(&path, &task("d", "desktop", "queued"), Some(&limits)).unwrap_err(),
            "wip_limit_reached:desktop"
        );

        upsert_at(&path, &task("a", "desktop", "done"), Some(&limits)).unwrap();
        upsert_at(&path, &task("f", "desktop", "running"), Some(&limits)).unwrap();
        let queue = read_at(&path).unwrap();
        assert_eq!(queue["wip_per_track"]["desktop"], 2);
    }

    #[test]
    fn upsert_is_atomic_idempotent_and_sorted() {
        let path = temp_queue("atomic");
        let first = json!({
            "id": "b", "issue": 433, "worktree": "C:/wt/b", "agent": "claude",
            "track": "desktop", "wave": 2, "status": "queued", "parent": null,
            "updated_at": "2026-10-23T12:00:00.000Z",
        });
        let second = json!({
            "id": "a", "issue": 433, "worktree": "C:/wt/a", "agent": "codex",
            "track": "desktop", "wave": 1, "status": "queued", "parent": null,
            "updated_at": "2026-10-23T12:00:00.000Z",
        });
        upsert_at(&path, &first, None).unwrap();
        upsert_at(&path, &second, None).unwrap();
        let bytes = fs::read(&path).unwrap();
        let stored = read_at(&path).unwrap();
        let ids: Vec<&str> = stored["tasks"]
            .as_array()
            .unwrap()
            .iter()
            .map(|task| task["id"].as_str().unwrap())
            .collect();
        assert_eq!(ids, ["a", "b"]);

        upsert_at(&path, &second, None).unwrap();
        assert_eq!(fs::read(&path).unwrap(), bytes);

        let entries: Vec<_> = fs::read_dir(path.parent().unwrap())
            .unwrap()
            .map(|entry| entry.unwrap().file_name())
            .collect();
        assert_eq!(entries, vec![std::ffi::OsString::from("fleet-queue.json")]);

        let other = temp_queue("atomic-reverse");
        upsert_at(&other, &second, None).unwrap();
        upsert_at(&other, &first, None).unwrap();
        assert_eq!(fs::read(&other).unwrap(), bytes);
    }

    #[test]
    fn keeps_parent_child_links_and_rejects_unknown_parents_and_cycles() {
        let path = temp_queue("hierarchy");
        upsert_at(&path, &task("parent", "desktop", "running"), None).unwrap();
        let mut child = task("child", "desktop", "queued");
        child["parent"] = json!("parent");
        upsert_at(&path, &child, None).unwrap();
        let stored = read_at(&path).unwrap();
        let stored_child = stored["tasks"]
            .as_array()
            .unwrap()
            .iter()
            .find(|task| task["id"] == "child")
            .unwrap();
        assert_eq!(stored_child["parent"], "parent");

        let mut missing = task("orphan", "desktop", "queued");
        missing["parent"] = json!("ghost");
        assert_eq!(
            upsert_at(&path, &missing, None).unwrap_err(),
            "parent_unknown:ghost"
        );

        let mut cycle = task("parent", "desktop", "running");
        cycle["parent"] = json!("child");
        assert_eq!(upsert_at(&path, &cycle, None).unwrap_err(), "task_cycle");
    }

    #[test]
    fn never_invents_orientation_measurements() {
        let path = temp_queue("orientation");
        upsert_at(&path, &task("a", "desktop", "queued"), None).unwrap();
        let stored = read_at(&path).unwrap();
        assert!(stored["tasks"][0].get("orientation_ms").is_none());
        assert!(stored["tasks"][0].get("started_at").is_none());

        let mut measured = task("b", "desktop", "running");
        measured["started_at"] = json!("2026-10-23T12:00:00.000Z");
        measured["orientation_ms"] = json!(1200);
        upsert_at(&path, &measured, None).unwrap();
        let stored = read_at(&path).unwrap();
        let item = stored["tasks"]
            .as_array()
            .unwrap()
            .iter()
            .find(|task| task["id"] == "b")
            .unwrap();
        assert_eq!(item["orientation_ms"], 1200);
        assert_eq!(item["started_at"], "2026-10-23T12:00:00.000Z");

        let mut invalid = task("c", "desktop", "running");
        invalid["orientation_ms"] = json!(-1);
        assert_eq!(
            upsert_at(&path, &invalid, None).unwrap_err(),
            "orientation_invalid"
        );
    }

    #[test]
    fn resolves_repo_or_home_state_paths() {
        let repo = temp_queue("repo-root");
        let root = repo.parent().unwrap().to_path_buf();
        let selected = state_path(root.to_str()).unwrap();
        assert_eq!(
            selected,
            root.canonicalize()
                .unwrap()
                .join(".simplicio")
                .join("fleet-queue.json")
        );
        let fallback = state_path(None).unwrap();
        assert!(fallback.ends_with(Path::new(".simplicio").join("fleet-queue.json")));
    }
}
