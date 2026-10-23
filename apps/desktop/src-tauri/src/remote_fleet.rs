//! Read-only projection of the remote runtime fleet.
//!
//! The allowlist lives in `~/.simplicio/desktop-remotes.json`
//! (`simplicio.desktop-remotes/v1`). It names an environment variable per
//! remote and never stores a token. Probing is a single bounded
//! `GET <url>/v1/health` per remote with a 3s timeout, no redirects and a
//! bounded body. Credentials, response bodies and free-form messages never
//! enter the projection returned to the WebView.
use serde_json::{json, Value};
use std::{
    collections::BTreeSet,
    env, fs,
    io::Read,
    net::IpAddr,
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

const CONFIG_PATH: &str = ".simplicio/desktop-remotes.json";
const CONFIG_SCHEMA: &str = "simplicio.desktop-remotes/v1";
const FLEET_SCHEMA: &str = "simplicio.desktop-remote-fleet/v1";
const MAX_CONFIG_BYTES: u64 = 65_536;
const MAX_BODY_BYTES: u64 = 65_536;
const MAX_REMOTES: usize = 32;
const MAX_LABEL_CHARS: usize = 80;
const MAX_URL_BYTES: usize = 2_048;
const MAX_VERSION_CHARS: usize = 64;
const MAX_LATENCY_MS: u64 = 60_000;
const MAX_WORKERS: usize = 32;
const MAX_WORKER_LABEL_CHARS: usize = 80;
const MAX_WORKER_CLAIM_CHARS: usize = 120;
const MAX_WORKER_PROGRESS: u64 = 1_000_000;
const WORKER_STATES: [&str; 5] = ["queued", "running", "paused", "blocked", "done"];
const TIMEOUT: Duration = Duration::from_secs(3);

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct Remote {
    pub(crate) id: String,
    pub(crate) label: String,
    pub(crate) base_url: String,
    pub(crate) token_env: Option<String>,
}

/// One worker the remote reported in its health body. Read-mostly: this module
/// only projects it, and no worker is derived from a neighbouring machine.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct Worker {
    pub(crate) id: String,
    pub(crate) label: String,
    pub(crate) claim: Option<String>,
    pub(crate) state: String,
    pub(crate) done: u64,
    pub(crate) total: Option<u64>,
    pub(crate) receipt_id: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct Observation {
    status: &'static str,
    authenticated: bool,
    version: Option<String>,
    latency_ms: Option<u64>,
    reason_code: Option<&'static str>,
    workers: Vec<Worker>,
}

impl Observation {
    fn offline(latency_ms: Option<u64>, reason_code: &'static str) -> Self {
        Self {
            status: "offline",
            authenticated: false,
            version: None,
            latency_ms,
            reason_code: Some(reason_code),
            workers: Vec::new(),
        }
    }

    fn unauthorized(reason_code: &'static str) -> Self {
        Self {
            status: "unauthorized",
            authenticated: false,
            version: None,
            latency_ms: None,
            reason_code: Some(reason_code),
            workers: Vec::new(),
        }
    }
}

fn valid_id(value: &str) -> bool {
    let mut chars = value.chars();
    let Some(first) = chars.next() else {
        return false;
    };
    value.len() <= 64
        && (first.is_ascii_lowercase() || first.is_ascii_digit())
        && chars.all(|character| {
            character.is_ascii_lowercase()
                || character.is_ascii_digit()
                || matches!(character, '.' | '_' | '-')
        })
}

fn valid_env_name(value: &str) -> bool {
    let mut chars = value.chars();
    let Some(first) = chars.next() else {
        return false;
    };
    value.len() <= 128
        && (first.is_ascii_uppercase() || first == '_')
        && chars.all(|character| {
            character.is_ascii_uppercase() || character.is_ascii_digit() || character == '_'
        })
}

/// A label or URL must not smuggle a credential into the config file.
fn looks_secret(value: &str) -> bool {
    const PREFIXES: [&str; 8] = [
        "ghp_", "gho_", "ghu_", "ghs_", "ghr_", "sk-", "xoxb-", "xoxp-",
    ];
    PREFIXES.iter().any(|prefix| {
        value.match_indices(prefix).any(|(index, _)| {
            value[index + prefix.len()..]
                .chars()
                .take_while(|character| {
                    character.is_ascii_alphanumeric() || matches!(character, '_' | '-')
                })
                .count()
                >= 16
        })
    })
}

fn normalize_url(value: &str) -> Result<(String, bool), &'static str> {
    if value.trim().is_empty() || value.len() > MAX_URL_BYTES {
        return Err("remote_config_url_invalid");
    }
    if looks_secret(value) {
        return Err("remote_secret_inline");
    }
    let url = reqwest::Url::parse(value.trim()).map_err(|_| "remote_config_url_invalid")?;
    if !matches!(url.scheme(), "http" | "https") {
        return Err("remote_config_url_insecure");
    }
    if !url.username().is_empty() || url.password().is_some() {
        return Err("remote_config_url_credentials");
    }
    if url.query().is_some() || url.fragment().is_some() || url.cannot_be_a_base() {
        return Err("remote_config_url_invalid");
    }
    let host = url.host_str().ok_or("remote_config_url_invalid")?;
    let loopback = host.eq_ignore_ascii_case("localhost")
        || host
            .parse::<IpAddr>()
            .is_ok_and(|address| address.is_loopback());
    Ok((url.as_str().trim_end_matches('/').to_string(), loopback))
}

fn parse_config(value: &Value) -> Result<Vec<Remote>, String> {
    let object = value.as_object().ok_or("remote_config_invalid")?;
    if object
        .keys()
        .any(|key| !matches!(key.as_str(), "schema" | "remotes"))
    {
        return Err("remote_config_unknown_field".into());
    }
    if object.get("schema").and_then(Value::as_str) != Some(CONFIG_SCHEMA) {
        return Err("remote_config_schema".into());
    }
    let entries = object
        .get("remotes")
        .and_then(Value::as_array)
        .ok_or("remote_config_invalid")?;
    if entries.len() > MAX_REMOTES {
        return Err("remote_config_limit".into());
    }
    let mut ids = BTreeSet::new();
    let mut remotes = Vec::with_capacity(entries.len());
    for entry in entries {
        let entry = entry.as_object().ok_or("remote_config_invalid")?;
        if entry
            .keys()
            .any(|key| !matches!(key.as_str(), "id" | "label" | "url" | "token_env"))
        {
            // A literal `token` field is refused rather than ignored.
            return Err("remote_config_unknown_field".into());
        }
        let id = entry
            .get("id")
            .and_then(Value::as_str)
            .filter(|value| valid_id(value))
            .ok_or("remote_config_id_invalid")?;
        if !ids.insert(id.to_string()) {
            return Err("remote_config_duplicate".into());
        }
        let label = entry
            .get("label")
            .and_then(Value::as_str)
            .map(str::trim)
            .unwrap_or("")
            .to_string();
        if label.is_empty()
            || label.chars().count() > MAX_LABEL_CHARS
            || label.chars().any(char::is_control)
            || looks_secret(&label)
        {
            return Err("remote_config_label_invalid".into());
        }
        let raw_url = entry
            .get("url")
            .and_then(Value::as_str)
            .ok_or("remote_config_url_invalid")?;
        if looks_secret(raw_url) {
            return Err("remote_secret_inline".into());
        }
        let (base_url, loopback) = normalize_url(raw_url)?;
        let token_env = match entry.get("token_env") {
            None | Some(Value::Null) => None,
            Some(candidate) => Some(
                candidate
                    .as_str()
                    .filter(|value| valid_env_name(value))
                    .ok_or("remote_config_token_env_invalid")?
                    .to_string(),
            ),
        };
        // Default deny: an address outside the loopback requires an explicit
        // token source. Loopback may stay tokenless but is never actionable.
        if !loopback && token_env.is_none() {
            return Err("remote_config_token_required".into());
        }
        remotes.push(Remote {
            id: id.to_string(),
            label,
            base_url,
            token_env,
        });
    }
    Ok(remotes)
}

fn read_bounded(mut reader: impl Read) -> Result<Vec<u8>, &'static str> {
    let mut bytes = Vec::new();
    reader
        .take(MAX_BODY_BYTES + 1)
        .read_to_end(&mut bytes)
        .map_err(|_| "read_failed")?;
    if bytes.len() as u64 > MAX_BODY_BYTES {
        return Err("response_too_large");
    }
    Ok(bytes)
}

/// Returns `Some(version)` for a healthy body and `None` for anything that
/// does not prove the health contract.
fn health_version(body: &[u8]) -> Option<Option<String>> {
    let value = serde_json::from_slice::<Value>(body).ok()?;
    let object = value.as_object()?;
    match object.get("status").and_then(Value::as_str) {
        Some("ok") | Some("healthy") => {}
        _ => return None,
    }
    match object.get("version") {
        None | Some(Value::Null) => Some(None),
        Some(candidate) => {
            let version = candidate.as_str()?.trim();
            if version.is_empty()
                || version.chars().count() > MAX_VERSION_CHARS
                || version.chars().any(char::is_control)
            {
                return None;
            }
            Some(Some(version.to_string()))
        }
    }
}

fn bounded_text(value: Option<&Value>, max: usize) -> Option<String> {
    let text = value?.as_str()?.trim();
    if text.is_empty() || text.chars().count() > max || text.chars().any(char::is_control) {
        return None;
    }
    Some(text.to_string())
}

fn valid_worker_id(value: &str) -> bool {
    let mut chars = value.chars();
    let Some(first) = chars.next() else {
        return false;
    };
    value.len() <= 64
        && first.is_ascii_alphanumeric()
        && chars.all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | ':' | '-')
        })
}

/// A Runtime receipt id is opaque but bounded; this module only forwards it.
pub(crate) fn valid_receipt_id(value: &str) -> bool {
    let mut chars = value.chars();
    let Some(first) = chars.next() else {
        return false;
    };
    value.len() <= 128
        && first.is_ascii_alphanumeric()
        && chars.all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | ':' | '-')
        })
}

fn parse_worker(value: &Value) -> Result<Worker, ()> {
    let object = value.as_object().ok_or(())?;
    if object.keys().any(|key| {
        !matches!(
            key.as_str(),
            "id" | "label" | "claim" | "state" | "progress" | "receipt_id" | "receiptId"
        )
    }) {
        return Err(());
    }
    let id = object
        .get("id")
        .and_then(Value::as_str)
        .filter(|value| valid_worker_id(value))
        .ok_or(())?
        .to_string();
    let label = bounded_text(object.get("label"), MAX_WORKER_LABEL_CHARS).ok_or(())?;
    let claim = match object.get("claim") {
        None | Some(Value::Null) => None,
        Some(_) => Some(bounded_text(object.get("claim"), MAX_WORKER_CLAIM_CHARS).ok_or(())?),
    };
    let state = object
        .get("state")
        .and_then(Value::as_str)
        .filter(|value| WORKER_STATES.contains(value))
        .ok_or(())?
        .to_string();
    let (done, total) = match object.get("progress") {
        None | Some(Value::Null) => (0, None),
        Some(progress) => {
            let progress = progress.as_object().ok_or(())?;
            if progress
                .keys()
                .any(|key| !matches!(key.as_str(), "done" | "total"))
            {
                return Err(());
            }
            let done = progress
                .get("done")
                .and_then(Value::as_u64)
                .filter(|done| *done <= MAX_WORKER_PROGRESS)
                .ok_or(())?;
            let total = match progress.get("total") {
                None | Some(Value::Null) => None,
                Some(candidate) => Some(
                    candidate
                        .as_u64()
                        .filter(|total| *total >= done && *total <= MAX_WORKER_PROGRESS)
                        .ok_or(())?,
                ),
            };
            (done, total)
        }
    };
    let receipt_id = match object.get("receipt_id").or_else(|| object.get("receiptId")) {
        None | Some(Value::Null) => None,
        Some(candidate) => Some(
            candidate
                .as_str()
                .filter(|value| valid_receipt_id(value))
                .ok_or(())?
                .to_string(),
        ),
    };
    Ok(Worker {
        id,
        label,
        claim,
        state,
        done,
        total,
        receipt_id,
    })
}

/// Strict parser for the optional bounded worker list in the health body. An
/// absent list means "the remote reported no workers", never "unknown".
fn health_workers(body: &[u8]) -> Result<Vec<Worker>, ()> {
    let value = serde_json::from_slice::<Value>(body).map_err(|_| ())?;
    let object = value.as_object().ok_or(())?;
    let workers = match object.get("workers") {
        None | Some(Value::Null) => return Ok(Vec::new()),
        Some(candidate) => candidate.as_array().ok_or(())?,
    };
    if workers.len() > MAX_WORKERS {
        return Err(());
    }
    let mut parsed = Vec::with_capacity(workers.len());
    let mut ids = BTreeSet::new();
    for worker in workers {
        let worker = parse_worker(worker)?;
        if !ids.insert(worker.id.clone()) {
            return Err(());
        }
        parsed.push(worker);
    }
    Ok(parsed)
}

fn probe(remote: &Remote, token: Option<&str>) -> Observation {
    let started = Instant::now();
    let client = match reqwest::blocking::Client::builder()
        .timeout(TIMEOUT)
        .redirect(reqwest::redirect::Policy::none())
        .build()
    {
        Ok(client) => client,
        Err(_) => return Observation::offline(None, "remote_client_unavailable"),
    };
    let mut request = client
        .get(format!("{}/v1/health", remote.base_url))
        .header("Accept", "application/json");
    if let Some(token) = token {
        request = request.bearer_auth(token);
    }
    let response = match request.send() {
        Ok(response) => response,
        Err(_) => return Observation::offline(None, "remote_unreachable"),
    };
    let latency_ms = Some(started.elapsed().as_millis().min(MAX_LATENCY_MS as u128) as u64);
    let status = response.status().as_u16();
    if matches!(status, 401 | 403) {
        let mut observation = Observation::unauthorized("remote_unauthorized");
        observation.latency_ms = latency_ms;
        return observation;
    }
    if !(200..300).contains(&status) {
        return Observation::offline(latency_ms, "remote_http_error");
    }
    let Some(body) = read_bounded(response).ok() else {
        return Observation::offline(latency_ms, "remote_health_invalid");
    };
    let Some(version) = health_version(&body) else {
        return Observation::offline(latency_ms, "remote_health_invalid");
    };
    // A malformed worker list fails the machine instead of publishing a partial
    // fleet: an unusable worker row must not reach the mobile layout.
    let Ok(workers) = health_workers(&body) else {
        return Observation::offline(latency_ms, "remote_workers_invalid");
    };
    Observation {
        status: "online",
        // A 2xx only proves an accepted token when this Desktop sent one.
        authenticated: token.is_some(),
        version,
        latency_ms,
        reason_code: None,
        workers,
    }
}

fn probe_entry(remote: &Remote) -> Value {
    let token = match remote.token_env.as_deref() {
        Some(name) => match env::var(name) {
            Ok(value)
                if !value.trim().is_empty()
                    && value.len() <= 4_096
                    && !value.chars().any(char::is_control) =>
            {
                Some(value)
            }
            // The named environment variable is absent or unusable. Fail closed
            // without a request instead of probing unauthenticated.
            _ => {
                let observation = Observation::unauthorized("remote_token_missing");
                return entry(remote, &observation);
            }
        },
        None => None,
    };
    entry(remote, &probe(remote, token.as_deref()))
}

fn entry(remote: &Remote, observation: &Observation) -> Value {
    json!({
        "id": remote.id,
        "label": remote.label,
        "url": remote.base_url,
        "status": observation.status,
        "authenticated": observation.authenticated,
        "version": observation.version,
        "latencyMs": observation.latency_ms,
        "reasonCode": observation.reason_code,
        "workers": observation.workers.iter().map(worker_json).collect::<Vec<_>>(),
    })
}

fn worker_json(worker: &Worker) -> Value {
    json!({
        "id": worker.id,
        "label": worker.label,
        "claim": worker.claim,
        "state": worker.state,
        "progress": { "done": worker.done, "total": worker.total },
        "receiptId": worker.receipt_id,
    })
}

fn empty(configured: bool, error: Option<&str>, observed_at: i64) -> Value {
    json!({
        "schema": FLEET_SCHEMA,
        "configured": configured,
        "redacted": true,
        "observedAt": observed_at,
        "error": error,
        "remotes": [],
    })
}

fn project(remotes: &[Remote], observed_at: i64) -> Value {
    let mut projected = vec![Value::Null; remotes.len()];
    // At most 32 scoped workers; each request keeps its own 3s deadline.
    std::thread::scope(|scope| {
        let handles = remotes
            .iter()
            .enumerate()
            .map(|(index, remote)| scope.spawn(move || (index, probe_entry(remote))))
            .collect::<Vec<_>>();
        for (index, handle) in handles.into_iter().enumerate() {
            match handle.join() {
                Ok((index, value)) => projected[index] = value,
                // A panicking worker must not leave an unparseable slot.
                Err(_) => {
                    projected[index] = entry(
                        &remotes[index],
                        &Observation::offline(None, "remote_probe_failed"),
                    )
                }
            }
        }
    });
    json!({
        "schema": FLEET_SCHEMA,
        "configured": true,
        "redacted": true,
        "observedAt": observed_at,
        "error": Value::Null,
        "remotes": projected,
    })
}

/// Reads the allowlist and probes every configured remote. A missing file is an
/// empty fleet, never a demo. An unreadable or invalid file is an empty fleet
/// plus a reason code, so the Desktop cannot invent machines.
pub fn read_at(home: &Path, observed_at: i64) -> Value {
    match load_config(home) {
        ConfigLoad::Missing => empty(false, None, observed_at),
        ConfigLoad::Invalid(code) => empty(true, Some(code.as_str()), observed_at),
        ConfigLoad::Remotes(remotes) => project(&remotes, observed_at),
    }
}

/// One allowlist load, shared by the read projection and the steer command so
/// both enforce the same file rules.
enum ConfigLoad {
    Missing,
    Invalid(String),
    Remotes(Vec<Remote>),
}

fn load_config(home: &Path) -> ConfigLoad {
    let path = home.join(CONFIG_PATH);
    let metadata = match fs::metadata(&path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return ConfigLoad::Missing,
        Err(_) => return ConfigLoad::Invalid("remote_config_unreadable".into()),
    };
    if !metadata.is_file() {
        return ConfigLoad::Invalid("remote_config_unreadable".into());
    }
    if metadata.len() > MAX_CONFIG_BYTES {
        return ConfigLoad::Invalid("remote_config_too_large".into());
    }
    let bytes = match fs::read(&path) {
        Ok(bytes) if bytes.len() as u64 <= MAX_CONFIG_BYTES => bytes,
        Ok(_) => return ConfigLoad::Invalid("remote_config_too_large".into()),
        Err(_) => return ConfigLoad::Invalid("remote_config_unreadable".into()),
    };
    let value = match serde_json::from_slice::<Value>(&bytes) {
        Ok(value) => value,
        Err(_) => return ConfigLoad::Invalid("remote_config_invalid".into()),
    };
    match parse_config(&value) {
        Ok(remotes) => ConfigLoad::Remotes(remotes),
        Err(code) => ConfigLoad::Invalid(code),
    }
}

/// Resolves one allowlisted machine for a steer action. An absent, unreadable
/// or invalid allowlist never becomes a machine: it is the same error the read
/// projection reports, so the UI states the real reason.
pub(crate) fn find_remote(home: &Path, id: &str) -> Result<Remote, String> {
    if !valid_id(id) {
        return Err("fleet_steer_machine_unknown".into());
    }
    match load_config(home) {
        ConfigLoad::Remotes(remotes) => remotes
            .into_iter()
            .find(|remote| remote.id == id)
            .ok_or_else(|| "fleet_steer_machine_unknown".to_string()),
        ConfigLoad::Missing => Err("fleet_steer_machine_unknown".into()),
        ConfigLoad::Invalid(code) => Err(code),
    }
}

/// Windows resolves `%USERPROFILE%`; other platforms use `$HOME`.
pub(crate) fn default_home() -> Option<PathBuf> {
    #[cfg(windows)]
    {
        std::env::var_os("USERPROFILE")
            .or_else(|| std::env::var_os("HOME"))
            .map(PathBuf::from)
    }
    #[cfg(not(windows))]
    {
        std::env::var_os("HOME").map(PathBuf::from)
    }
}

pub fn read() -> Result<Value, String> {
    let home = default_home().ok_or("remote_fleet_home_unavailable")?;
    Ok(read_at(&home, chrono::Utc::now().timestamp()))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn remote(url: &str, token_env: Option<&str>) -> Value {
        json!({
            "id": "mac-mini",
            "label": "Mac mini",
            "url": url,
            "token_env": token_env,
        })
    }

    fn config(remotes: Vec<Value>) -> Value {
        json!({"schema": CONFIG_SCHEMA, "remotes": remotes})
    }

    #[test]
    fn accepts_loopback_without_a_token_and_remote_with_token_env() {
        let parsed = parse_config(&config(vec![
            remote("http://127.0.0.1:8787", None),
            json!({
                "id": "studio",
                "label": "Studio",
                "url": "https://studio.example.test",
                "token_env": "SIMPLICIO_REMOTE_STUDIO_TOKEN"
            }),
        ]))
        .unwrap();
        assert_eq!(
            parsed,
            vec![
                Remote {
                    id: "mac-mini".into(),
                    label: "Mac mini".into(),
                    base_url: "http://127.0.0.1:8787".into(),
                    token_env: None,
                },
                Remote {
                    id: "studio".into(),
                    label: "Studio".into(),
                    base_url: "https://studio.example.test".into(),
                    token_env: Some("SIMPLICIO_REMOTE_STUDIO_TOKEN".into()),
                },
            ]
        );
    }

    #[test]
    fn denies_non_loopback_without_an_explicit_token() {
        let error =
            parse_config(&config(vec![remote("https://studio.example.test", None)])).unwrap_err();
        assert_eq!(error, "remote_config_token_required");
    }

    #[test]
    fn denies_embedded_credentials_and_literal_tokens() {
        assert_eq!(
            parse_config(&config(vec![remote(
                "https://user:pass@studio.test",
                Some("TOKEN")
            )]))
            .unwrap_err(),
            "remote_config_url_credentials"
        );
        assert_eq!(
            normalize_url("ftp://127.0.0.1").unwrap_err(),
            "remote_config_url_insecure"
        );
        let literal = json!({
            "id": "studio",
            "label": "Studio",
            "url": "https://studio.example.test",
            "token": "ghp_0123456789abcdefghijklmnop"
        });
        assert_eq!(
            parse_config(&config(vec![literal])).unwrap_err(),
            "remote_config_unknown_field"
        );
        let inline = json!({
            "id": "studio",
            "label": "Studio",
            "url": "https://studio.example.test",
            "token_env": "ghp_0123456789abcdefghijklmnop"
        });
        assert_eq!(
            parse_config(&config(vec![inline])).unwrap_err(),
            "remote_config_token_env_invalid"
        );
    }

    #[test]
    fn bounds_the_fleet_and_rejects_duplicates() {
        let entries = (0..33)
            .map(|index| {
                json!({
                    "id": format!("remote-{index}"),
                    "label": "Remote",
                    "url": "http://127.0.0.1:8787"
                })
            })
            .collect::<Vec<_>>();
        assert_eq!(
            parse_config(&config(entries)).unwrap_err(),
            "remote_config_limit"
        );
        assert_eq!(
            parse_config(&config(vec![
                remote("http://127.0.0.1:8787", None),
                remote("http://127.0.0.1:8788", None)
            ]))
            .unwrap_err(),
            "remote_config_duplicate"
        );
    }

    #[test]
    fn maps_health_status_without_trusting_the_body() {
        assert_eq!(
            health_version(br#"{"status":"ok","version":"3.10.0"}"#),
            Some(Some("3.10.0".into()))
        );
        assert_eq!(health_version(br#"{"status":"healthy"}"#), Some(None));
        assert_eq!(health_version(br#"{"status":"degraded"}"#), None);
        assert_eq!(health_version(br#"{"status":"ok","version":42}"#), None);
        assert_eq!(health_version(b"not-json"), None);
    }

    #[test]
    fn maps_the_optional_worker_list_and_defaults_to_none() {
        assert_eq!(health_workers(br#"{"status":"ok"}"#), Ok(Vec::new()));
        assert_eq!(health_workers(br#"{"workers":null}"#), Ok(Vec::new()));
        let body = json!({
            "status": "ok",
            "workers": [
                {
                    "id": "w-1",
                    "label": "issue-468",
                    "claim": "issue:468",
                    "state": "running",
                    "progress": {"done": 3, "total": 7},
                    "receipt_id": "rcpt-abc"
                },
                {"id": "w-2", "label": "review", "state": "paused"}
            ]
        });
        let parsed = health_workers(body.to_string().as_bytes()).unwrap();
        assert_eq!(parsed.len(), 2);
        assert_eq!(parsed[0].state, "running");
        assert_eq!(parsed[0].claim.as_deref(), Some("issue:468"));
        assert_eq!((parsed[0].done, parsed[0].total), (3, Some(7)));
        assert_eq!(parsed[0].receipt_id.as_deref(), Some("rcpt-abc"));
        assert_eq!(parsed[1].claim, None);
        assert_eq!((parsed[1].done, parsed[1].total), (0, None));
    }

    #[test]
    fn refuses_worker_rows_that_break_the_contract() {
        let invalid = [
            // duplicate id
            json!({"workers": [{"id": "w-1", "label": "a", "state": "running"}, {"id": "w-1", "label": "b", "state": "done"}]}),
            // unknown state
            json!({"workers": [{"id": "w-1", "label": "a", "state": "paused-by-user"}]}),
            // progress total below done
            json!({"workers": [{"id": "w-1", "label": "a", "state": "running", "progress": {"done": 5, "total": 2}}]}),
            // unknown field
            json!({"workers": [{"id": "w-1", "label": "a", "state": "running", "token": "x"}]}),
            // path traversal in the id
            json!({"workers": [{"id": "../w", "label": "a", "state": "running"}]}),
            // receipt that could not be forwarded
            json!({"workers": [{"id": "w-1", "label": "a", "state": "running", "receipt_id": "rcpt with space"}]}),
        ];
        for body in invalid {
            assert!(
                health_workers(body.to_string().as_bytes()).is_err(),
                "{body} must be refused"
            );
        }
        let too_many = json!({
            "workers": (0..=MAX_WORKERS)
                .map(|index| json!({"id": format!("w-{index}"), "label": "x", "state": "queued"}))
                .collect::<Vec<_>>()
        });
        assert!(health_workers(too_many.to_string().as_bytes()).is_err());
    }

    #[test]
    fn projects_workers_next_to_the_machine() {
        let remote = Remote {
            id: "mac-mini".into(),
            label: "Mac mini".into(),
            base_url: "http://127.0.0.1:8787".into(),
            token_env: None,
        };
        let observation = Observation {
            status: "online",
            authenticated: false,
            version: Some("3.10.0".into()),
            latency_ms: Some(9),
            reason_code: None,
            workers: vec![Worker {
                id: "w-1".into(),
                label: "issue-468".into(),
                claim: Some("issue:468".into()),
                state: "running".into(),
                done: 1,
                total: Some(4),
                receipt_id: None,
            }],
        };
        let value = entry(&remote, &observation);
        assert_eq!(value["workers"][0]["id"], "w-1");
        assert_eq!(value["workers"][0]["claim"], "issue:468");
        assert_eq!(value["workers"][0]["progress"]["done"], 1);
        assert_eq!(value["workers"][0]["progress"]["total"], 4);
        assert_eq!(value["workers"][0]["receiptId"], Value::Null);
    }

    #[test]
    fn resolves_an_allowlisted_machine_for_steer() {
        let home = std::env::temp_dir().join(format!("simplicio-fleet-{}", std::process::id()));
        let _ = fs::create_dir_all(home.join(".simplicio"));
        let path = home.join(CONFIG_PATH);
        fs::write(
            &path,
            config(vec![
                json!({"id": "mac-mini", "label": "Mac mini", "url": "http://127.0.0.1:8787"}),
            ])
            .to_string(),
        )
        .unwrap();
        assert_eq!(
            find_remote(&home, "mac-mini").unwrap().base_url,
            "http://127.0.0.1:8787"
        );
        assert_eq!(
            find_remote(&home, "studio").unwrap_err(),
            "fleet_steer_machine_unknown"
        );
        // A path-shaped id never reaches the filesystem.
        assert_eq!(
            find_remote(&home, "../etc").unwrap_err(),
            "fleet_steer_machine_unknown"
        );
        let _ = fs::remove_file(&path);
        let _ = fs::remove_dir_all(&home);
    }

    #[test]
    fn missing_config_is_an_empty_fleet_not_a_demo() {
        let fleet = read_at(
            Path::new("C:/definitely-not-a-simplicio-home"),
            1_900_000_000,
        );
        assert_eq!(fleet["schema"], FLEET_SCHEMA);
        assert_eq!(fleet["configured"], false);
        assert_eq!(fleet["redacted"], true);
        assert_eq!(fleet["error"], Value::Null);
        assert_eq!(fleet["remotes"], json!([]));
    }

    #[test]
    fn refuses_a_config_that_stores_a_token() {
        let mut parsed = config(vec![remote("http://127.0.0.1:8787", None)]);
        parsed["remotes"][0]["token"] = json!("secret");
        assert_eq!(
            parse_config(&parsed).unwrap_err(),
            "remote_config_unknown_field"
        );
    }

    #[test]
    fn response_cap_is_enforced() {
        assert_eq!(
            read_bounded(vec![0; MAX_BODY_BYTES as usize + 1].as_slice()).unwrap_err(),
            "response_too_large"
        );
    }
}
