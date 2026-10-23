//! Validated, bounded bridge for the Runtime daemon event stream (#432).
//!
//! The page shape is the Runtime-owned `simplicio.desktop-events-page/v1`;
//! each envelope is `simplicio.desktop-events/v1`. This module never repairs,
//! reorders or invents an event: a page that does not validate is an error.
use serde_json::Value;

const PAGE_SCHEMA: &str = "simplicio.desktop-events-page/v1";
const EVENT_SCHEMA: &str = "simplicio.desktop-events/v1";
const MAX_SAFE_INTEGER: u64 = 9_007_199_254_740_991;
const MAX_PAGE_BYTES: usize = 1_000_000;
pub(crate) const MAX_EVENTS: usize = 500;
/// Largest page the daemon `events` method serves (its own `MAX_PAGE`).
const RUNTIME_PAGE_LIMIT: u64 = 256;
/// Long-poll ceiling for one Desktop poll; the UI expects a response in ~1 s.
pub(crate) const MAX_WAIT_MS: u64 = 1_000;
const EVENT_KINDS: &[&str] = &[
    "run.started",
    "run.progress",
    "run.finished",
    "plugin.installed",
    "plugin.updated",
    "plugin.removed",
    "host.connected",
    "host.disconnected",
    "map.baseline.building",
    "map.baseline.ready",
    "update.available",
    "update.applied",
];

fn safe_text<'a>(value: Option<&'a Value>, code: &str) -> Result<&'a str, String> {
    let text = value
        .and_then(Value::as_str)
        .filter(|text| !text.is_empty() && text.len() <= 512)
        .ok_or(code)?;
    if text
        .bytes()
        .any(|byte| byte == 0 || byte < 0x20 || byte == 0x7f)
    {
        return Err(code.into());
    }
    Ok(text)
}

fn safe_integer(value: Option<&Value>, code: &str) -> Result<u64, String> {
    value
        .and_then(Value::as_u64)
        .filter(|number| *number <= MAX_SAFE_INTEGER)
        .ok_or(code.into())
}

/// `simplicio daemon events --json --cursor N --limit 256 --wait-ms N`.
pub(crate) fn query_args(after_cursor: u64, wait_ms: u64) -> Result<Vec<String>, String> {
    if after_cursor > MAX_SAFE_INTEGER {
        return Err("activity_events_cursor_invalid".into());
    }
    Ok(vec![
        "daemon".into(),
        "events".into(),
        "--json".into(),
        "--cursor".into(),
        after_cursor.to_string(),
        "--limit".into(),
        RUNTIME_PAGE_LIMIT.to_string(),
        "--wait-ms".into(),
        wait_ms.min(MAX_WAIT_MS).to_string(),
    ])
}

fn validate_event(event: &Value) -> Result<(), String> {
    let object = event.as_object().ok_or("activity_events_invalid_event")?;
    if object.get("schema").and_then(Value::as_str) != Some(EVENT_SCHEMA) {
        return Err("activity_events_invalid_event".into());
    }
    let kind = safe_text(object.get("event"), "activity_events_invalid_event")?;
    if !EVENT_KINDS.contains(&kind) {
        return Err("activity_events_invalid_event".into());
    }
    safe_integer(object.get("cursor"), "activity_events_invalid_event")?;
    if !object.get("payload").is_some_and(Value::is_object) {
        return Err("activity_events_invalid_event".into());
    }
    Ok(())
}

/// Validate one daemon page and return it unchanged. Fail-closed: a malformed
/// event rejects the whole page rather than being silently dropped.
pub(crate) fn validate_page(value: Value) -> Result<Value, String> {
    let object = value.as_object().ok_or("activity_events_invalid")?;
    if object.get("schema").and_then(Value::as_str) != Some(PAGE_SCHEMA) {
        return Err("activity_events_invalid".into());
    }
    safe_text(object.get("stream_id"), "activity_events_invalid")?;
    let events = object
        .get("events")
        .and_then(Value::as_array)
        .ok_or("activity_events_invalid")?;
    if events.len() > MAX_EVENTS {
        return Err("activity_events_too_many".into());
    }
    safe_integer(object.get("next_cursor"), "activity_events_invalid")?;
    safe_integer(object.get("head_cursor"), "activity_events_invalid")?;
    safe_integer(object.get("retention_window"), "activity_events_invalid")?;
    if object.get("has_more").and_then(Value::as_bool).is_none() {
        return Err("activity_events_invalid".into());
    }
    for event in events {
        validate_event(event)?;
    }
    if serde_json::to_vec(&value)
        .map_err(|_| "activity_events_invalid")?
        .len()
        > MAX_PAGE_BYTES
    {
        return Err("activity_events_too_large".into());
    }
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn page() -> Value {
        json!({
            "schema": PAGE_SCHEMA,
            "stream_id": "stream-1",
            "events": [
                {
                    "schema": EVENT_SCHEMA,
                    "event": "run.started",
                    "cursor": 1,
                    "payload": {"run_id": "run-1", "issue": "432", "command": "map"}
                },
                {
                    "schema": EVENT_SCHEMA,
                    "event": "run.finished",
                    "cursor": 2,
                    "payload": {"run_id": "run-1", "status": "ok", "duration_ms": 12, "receipt_id": "r-1"}
                }
            ],
            "next_cursor": 2,
            "has_more": false,
            "head_cursor": 2,
            "retention_window": 4096
        })
    }

    #[test]
    fn builds_a_bounded_runtime_query() {
        assert_eq!(
            query_args(3, 5_000).unwrap(),
            [
                "daemon",
                "events",
                "--json",
                "--cursor",
                "3",
                "--limit",
                "256",
                "--wait-ms",
                "1000"
            ]
        );
        assert!(query_args(MAX_SAFE_INTEGER + 1, 0).is_err());
    }

    #[test]
    fn accepts_a_well_formed_page_unchanged() {
        let value = page();
        assert_eq!(validate_page(value.clone()).unwrap(), value);
    }

    #[test]
    fn rejects_unknown_kinds_and_missing_fields() {
        let mut unknown = page();
        unknown["events"][0]["event"] = json!("run.invented");
        assert_eq!(
            validate_page(unknown).unwrap_err(),
            "activity_events_invalid_event"
        );
        let mut bad_cursor = page();
        bad_cursor["events"][0]["cursor"] = json!(-1);
        assert!(validate_page(bad_cursor).is_err());
        let mut no_payload = page();
        no_payload["events"][0]
            .as_object_mut()
            .unwrap()
            .remove("payload");
        assert!(validate_page(no_payload).is_err());
        let mut bad_page = page();
        bad_page["schema"] = json!("simplicio.activity-export/v1");
        assert_eq!(
            validate_page(bad_page).unwrap_err(),
            "activity_events_invalid"
        );
    }

    #[test]
    fn rejects_more_than_the_desktop_bound() {
        let mut oversized = page();
        let events = (0..=MAX_EVENTS)
            .map(|index| {
                json!({
                    "schema": EVENT_SCHEMA,
                    "event": "run.progress",
                    "cursor": index,
                    "payload": {"run_id": "run-1", "message": "x"}
                })
            })
            .collect::<Vec<_>>();
        oversized["events"] = Value::Array(events);
        assert_eq!(
            validate_page(oversized).unwrap_err(),
            "activity_events_too_many"
        );
    }
}
