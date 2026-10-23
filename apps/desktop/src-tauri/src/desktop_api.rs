//! Local, authenticated HTTP API for scripted Desktop actions.
//!
//! The server binds an ephemeral loopback port from Tauri's setup hook, writes a
//! versioned discovery file under the user's home directory, and requires a
//! random bearer token on every endpoint. It reuses the same fixed Runtime
//! commands and repository validators as the Tauri commands.

use serde::Deserialize;
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::io::{ErrorKind, Read, Write};
use std::net::{Ipv4Addr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{mpsc, Arc, Mutex, OnceLock};
use std::time::{Duration, Instant};

pub(crate) const SCHEMA: &str = "simplicio.desktop-api/v1";
pub(crate) const RESPONSE_SCHEMA: &str = "simplicio.desktop-api-response/v1";
const HOST: &str = "127.0.0.1";
const TOKEN_BYTES: usize = 32;
const MAX_HEADER_BYTES: usize = 8 * 1024;
const MAX_BODY_BYTES: usize = 8 * 1024;
const MAX_TARGET_BYTES: usize = 4 * 1024;
const REQUEST_TIMEOUT: Duration = Duration::from_secs(10);
const ACCEPT_POLL: Duration = Duration::from_millis(10);
const WORKERS: usize = 4;

static API_INFO: OnceLock<ApiInfo> = OnceLock::new();
static API_SHUTDOWN: OnceLock<Arc<AtomicBool>> = OnceLock::new();
static API_START_LOCK: Mutex<()> = Mutex::new(());

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ApiInfo {
    host: String,
    port: u16,
}

impl ApiInfo {
    fn new(port: u16) -> Self {
        Self {
            host: HOST.to_string(),
            port,
        }
    }

    fn status_json(&self) -> Value {
        json!({
            "schema": SCHEMA,
            "status": "running",
            "host": self.host,
            "port": self.port,
        })
    }
}

/// Starts the local API once per process. The bearer token is written to the
/// discovery file and is never returned from this function or logged.
pub(crate) fn start() -> Result<(), String> {
    let _guard = API_START_LOCK
        .lock()
        .map_err(|_| "desktop_api_unavailable".to_string())?;
    if API_INFO.get().is_some() {
        return Ok(());
    }

    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0))
        .map_err(|_| "desktop_api_bind_failed".to_string())?;
    let port = listener
        .local_addr()
        .map_err(|_| "desktop_api_bind_failed".to_string())?
        .port();
    let info = ApiInfo::new(port);
    let token = generate_token()?;
    let home = api_home()?;
    write_token_file(&home, &info, &token)?;

    let shutdown = Arc::new(AtomicBool::new(false));
    let server_shutdown = Arc::clone(&shutdown);
    let server_info = info.clone();
    if let Err(error) = std::thread::Builder::new()
        .name("simplicio-desktop-api".to_string())
        .spawn(move || {
            serve(
                listener,
                token,
                server_info,
                server_shutdown,
                Arc::new(NativeActions),
            )
        })
    {
        let _ = std::fs::remove_file(token_file_path(&home));
        return Err(format!("desktop_api_start_failed: {error}"));
    }

    let _ = API_SHUTDOWN.set(shutdown);
    let _ = API_INFO.set(info);
    Ok(())
}

/// Safe metadata for the `desktop_api_status` Tauri command.
pub(crate) fn status() -> Value {
    match API_INFO.get() {
        Some(info) => info.status_json(),
        None => json!({
            "schema": SCHEMA,
            "status": "unavailable",
            "host": HOST,
            "port": Value::Null,
        }),
    }
}

fn api_home() -> Result<PathBuf, String> {
    let home = if cfg!(windows) {
        std::env::var_os("USERPROFILE").or_else(|| std::env::var_os("HOME"))
    } else {
        std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE"))
    };
    home.map(PathBuf::from)
        .ok_or_else(|| "desktop_api_home_unavailable".to_string())
}

fn token_file_path(home: &Path) -> PathBuf {
    home.join(".simplicio").join("desktop-api.json")
}

fn write_token_file(home: &Path, info: &ApiInfo, token: &str) -> Result<(), String> {
    let path = token_file_path(home);
    let directory = path
        .parent()
        .ok_or_else(|| "desktop_api_token_file_failed".to_string())?;
    std::fs::create_dir_all(directory).map_err(|_| "desktop_api_token_file_failed".to_string())?;
    let document = json!({
        "schema": SCHEMA,
        "host": info.host,
        "port": info.port,
        "token": token,
    });
    let bytes =
        serde_json::to_vec(&document).map_err(|_| "desktop_api_token_file_failed".to_string())?;
    let temporary = directory.join(format!("desktop-api.json.{}.tmp", std::process::id()));
    std::fs::write(&temporary, &bytes).map_err(|_| "desktop_api_token_file_failed".to_string())?;
    restrict_token_file(&temporary);
    if std::fs::rename(&temporary, &path).is_err() {
        let _ = std::fs::remove_file(&path);
        if std::fs::rename(&temporary, &path).is_err() {
            let _ = std::fs::remove_file(&temporary);
            return Err("desktop_api_token_file_failed".to_string());
        }
    }
    restrict_token_file(&path);
    Ok(())
}

#[cfg(unix)]
fn restrict_token_file(path: &Path) {
    use std::os::unix::fs::PermissionsExt;
    let _ = std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o600));
}

#[cfg(windows)]
fn restrict_token_file(path: &Path) {
    let Ok(user) = std::env::var("USERNAME") else {
        return;
    };
    if user.trim().is_empty() {
        return;
    }
    let granted = std::process::Command::new("icacls")
        .arg(path)
        .args(["/grant:r"])
        .arg(format!("{user}:F"))
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false);
    if granted {
        let _ = std::process::Command::new("icacls")
            .arg(path)
            .args(["/inheritance:r"])
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status();
    }
}

#[cfg(not(any(unix, windows)))]
fn restrict_token_file(_path: &Path) {}

fn generate_token() -> Result<String, String> {
    use ring::rand::{SecureRandom, SystemRandom};
    let random = SystemRandom::new();
    let mut bytes = [0u8; TOKEN_BYTES];
    random
        .fill(&mut bytes)
        .map_err(|_| "desktop_api_token_unavailable".to_string())?;
    Ok(bytes.iter().map(|byte| format!("{byte:02x}")).collect())
}

fn token_matches(provided: &str, expected: &str) -> bool {
    // Compare the full maximum length without an early return so a wrong token
    // does not disclose which byte or length differed.
    let provided = provided.as_bytes();
    let expected = expected.as_bytes();
    let mut difference = provided.len() ^ expected.len();
    for index in 0..provided.len().max(expected.len()) {
        let left = provided.get(index).copied().unwrap_or(0);
        let right = expected.get(index).copied().unwrap_or(0);
        difference |= usize::from(left ^ right);
    }
    difference == 0
}

fn bearer_token(header: &str) -> Option<&str> {
    let mut parts = header.split_whitespace();
    let scheme = parts.next()?;
    if !scheme.eq_ignore_ascii_case("Bearer") {
        return None;
    }
    let token = parts.next()?;
    if parts.next().is_some() {
        return None;
    }
    Some(token)
}

enum AuthFailure {
    Missing,
    Forbidden,
}

impl AuthFailure {
    fn response(&self) -> (u16, Value) {
        match self {
            Self::Missing => (401, error_body("unauthorized")),
            Self::Forbidden => (403, error_body("forbidden")),
        }
    }
}

fn authorize(headers: &BTreeMap<String, String>, expected: &str) -> Result<(), AuthFailure> {
    let Some(header) = headers.get("authorization") else {
        return Err(AuthFailure::Missing);
    };
    let Some(token) = bearer_token(header) else {
        return Err(AuthFailure::Forbidden);
    };
    if token_matches(token, expected) {
        Ok(())
    } else {
        Err(AuthFailure::Forbidden)
    }
}

fn serve(
    listener: TcpListener,
    token: String,
    info: ApiInfo,
    shutdown: Arc<AtomicBool>,
    actions: Arc<dyn ScriptedActions>,
) {
    let _ = listener.set_nonblocking(true);
    let (sender, receiver) = mpsc::sync_channel::<TcpStream>(WORKERS * 8);
    let receiver = Arc::new(Mutex::new(receiver));
    let mut workers = Vec::with_capacity(WORKERS);

    for _ in 0..WORKERS {
        let receiver = Arc::clone(&receiver);
        let token = token.clone();
        let info = info.clone();
        let actions = Arc::clone(&actions);
        workers.push(std::thread::spawn(move || loop {
            let next = {
                let guard = match receiver.lock() {
                    Ok(guard) => guard,
                    Err(_) => break,
                };
                guard.recv()
            };
            match next {
                Ok(mut stream) => handle_connection(&mut stream, &token, &info, actions.as_ref()),
                Err(_) => break,
            }
        }));
    }

    while !shutdown.load(Ordering::SeqCst) {
        match listener.accept() {
            Ok((stream, _)) => match sender.try_send(stream) {
                Ok(()) => {}
                Err(mpsc::TrySendError::Full(_)) => {}
                Err(mpsc::TrySendError::Disconnected(_)) => break,
            },
            Err(error) if error.kind() == ErrorKind::WouldBlock => {
                std::thread::sleep(ACCEPT_POLL);
            }
            Err(_) => break,
        }
    }

    drop(sender);
    for worker in workers {
        let _ = worker.join();
    }
}

fn handle_connection(
    stream: &mut TcpStream,
    token: &str,
    info: &ApiInfo,
    actions: &dyn ScriptedActions,
) {
    // BSD/macOS accepts inherit the listener's non-blocking flag; the request
    // reader expects a blocking socket or a slow client answers 408 instead of
    // waiting for its bytes.
    let _ = stream.set_nonblocking(false);
    let _ = stream.set_read_timeout(Some(REQUEST_TIMEOUT));
    let _ = stream.set_write_timeout(Some(REQUEST_TIMEOUT));
    let (status, body) = match read_request(stream) {
        Ok(request) => dispatch(request, token, info, actions),
        Err(failure) => (failure.status(), failure.body()),
    };
    write_response(stream, status, &body);
}

struct Request {
    method: String,
    target: String,
    headers: BTreeMap<String, String>,
    body: Vec<u8>,
}

struct Target {
    path: String,
    query: BTreeMap<String, String>,
}

#[derive(Debug)]
enum RequestFailure {
    BadRequest,
    TooLarge,
    Timeout,
}

impl RequestFailure {
    fn status(&self) -> u16 {
        match self {
            Self::BadRequest => 400,
            Self::TooLarge => 413,
            Self::Timeout => 408,
        }
    }

    fn body(&self) -> Value {
        match self {
            Self::BadRequest => error_body("invalid_request"),
            Self::TooLarge => error_body("payload_too_large"),
            Self::Timeout => error_body("request_timeout"),
        }
    }
}

fn read_request(stream: &mut TcpStream) -> Result<Request, RequestFailure> {
    let deadline = Instant::now() + REQUEST_TIMEOUT;
    let mut buffer = Vec::new();
    let header_end = loop {
        if buffer.len() > MAX_HEADER_BYTES {
            return Err(RequestFailure::TooLarge);
        }
        if let Some(position) = buffer.windows(4).position(|window| window == b"\r\n\r\n") {
            let end = position + 4;
            if end > MAX_HEADER_BYTES {
                return Err(RequestFailure::TooLarge);
            }
            break end;
        }
        read_more(stream, &mut buffer, deadline)?;
    };

    let head =
        std::str::from_utf8(&buffer[..header_end - 4]).map_err(|_| RequestFailure::BadRequest)?;
    let mut request = parse_request_head(head)?;
    if request.headers.contains_key("transfer-encoding") {
        return Err(RequestFailure::BadRequest);
    }
    let content_length = content_length(&request.headers)?;
    if content_length > MAX_BODY_BYTES {
        return Err(RequestFailure::TooLarge);
    }
    let mut body = buffer[header_end..].to_vec();
    if body.len() > content_length {
        body.truncate(content_length);
    }
    while body.len() < content_length {
        let mut chunk = [0u8; 1024];
        let read = read_chunk(stream, &mut chunk, deadline)?;
        if read == 0 {
            return Err(RequestFailure::BadRequest);
        }
        body.extend_from_slice(&chunk[..read]);
        if body.len() > MAX_BODY_BYTES {
            return Err(RequestFailure::TooLarge);
        }
    }
    request.body = body;
    Ok(request)
}

fn read_more(
    stream: &mut TcpStream,
    buffer: &mut Vec<u8>,
    deadline: Instant,
) -> Result<(), RequestFailure> {
    let mut chunk = [0u8; 1024];
    let read = read_chunk(stream, &mut chunk, deadline)?;
    if read == 0 {
        return Err(RequestFailure::BadRequest);
    }
    buffer.extend_from_slice(&chunk[..read]);
    Ok(())
}

fn read_chunk(
    stream: &mut TcpStream,
    chunk: &mut [u8],
    deadline: Instant,
) -> Result<usize, RequestFailure> {
    let remaining = deadline.saturating_duration_since(Instant::now());
    if remaining.is_zero() {
        return Err(RequestFailure::Timeout);
    }
    let slice = remaining.min(Duration::from_secs(5));
    stream
        .set_read_timeout(Some(slice))
        .map_err(|_| RequestFailure::BadRequest)?;
    match stream.read(chunk) {
        Ok(read) => Ok(read),
        Err(error) if matches!(error.kind(), ErrorKind::WouldBlock | ErrorKind::TimedOut) => {
            Err(RequestFailure::Timeout)
        }
        Err(_) => Err(RequestFailure::BadRequest),
    }
}

fn parse_request_head(head: &str) -> Result<Request, RequestFailure> {
    let mut lines = head.split("\r\n");
    let request_line = lines.next().ok_or(RequestFailure::BadRequest)?;
    let (method, target, _version) = parse_request_line(request_line)?;
    let mut headers = BTreeMap::new();
    for line in lines {
        if line.is_empty() {
            continue;
        }
        let (name, value) = line.split_once(':').ok_or(RequestFailure::BadRequest)?;
        if name.is_empty() || !name.bytes().all(is_token_byte) {
            return Err(RequestFailure::BadRequest);
        }
        let name = name.to_ascii_lowercase();
        if headers.insert(name, value.trim().to_string()).is_some() {
            return Err(RequestFailure::BadRequest);
        }
    }
    Ok(Request {
        method: method.to_string(),
        target: target.to_string(),
        headers,
        body: Vec::new(),
    })
}

fn parse_request_line(line: &str) -> Result<(&str, &str, &str), RequestFailure> {
    if line.len() > MAX_TARGET_BYTES + 32 {
        return Err(RequestFailure::TooLarge);
    }
    let mut parts = line.split(' ');
    let method = parts.next().ok_or(RequestFailure::BadRequest)?;
    let target = parts.next().ok_or(RequestFailure::BadRequest)?;
    let version = parts.next().ok_or(RequestFailure::BadRequest)?;
    if parts.next().is_some()
        || method.is_empty()
        || target.is_empty()
        || version.is_empty()
        || !method.bytes().all(is_token_byte)
        || !target.starts_with('/')
        || target.len() > MAX_TARGET_BYTES
        || !matches!(version, "HTTP/1.0" | "HTTP/1.1")
    {
        return Err(RequestFailure::BadRequest);
    }
    Ok((method, target, version))
}

fn is_token_byte(byte: u8) -> bool {
    byte.is_ascii_alphanumeric() || b"!#$%&'*+-.^_|~".contains(&byte) || byte == 0x60
}

fn content_length(headers: &BTreeMap<String, String>) -> Result<usize, RequestFailure> {
    let Some(value) = headers.get("content-length") else {
        return Ok(0);
    };
    if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
        return Err(RequestFailure::BadRequest);
    }
    value.parse::<usize>().map_err(|_| RequestFailure::TooLarge)
}

/// Groups the scripted twin (`simplicio desktop <group> ...` and the
/// `simplicio_desktop` MCP tool) advertises. Every Runtime call behind them is a
/// trait method so the routes can be tested without an installed Runtime.
pub(crate) trait ScriptedActions: Send + Sync {
    /// `simplicio goal report [--repo <p>] [--id <goal>] --json`.
    fn run(&self, repo: Option<&str>, goal_id: Option<&str>) -> Result<Value, String>;
    /// `simplicio evidence receipt get --run-id <id> --json`.
    fn receipt(&self, run_id: &str) -> Result<Value, String>;
    /// The existing execution-report projection, reused by `report open`.
    fn report(&self, repo: Option<&str>, run_id: Option<&str>) -> Result<Value, String>;
    /// `git diff` for one worktree, bounded and redacted.
    fn diff(&self, path: &str, base: Option<&str>) -> Result<Value, String>;
    /// `review commit` — one commit with the human's message, receipt with sha.
    fn review_commit(
        &self,
        repo: &str,
        digest: &str,
        message: &str,
        base: Option<&str>,
    ) -> Result<Value, String>;
    /// `review push` — pushes a recorded commit; there is no force variant.
    fn review_push(
        &self,
        repo: &str,
        digest: &str,
        sha: &str,
        create_upstream: bool,
    ) -> Result<Value, String>;
}

struct NativeActions;

impl ScriptedActions for NativeActions {
    fn run(&self, repo: Option<&str>, goal_id: Option<&str>) -> Result<Value, String> {
        crate::require_read_access()?;
        let mut args = vec!["goal".to_string(), "report".to_string()];
        if let Some(repo) = repo {
            args.push("--repo".to_string());
            args.push(repo.to_string());
        }
        if let Some(goal_id) = goal_id {
            args.push("--id".to_string());
            args.push(goal_id.to_string());
        }
        args.push("--json".to_string());
        let borrowed = args.iter().map(String::as_str).collect::<Vec<_>>();
        crate::run_runtime_json(&borrowed).map_err(|_| "run_unavailable".to_string())
    }

    fn receipt(&self, run_id: &str) -> Result<Value, String> {
        crate::require_read_access()?;
        let args = ["evidence", "receipt", "get", "--run-id", run_id, "--json"];
        crate::run_runtime_json(&args).map_err(|_| "receipt_unavailable".to_string())
    }

    fn report(&self, repo: Option<&str>, run_id: Option<&str>) -> Result<Value, String> {
        crate::execution_report_from(repo, run_id)
    }

    fn diff(&self, path: &str, base: Option<&str>) -> Result<Value, String> {
        crate::diff_from_path(path, base)
    }

    fn review_commit(
        &self,
        repo: &str,
        digest: &str,
        message: &str,
        base: Option<&str>,
    ) -> Result<Value, String> {
        crate::review_commit_from_repo(repo, digest, message, base)
    }

    fn review_push(
        &self,
        repo: &str,
        digest: &str,
        sha: &str,
        create_upstream: bool,
    ) -> Result<Value, String> {
        crate::review_push_from_repo(repo, digest, sha, create_upstream)
    }
}

/// `simplicio.desktop-run/v1`, `receipt/v1` and the diff schema; one document per
/// group, matching the twin's group names.
pub(crate) const RUN_SCHEMA: &str = "simplicio.desktop-run/v1";
pub(crate) const RECEIPT_SCHEMA: &str = "simplicio.desktop-receipt/v1";
/// Statuses that mean the run is no longer active (`run wait --for idle`).
const TERMINAL_RUN_STATUSES: &[&str] = &[
    "complete",
    "completed",
    "done",
    "failed",
    "cancelled",
    "canceled",
    "idle",
];
const MAX_SELECTOR_BYTES: usize = 4096;

/// `id:<x>`, `path:<p>` or `issue:<n>`, parsed exactly like the Runtime twin:
/// an unprefixed value is rejected, never guessed.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum Selector {
    Id(String),
    Path(String),
    Issue(u64),
}

impl Selector {
    fn parse(raw: &str) -> Result<Self, String> {
        let bad = || "invalid_selector".to_string();
        if raw.is_empty()
            || raw.len() > MAX_SELECTOR_BYTES
            || raw.chars().any(|value| matches!(value, '\0' | '\r' | '\n'))
        {
            return Err(bad());
        }
        let (kind, value) = raw.split_once(':').ok_or_else(bad)?;
        if value.is_empty() {
            return Err(bad());
        }
        match kind {
            "id" => {
                if value.chars().any(char::is_whitespace) {
                    return Err(bad());
                }
                Ok(Self::Id(value.to_string()))
            }
            "path" => Ok(Self::Path(value.to_string())),
            "issue" => value.parse().map(Self::Issue).map_err(|_| bad()),
            _ => Err(bad()),
        }
    }

    fn kind(&self) -> &'static str {
        match self {
            Self::Id(_) => "id",
            Self::Path(_) => "path",
            Self::Issue(_) => "issue",
        }
    }

    fn value(&self) -> String {
        match self {
            Self::Id(value) | Self::Path(value) => value.clone(),
            Self::Issue(issue) => issue.to_string(),
        }
    }

    fn document(&self) -> Value {
        json!({
            "raw": format!("{}:{}", self.kind(), self.value()),
            "kind": self.kind(),
            "value": self.value(),
        })
    }
}

fn required_selector(query: &BTreeMap<String, String>) -> Result<Selector, String> {
    let raw = query
        .get("selector")
        .ok_or_else(|| "selector_required".to_string())?;
    Selector::parse(raw)
}

/// Base repository for `issue:<n>`/`id:<x>` lookups: the `repo` parameter, or
/// the same default the other routes use.
fn selector_base_repo(query: &BTreeMap<String, String>) -> Result<String, String> {
    match query.get("repo") {
        Some(repo) => Ok(repo.clone()),
        None => default_repo_string(),
    }
}

fn issue_worktree(query: &BTreeMap<String, String>, issue: u64) -> Result<String, String> {
    if issue == 0 {
        return Err("issue_invalid".to_string());
    }
    crate::worktree_path_for(&selector_base_repo(query)?, &format!("issue-{issue}"))
}

fn run_is_idle(document: &Value) -> bool {
    ["/goal/status", "/status", "/loop/status"]
        .iter()
        .filter_map(|pointer| document.pointer(pointer).and_then(Value::as_str))
        .any(|status| TERMINAL_RUN_STATUSES.contains(&status.to_ascii_lowercase().as_str()))
}

struct WaitPolicy {
    attempts: u32,
    gap: Duration,
}

#[cfg(test)]
fn wait_policy() -> WaitPolicy {
    WaitPolicy {
        attempts: 3,
        gap: Duration::from_millis(1),
    }
}

#[cfg(not(test))]
fn wait_policy() -> WaitPolicy {
    WaitPolicy {
        attempts: 5,
        gap: Duration::from_millis(200),
    }
}

/// `path:` names the working tree, so a separate `repo` would be ambiguous.
/// `issue:`/`id:` still use `repo` as the base repository for the lookup.
fn reject_redundant_repo(
    selector: &Selector,
    query: &BTreeMap<String, String>,
) -> Result<(), String> {
    if matches!(selector, Selector::Path(_)) && query.contains_key("repo") {
        return Err("invalid_query".to_string());
    }
    Ok(())
}

fn run_data(
    query: &BTreeMap<String, String>,
    actions: &dyn ScriptedActions,
) -> Result<Value, String> {
    let selector = required_selector(query)?;
    reject_redundant_repo(&selector, query)?;
    let wait = query.get("wait").map(String::as_str);
    if let Some(wait) = wait {
        if wait != "idle" {
            return Err("invalid_query".to_string());
        }
    }
    let repo = match &selector {
        Selector::Id(_) => query.get("repo").cloned(),
        Selector::Path(path) => Some(crate::validated_repo_path(path)?.display().to_string()),
        Selector::Issue(issue) => Some(issue_worktree(query, *issue)?),
    };
    let goal_id = match &selector {
        Selector::Id(value) => Some(value.clone()),
        _ => None,
    };
    let mut document = actions.run(repo.as_deref(), goal_id.as_deref())?;
    let waited = match wait {
        None => Value::Null,
        Some(_) => {
            let policy = wait_policy();
            let started = Instant::now();
            let mut attempts = 1u32;
            while !run_is_idle(&document) && attempts < policy.attempts {
                std::thread::sleep(policy.gap);
                document = actions.run(repo.as_deref(), goal_id.as_deref())?;
                attempts += 1;
            }
            let idle = run_is_idle(&document);
            json!({
                "for": "idle",
                "outcome": if idle { "idle" } else { "timeout" },
                "attempts": attempts,
                "elapsed_ms": started.elapsed().as_millis() as u64,
            })
        }
    };
    Ok(json!({
        "schema": RUN_SCHEMA,
        "group": "run",
        "action": if wait.is_some() { "wait" } else { "open" },
        "selector": selector.document(),
        "repo": repo,
        "goal_id": goal_id,
        "wait": waited,
        "run": document,
    }))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RunRequest {
    selector: String,
    #[serde(default)]
    wait: Option<String>,
    #[serde(default)]
    repo: Option<String>,
}

fn post_run_data(
    body: &[u8],
    query: &BTreeMap<String, String>,
    actions: &dyn ScriptedActions,
) -> Result<Value, String> {
    if query
        .keys()
        .any(|key| matches!(key.as_str(), "selector" | "wait" | "repo"))
    {
        return Err("invalid_query".to_string());
    }
    let request: RunRequest =
        serde_json::from_slice(body).map_err(|_| "invalid_json".to_string())?;
    let mut merged = BTreeMap::new();
    merged.insert("selector".to_string(), request.selector);
    if let Some(wait) = request.wait {
        merged.insert("wait".to_string(), wait);
    }
    if let Some(repo) = request.repo {
        merged.insert("repo".to_string(), repo);
    }
    run_data(&merged, actions)
}

fn diff_data(
    query: &BTreeMap<String, String>,
    actions: &dyn ScriptedActions,
) -> Result<Value, String> {
    let selector = required_selector(query)?;
    reject_redundant_repo(&selector, query)?;
    let base = query
        .get("base")
        .map(String::as_str)
        .filter(|value| !value.trim().is_empty());
    if let Some(base) = base {
        if !crate::review_submit::valid_base_revision(base) {
            return Err("review_base_invalid".to_string());
        }
    }
    let target = match &selector {
        Selector::Id(id) => crate::worktree_path_for(&selector_base_repo(query)?, id)?,
        Selector::Path(path) => crate::validated_repo_path(path)?.display().to_string(),
        Selector::Issue(issue) => issue_worktree(query, *issue)?,
    };
    let snapshot = actions.diff(&target, base)?;
    Ok(json!({
        "schema": crate::DIFF_SCHEMA,
        "group": "diff",
        "action": "open",
        "selector": selector.document(),
        "path": target,
        "base": base,
        "snapshot": snapshot,
    }))
}

fn receipt_data(
    query: &BTreeMap<String, String>,
    actions: &dyn ScriptedActions,
) -> Result<Value, String> {
    let selector = required_selector(query)?;
    // A receipt is addressed by run id; `path:`/`issue:` name a worktree and
    // cannot identify one, so they are refused instead of guessed.
    let run_id = match &selector {
        Selector::Id(value) => value.clone(),
        _ => return Err("selector_kind_unsupported".to_string()),
    };
    let receipt = actions.receipt(&run_id)?;
    Ok(json!({
        "schema": RECEIPT_SCHEMA,
        "group": "receipt",
        "action": "open",
        "selector": selector.document(),
        "run_id": run_id,
        "receipt": receipt,
    }))
}

fn report_data(
    query: &BTreeMap<String, String>,
    actions: &dyn ScriptedActions,
) -> Result<Value, String> {
    let Some(raw) = query.get("selector") else {
        return actions.report(query.get("repo").map(String::as_str), None);
    };
    let selector = Selector::parse(raw)?;
    match &selector {
        // `repo` keeps its meaning as the repository filter for a run id.
        Selector::Id(run_id) => actions.report(query.get("repo").map(String::as_str), Some(run_id)),
        other => {
            reject_redundant_repo(&selector, query)?;
            let repo = match other {
                Selector::Path(path) => crate::validated_repo_path(path)?.display().to_string(),
                Selector::Issue(issue) => issue_worktree(query, *issue)?,
                Selector::Id(_) => unreachable!("handled above"),
            };
            actions.report(Some(&repo), None)
        }
    }
}

/// One authoritative table for the routes: path, methods and accepted query
/// keys. Dispatch, `405` and `invalid_query` all read it, so a route cannot be
/// half-registered.
struct Route {
    path: &'static str,
    methods: &'static [&'static str],
    query: &'static [&'static str],
}

const ROUTES: &[Route] = &[
    Route {
        path: "/v1/health",
        methods: &["GET"],
        query: &[],
    },
    Route {
        path: "/v1/snapshot",
        methods: &["GET"],
        query: &[],
    },
    Route {
        path: "/v1/report",
        methods: &["GET"],
        query: &["repo", "selector"],
    },
    Route {
        path: "/v1/review",
        methods: &["GET"],
        query: &["repo", "base"],
    },
    Route {
        path: "/v1/review/commit",
        methods: &["POST"],
        query: &[],
    },
    Route {
        path: "/v1/review/push",
        methods: &["POST"],
        query: &[],
    },
    Route {
        path: "/v1/worktrees",
        methods: &["GET"],
        query: &["repo"],
    },
    Route {
        path: "/v1/worktree",
        methods: &["POST"],
        query: &["repo"],
    },
    Route {
        path: "/v1/run",
        methods: &["GET", "POST"],
        query: &["selector", "repo", "wait"],
    },
    Route {
        path: "/v1/diff",
        methods: &["GET"],
        query: &["selector", "repo", "base"],
    },
    Route {
        path: "/v1/receipt",
        methods: &["GET"],
        query: &["selector"],
    },
];

fn route(path: &str) -> Option<&'static Route> {
    ROUTES.iter().find(|route| route.path == path)
}

fn dispatch(
    request: Request,
    token: &str,
    info: &ApiInfo,
    actions: &dyn ScriptedActions,
) -> (u16, Value) {
    if let Err(failure) = authorize(&request.headers, token) {
        return failure.response();
    }

    let target = match parse_target(&request.target) {
        Ok(target) => target,
        Err(failure) => return (failure.status(), failure.body()),
    };

    let Some(route) = route(&target.path) else {
        return (404, error_body("not_found"));
    };
    if !route.methods.contains(&request.method.as_str()) {
        return (405, error_body("method_not_allowed"));
    }
    if target
        .query
        .keys()
        .any(|key| !route.query.contains(&key.as_str()))
    {
        return (400, error_body("invalid_query"));
    }

    match (request.method.as_str(), target.path.as_str()) {
        ("GET", "/v1/health") => (200, ok_body(health_data(info))),
        ("GET", "/v1/snapshot") => result_body(crate::snapshot_from_runtime()),
        ("GET", "/v1/report") => result_body(report_data(&target.query, actions)),
        ("GET", "/v1/review") => result_body(review_data(
            target.query.get("repo").map(String::as_str),
            target.query.get("base").map(String::as_str),
        )),
        ("POST", "/v1/review/commit") => result_body(review_commit_data(&request.body, actions)),
        ("POST", "/v1/review/push") => result_body(review_push_data(&request.body, actions)),
        ("GET", "/v1/worktrees") => {
            result_body(worktrees_data(target.query.get("repo").map(String::as_str)))
        }
        ("POST", "/v1/worktree") => result_body(worktree_data(
            &request.body,
            target.query.get("repo").map(String::as_str),
        )),
        ("GET", "/v1/run") => result_body(run_data(&target.query, actions)),
        ("POST", "/v1/run") => result_body(post_run_data(&request.body, &target.query, actions)),
        ("GET", "/v1/diff") => result_body(diff_data(&target.query, actions)),
        ("GET", "/v1/receipt") => result_body(receipt_data(&target.query, actions)),
        _ => (404, error_body("not_found")),
    }
}

fn health_data(info: &ApiInfo) -> Value {
    json!({
        "schema": SCHEMA,
        "status": "ok",
        "service": "simplicio-desktop",
        "version": env!("CARGO_PKG_VERSION"),
        "host": info.host,
        "port": info.port,
    })
}

fn default_repo_string() -> Result<String, String> {
    crate::default_projection_repo().map(|path| path.to_string_lossy().into_owned())
}

fn review_data(repo: Option<&str>, base: Option<&str>) -> Result<Value, String> {
    let repo = match repo {
        Some(repo) => repo.to_string(),
        None => default_repo_string()?,
    };
    crate::review_from_repo(&repo, base)
}

fn worktrees_data(repo: Option<&str>) -> Result<Value, String> {
    let repo = match repo {
        Some(repo) => repo.to_string(),
        None => default_repo_string()?,
    };
    crate::worktrees_from_repo(&repo)
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReviewCommitRequest {
    repo: String,
    digest: String,
    message: String,
    #[serde(default)]
    base: Option<String>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReviewPushRequest {
    repo: String,
    digest: String,
    sha: String,
    #[serde(default, rename = "createUpstream", alias = "create_upstream")]
    create_upstream: bool,
}

/// The commit mutation takes its repository and message from the body: there is
/// no default repository, because committing to a guessed tree is destructive.
fn review_commit_data(body: &[u8], actions: &dyn ScriptedActions) -> Result<Value, String> {
    let request: ReviewCommitRequest =
        serde_json::from_slice(body).map_err(|_| "invalid_json".to_string())?;
    let base = request
        .base
        .as_deref()
        .map(str::trim)
        .filter(|value| !value.is_empty());
    if let Some(base) = base {
        if !crate::review_submit::valid_base_revision(base) {
            return Err("review_base_invalid".to_string());
        }
    }
    actions.review_commit(&request.repo, &request.digest, &request.message, base)
}

fn review_push_data(body: &[u8], actions: &dyn ScriptedActions) -> Result<Value, String> {
    let request: ReviewPushRequest =
        serde_json::from_slice(body).map_err(|_| "invalid_json".to_string())?;
    actions.review_push(
        &request.repo,
        &request.digest,
        &request.sha,
        request.create_upstream,
    )
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct WorktreeRequest {
    issue: u64,
    agent: String,
    #[serde(rename = "wipLimit", alias = "wip_limit")]
    wip_limit: Option<u32>,
    #[serde(default, alias = "repoPath", alias = "repo_path")]
    repo: Option<String>,
}

fn worktree_data(body: &[u8], query_repo: Option<&str>) -> Result<Value, String> {
    let request: WorktreeRequest =
        serde_json::from_slice(body).map_err(|_| "invalid_json".to_string())?;
    let repo = match (request.repo.as_deref(), query_repo) {
        (Some(body_repo), Some(query_repo)) if body_repo != query_repo => {
            return Err("invalid_repo".to_string());
        }
        (Some(body_repo), _) => body_repo.to_string(),
        (None, Some(query_repo)) => query_repo.to_string(),
        (None, None) => default_repo_string()?,
    };
    crate::create_managed_worktree(&repo, request.issue, &request.agent, request.wip_limit)
}

fn parse_target(target: &str) -> Result<Target, RequestFailure> {
    let (path, query) = match target.split_once('?') {
        Some((path, query)) => (path, query),
        None => (target, ""),
    };
    let path = percent_decode(path)?;
    if path.is_empty()
        || !path.starts_with('/')
        || path.len() > MAX_TARGET_BYTES
        || path
            .chars()
            .any(|value| matches!(value, '\0' | '\r' | '\n'))
    {
        return Err(RequestFailure::BadRequest);
    }
    let mut parameters = BTreeMap::new();
    if !query.is_empty() {
        for pair in query.split('&') {
            if pair.is_empty() {
                continue;
            }
            let (key, value) = pair.split_once('=').unwrap_or((pair, ""));
            let key = percent_decode(key)?;
            let value = percent_decode(value)?;
            if value
                .chars()
                .any(|character| matches!(character, '\0' | '\r' | '\n'))
            {
                return Err(RequestFailure::BadRequest);
            }
            if key.is_empty()
                || key.len() > 128
                || !key
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'_' | b'-'))
            {
                return Err(RequestFailure::BadRequest);
            }
            if parameters.insert(key, value).is_some() {
                return Err(RequestFailure::BadRequest);
            }
        }
    }
    Ok(Target {
        path,
        query: parameters,
    })
}

fn percent_decode(value: &str) -> Result<String, RequestFailure> {
    let bytes = value.as_bytes();
    let mut decoded = Vec::with_capacity(bytes.len());
    let mut index = 0;
    while index < bytes.len() {
        match bytes[index] {
            b'%' => {
                if index + 2 >= bytes.len() {
                    return Err(RequestFailure::BadRequest);
                }
                let high = hex_value(bytes[index + 1]).ok_or(RequestFailure::BadRequest)?;
                let low = hex_value(bytes[index + 2]).ok_or(RequestFailure::BadRequest)?;
                decoded.push(high * 16 + low);
                index += 3;
            }
            b'+' => {
                decoded.push(b' ');
                index += 1;
            }
            byte => {
                decoded.push(byte);
                index += 1;
            }
        }
    }
    String::from_utf8(decoded).map_err(|_| RequestFailure::BadRequest)
}

fn hex_value(byte: u8) -> Option<u8> {
    match byte {
        b'0'..=b'9' => Some(byte - b'0'),
        b'a'..=b'f' => Some(byte - b'a' + 10),
        b'A'..=b'F' => Some(byte - b'A' + 10),
        _ => None,
    }
}

fn ok_body(data: Value) -> Value {
    json!({
        "schema": RESPONSE_SCHEMA,
        "status": "ok",
        "data": data,
    })
}

fn error_body(code: &str) -> Value {
    json!({
        "schema": RESPONSE_SCHEMA,
        "status": "error",
        "error": { "code": safe_error_code(code) },
    })
}

fn result_body(result: Result<Value, String>) -> (u16, Value) {
    match result {
        Ok(data) => (200, ok_body(data)),
        Err(code) => {
            let code = safe_error_code(&code);
            (error_status(&code), error_body(&code))
        }
    }
}

fn safe_error_code(code: &str) -> String {
    if !code.is_empty()
        && code.len() <= 128
        && code
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'_' | b'-'))
    {
        code.to_string()
    } else {
        "internal_error".to_string()
    }
}

fn error_status(code: &str) -> u16 {
    match code {
        "invalid_json"
        | "invalid_query"
        | "invalid_repo"
        | "repo_path_invalid"
        | "issue_invalid"
        | "agent_invalid"
        | "invalid_selector"
        | "selector_required"
        | "selector_kind_unsupported"
        | "review_base_invalid"
        | "review_digest_invalid"
        | "review_message_empty"
        | "review_message_too_large"
        | "review_message_invalid"
        | "review_commit_sha_invalid" => 400,
        "desktop_access_not_active" => 403,
        "worktree_not_found" => 404,
        "wip_limit_reached"
        | "worktree_exists"
        | "worktree_path_invalid"
        | "review_digest_mismatch"
        | "review_truncated"
        | "review_protected_path"
        | "review_changes_empty"
        | "review_path_invalid"
        | "review_branch_protected"
        | "review_branch_detached"
        | "review_commit_base_unsupported"
        | "review_commit_in_progress"
        | "review_commit_missing"
        | "review_commit_not_head"
        | "review_commit_branch_changed"
        | "review_commit_receipt_invalid"
        | "review_push_no_upstream"
        | "review_push_upstream_mismatch"
        | "review_push_upstream_invalid"
        | "review_push_refspec_invalid" => 409,
        _ if code.starts_with("runtime_")
            || code.ends_with("_unavailable")
            || code.ends_with("_failed")
            || code.ends_with("_unverified") =>
        {
            503
        }
        _ => 500,
    }
}

fn write_response(stream: &mut TcpStream, status: u16, body: &Value) {
    let bytes = serde_json::to_vec(body).unwrap_or_else(|_| {
        br#"{"schema":"simplicio.desktop-api-response/v1","status":"error","error":{"code":"serialization_failed"}}"#
            .to_vec()
    });
    let mut head = format!(
        "HTTP/1.1 {status} {}\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: {}\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n",
        reason(status),
        bytes.len()
    );
    if status == 401 {
        head.push_str("WWW-Authenticate: Bearer realm=\"simplicio-desktop-api\"\r\n");
    }
    head.push_str("\r\n");
    let _ = stream.write_all(head.as_bytes());
    let _ = stream.write_all(&bytes);
    let _ = stream.flush();
}

fn reason(status: u16) -> &'static str {
    match status {
        200 => "OK",
        400 => "Bad Request",
        401 => "Unauthorized",
        403 => "Forbidden",
        404 => "Not Found",
        405 => "Method Not Allowed",
        408 => "Request Timeout",
        409 => "Conflict",
        413 => "Payload Too Large",
        503 => "Service Unavailable",
        _ => "Internal Server Error",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::Command;
    use std::sync::atomic::AtomicU64;

    static NEXT_TEMP: AtomicU64 = AtomicU64::new(1);

    fn temp_home() -> PathBuf {
        let directory = std::env::temp_dir().join(format!(
            "simplicio-desktop-api-{}-{}",
            std::process::id(),
            NEXT_TEMP.fetch_add(1, Ordering::Relaxed)
        ));
        std::fs::create_dir_all(&directory).unwrap();
        directory
    }

    /// A throwaway repository with one committed change, for the local `git diff`.
    fn temp_repo() -> PathBuf {
        let directory = temp_home().join("repo");
        std::fs::create_dir_all(&directory).unwrap();
        let git = |args: &[&str]| {
            let output = Command::new("git")
                .arg("-C")
                .arg(&directory)
                .args(args)
                .output()
                .unwrap();
            assert!(output.status.success(), "git {args:?}: {output:?}");
        };
        git(&["init", "-q"]);
        git(&["config", "user.email", "api@example.com"]);
        git(&["config", "user.name", "Desktop API"]);
        std::fs::write(directory.join("a.txt"), "one\n").unwrap();
        git(&["add", "a.txt"]);
        git(&["commit", "-q", "-m", "initial"]);
        std::fs::write(directory.join("a.txt"), "one\ntwo\n").unwrap();
        directory
    }

    /// Canned group documents, plus the calls the routes made, so the routes can
    /// be exercised without an installed Runtime.
    struct FakeActions {
        run_documents: Mutex<Vec<Value>>,
        calls: Mutex<Vec<String>>,
    }

    impl FakeActions {
        fn returning(run_documents: Vec<Value>) -> Self {
            Self {
                run_documents: Mutex::new(run_documents),
                calls: Mutex::new(Vec::new()),
            }
        }

        fn calls(&self) -> Vec<String> {
            self.calls.lock().unwrap().clone()
        }
    }

    impl ScriptedActions for FakeActions {
        fn run(&self, repo: Option<&str>, goal_id: Option<&str>) -> Result<Value, String> {
            self.calls.lock().unwrap().push(format!(
                "run repo={} id={}",
                repo.unwrap_or("-"),
                goal_id.unwrap_or("-")
            ));
            let mut documents = self.run_documents.lock().unwrap();
            if documents.is_empty() {
                return Ok(json!({
                    "schema": "simplicio.goal-report/v1",
                    "goal": {"status": "open"},
                }));
            }
            if documents.len() > 1 {
                Ok(documents.remove(0))
            } else {
                Ok(documents[0].clone())
            }
        }

        fn receipt(&self, run_id: &str) -> Result<Value, String> {
            self.calls.lock().unwrap().push(format!("receipt {run_id}"));
            Ok(json!({"schema": "simplicio.evidence-receipt/v1", "run_id": run_id}))
        }

        fn report(&self, repo: Option<&str>, run_id: Option<&str>) -> Result<Value, String> {
            self.calls.lock().unwrap().push(format!(
                "report repo={} id={}",
                repo.unwrap_or("-"),
                run_id.unwrap_or("-")
            ));
            Ok(json!({
                "schema": "simplicio.execution-report/v1",
                "repo": repo,
                "run_id": run_id,
            }))
        }

        fn diff(&self, path: &str, base: Option<&str>) -> Result<Value, String> {
            self.calls
                .lock()
                .unwrap()
                .push(format!("diff path={path} base={}", base.unwrap_or("-")));
            Ok(json!({
                "schema": crate::DIFF_SCHEMA,
                "path": path,
                "base": base,
                "diff": "+canned",
                "truncated": false,
                "redacted": true,
            }))
        }

        fn review_commit(
            &self,
            repo: &str,
            digest: &str,
            message: &str,
            base: Option<&str>,
        ) -> Result<Value, String> {
            self.calls.lock().unwrap().push(format!(
                "commit repo={repo} digest={} chars={} base={}",
                digest,
                message.chars().count(),
                base.unwrap_or("-")
            ));
            Ok(json!({
                "schema": crate::review_git::COMMIT_SCHEMA,
                "status": "committed",
                "sha": "1".repeat(40),
                "branch": "work",
                "pushed": false,
                "redacted": true,
            }))
        }

        fn review_push(
            &self,
            repo: &str,
            digest: &str,
            sha: &str,
            create_upstream: bool,
        ) -> Result<Value, String> {
            self.calls.lock().unwrap().push(format!(
                "push repo={repo} digest={digest} sha={sha} create={create_upstream}"
            ));
            Ok(json!({
                "schema": crate::review_git::PUSH_SCHEMA,
                "status": "pushed",
                "sha": sha,
                "upstream": "origin/work",
                "idempotent": false,
                "redacted": true,
            }))
        }
    }

    struct Server {
        port: u16,
        token: String,
        shutdown: Arc<AtomicBool>,
        handle: Option<std::thread::JoinHandle<()>>,
    }

    impl Server {
        fn start(actions: Arc<dyn ScriptedActions>) -> Self {
            let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).unwrap();
            let port = listener.local_addr().unwrap().port();
            let token = generate_token().unwrap();
            let info = ApiInfo::new(port);
            let shutdown = Arc::new(AtomicBool::new(false));
            let server_shutdown = Arc::clone(&shutdown);
            let server_token = token.clone();
            let handle = std::thread::spawn(move || {
                serve(listener, server_token, info, server_shutdown, actions)
            });
            Self {
                port,
                token,
                shutdown,
                handle: Some(handle),
            }
        }

        fn request(&self, method: &str, target: &str, body: Option<&str>) -> String {
            let mut head = format!(
                "{method} {target} HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {}\r\nConnection: close\r\n",
                self.token
            );
            if let Some(body) = body {
                head.push_str(&format!(
                    "Content-Type: application/json\r\nContent-Length: {}\r\n",
                    body.len()
                ));
            }
            head.push_str("\r\n");
            if let Some(body) = body {
                head.push_str(body);
            }
            http_request(self.port, &head)
        }

        fn anonymous(&self, target: &str) -> String {
            http_request(
                self.port,
                &format!("GET {target} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"),
            )
        }
    }

    impl Drop for Server {
        fn drop(&mut self) {
            self.shutdown.store(true, Ordering::SeqCst);
            if let Some(handle) = self.handle.take() {
                let _ = handle.join();
            }
        }
    }

    fn http_request(port: u16, request: &str) -> String {
        let mut stream = TcpStream::connect_timeout(
            &std::net::SocketAddr::from((Ipv4Addr::LOCALHOST, port)),
            Duration::from_secs(5),
        )
        .unwrap();
        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        stream.write_all(request.as_bytes()).unwrap();
        let mut response = Vec::new();
        stream.read_to_end(&mut response).unwrap();
        String::from_utf8_lossy(&response).into_owned()
    }

    fn status_of(response: &str) -> u16 {
        response
            .split(' ')
            .nth(1)
            .and_then(|value| value.parse().ok())
            .unwrap_or(0)
    }

    fn body_of(response: &str) -> Value {
        let (_, body) = response.split_once("\r\n\r\n").unwrap_or(("", "{}"));
        serde_json::from_str(body).unwrap_or_else(|_| json!({}))
    }

    fn data_of(response: &str) -> Value {
        body_of(response)["data"].clone()
    }

    fn code_of(response: &str) -> String {
        body_of(response)["error"]["code"]
            .as_str()
            .unwrap_or_default()
            .to_string()
    }

    fn query_value(value: &str) -> String {
        value.replace('+', "%2B").replace(' ', "%20")
    }

    const SCRIPTED_TARGETS: [&str; 4] = [
        "/v1/run?selector=id:run-7",
        "/v1/diff?selector=path:/tmp",
        "/v1/receipt?selector=id:rc-1",
        "/v1/report?selector=id:run-7",
    ];

    #[test]
    fn generated_token_has_32_random_bytes() {
        let first = generate_token().unwrap();
        let second = generate_token().unwrap();
        assert_eq!(first.len(), TOKEN_BYTES * 2);
        assert!(first.bytes().all(|byte| byte.is_ascii_hexdigit()));
        assert_ne!(first, second);
    }

    #[test]
    fn comparisons_and_bearer_headers_are_strict() {
        assert!(token_matches("abc", "abc"));
        assert!(!token_matches("abc", "abd"));
        assert!(!token_matches("abc", "abcd"));
        assert_eq!(bearer_token("Bearer abc"), Some("abc"));
        assert_eq!(bearer_token("bearer abc"), Some("abc"));
        assert_eq!(bearer_token("Basic abc"), None);
        assert_eq!(bearer_token("Bearer"), None);
        assert_eq!(bearer_token("Bearer abc extra"), None);
    }

    #[test]
    fn request_lines_are_parsed_strictly() {
        assert_eq!(
            parse_request_line("GET /v1/health HTTP/1.1").unwrap(),
            ("GET", "/v1/health", "HTTP/1.1")
        );
        assert_eq!(
            parse_request_line("POST /v1/worktree HTTP/1.0").unwrap(),
            ("POST", "/v1/worktree", "HTTP/1.0")
        );
        assert!(parse_request_line("GET /v1/health").is_err());
        assert!(parse_request_line("GET  /v1/health HTTP/1.1").is_err());
        assert!(parse_request_line("GET /v1/health HTTP/1.1 extra").is_err());
        assert!(parse_request_line("GET /v1/health HTTP/2").is_err());
        assert!(parse_request_line("OPTIONS * HTTP/1.1").is_err());
        assert!(parse_request_line("GE(T /v1/health HTTP/1.1").is_err());
    }

    #[test]
    fn targets_decode_query_values_and_reject_duplicates() {
        let target = parse_target("/v1/report?repo=C%3A%5CUsers%5Cme").unwrap();
        assert_eq!(target.path, "/v1/report");
        assert_eq!(
            target.query.get("repo").map(String::as_str),
            Some("C:\\Users\\me")
        );
        let target = parse_target("/v1/review?repo=%2Ftmp%2Frepo&base=main").unwrap();
        assert_eq!(
            target.query.get("repo").map(String::as_str),
            Some("/tmp/repo")
        );
        assert_eq!(target.query.get("base").map(String::as_str), Some("main"));
        assert!(parse_target("/v1/report?repo=%ZZ").is_err());
        assert!(parse_target("/v1/report?repo=a&repo=b").is_err());
        assert!(parse_target("/v1/report?repo=%00").is_err());
        assert!(parse_target("v1/report").is_err());
    }

    #[test]
    fn repository_paths_must_exist_and_be_directories() {
        let directory = temp_home();
        let canonical = directory.canonicalize().unwrap();
        assert!(crate::validated_repo_path(&canonical.to_string_lossy()).is_ok());
        assert!(crate::validated_repo_path("").is_err());
        assert!(crate::validated_repo_path("   ").is_err());
        assert!(
            crate::validated_repo_path(&canonical.join("missing-directory").to_string_lossy())
                .is_err()
        );
        let _ = std::fs::remove_dir_all(directory);
    }

    #[test]
    fn token_file_is_versioned_discoverable_and_restricted() {
        let home = temp_home();
        let info = ApiInfo::new(4242);
        let token = generate_token().unwrap();
        write_token_file(&home, &info, &token).unwrap();
        let path = token_file_path(&home);
        let document: Value = serde_json::from_slice(&std::fs::read(&path).unwrap()).unwrap();
        assert_eq!(document["schema"].as_str(), Some(SCHEMA));
        assert_eq!(document["host"].as_str(), Some(HOST));
        assert_eq!(document["port"].as_u64(), Some(4242));
        assert_eq!(document["token"].as_str(), Some(token.as_str()));
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mode = std::fs::metadata(&path).unwrap().permissions().mode();
            assert_eq!(mode & 0o077, 0);
        }
        let _ = std::fs::remove_dir_all(home);
    }

    #[test]
    fn listener_requires_the_bearer_token_on_health() {
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));

        let missing = http_request(
            server.port,
            "GET /v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n",
        );
        assert_eq!(status_of(&missing), 401, "{missing}");
        assert!(missing.contains(RESPONSE_SCHEMA));
        assert!(missing.contains("unauthorized"));

        let wrong = http_request(
            server.port,
            &format!(
                "GET /v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {}\r\nConnection: close\r\n\r\n",
                "0".repeat(TOKEN_BYTES * 2)
            ),
        );
        assert_eq!(status_of(&wrong), 403, "{wrong}");
        assert!(wrong.contains("forbidden"));

        let accepted = server.request("GET", "/v1/health", None);
        assert_eq!(status_of(&accepted), 200, "{accepted}");
        assert!(accepted.contains(RESPONSE_SCHEMA));
        assert!(accepted.contains("\"status\":\"ok\""));
        assert!(!accepted.contains(&server.token));
    }

    #[test]
    fn status_never_exposes_the_token() {
        let info = ApiInfo::new(5555);
        let status = info.status_json();
        assert_eq!(status["schema"].as_str(), Some(SCHEMA));
        assert_eq!(status["status"].as_str(), Some("running"));
        assert_eq!(status["host"].as_str(), Some(HOST));
        assert_eq!(status["port"].as_u64(), Some(5555));
        assert!(status.get("token").is_none());
    }

    #[test]
    fn selector_grammar_matches_the_runtime_twin() {
        assert_eq!(
            Selector::parse("id:run-7"),
            Ok(Selector::Id("run-7".into()))
        );
        assert_eq!(
            Selector::parse("path:/tmp/wt"),
            Ok(Selector::Path("/tmp/wt".into()))
        );
        assert_eq!(Selector::parse("issue:439"), Ok(Selector::Issue(439)));
        for bad in [
            "run-7",
            "issue:x",
            "id:",
            "path:",
            "branch:main",
            "",
            "id:a\nb",
        ] {
            assert_eq!(
                Selector::parse(bad),
                Err("invalid_selector".to_string()),
                "accepted {bad:?}"
            );
        }
        let long = format!("id:{}", "a".repeat(MAX_SELECTOR_BYTES));
        assert!(Selector::parse(&long).is_err());
        assert_eq!(
            Selector::Issue(439).document(),
            json!({"raw": "issue:439", "kind": "issue", "value": "439"})
        );
    }

    #[test]
    fn route_table_is_the_only_source_of_paths_methods_and_query_keys() {
        let mut paths = std::collections::BTreeSet::new();
        for entry in ROUTES {
            assert!(paths.insert(entry.path), "duplicate route {}", entry.path);
            assert!(!entry.methods.is_empty(), "{}", entry.path);
            assert!(route(entry.path).is_some(), "{}", entry.path);
        }
        // Everything the twin advertises is now a route.
        for path in ["/v1/run", "/v1/diff", "/v1/receipt"] {
            assert!(route(path).is_some(), "{path} is not registered");
        }

        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        assert_eq!(status_of(&server.request("GET", "/v1/nope", None)), 404);
        assert_eq!(
            code_of(&server.request("GET", "/v1/nope", None)),
            "not_found"
        );
        assert_eq!(status_of(&server.request("GET", "/v1/worktree", None)), 405);
        assert_eq!(status_of(&server.request("POST", "/v1/diff", None)), 405);
        assert_eq!(
            code_of(&server.request("POST", "/v1/diff", None)),
            "method_not_allowed"
        );
        for (target, key) in [
            ("/v1/run?selector=id:x&base=main", "base"),
            ("/v1/diff?selector=path:/tmp&wait=idle", "wait"),
            ("/v1/receipt?selector=id:x&repo=/tmp", "repo"),
            ("/v1/health?repo=/tmp", "repo"),
        ] {
            let response = server.request("GET", target, None);
            assert_eq!(status_of(&response), 400, "{target}: {response}");
            assert_eq!(code_of(&response), "invalid_query", "{target} {key}");
        }
    }

    #[test]
    fn every_scripted_route_rejects_an_unauthenticated_call() {
        let actions = Arc::new(FakeActions::returning(Vec::new()));
        let server = Server::start(Arc::clone(&actions) as Arc<dyn ScriptedActions>);
        for target in SCRIPTED_TARGETS {
            let response = server.anonymous(target);
            assert_eq!(status_of(&response), 401, "{target}: {response}");
            assert_eq!(code_of(&response), "unauthorized", "{target}");
        }
        // Nothing was executed for an unauthenticated call.
        assert!(actions.calls().is_empty(), "{:?}", actions.calls());
    }

    #[test]
    fn review_commit_and_push_routes_share_the_api_authorization() {
        let actions = Arc::new(FakeActions::returning(Vec::new()));
        let server = Server::start(Arc::clone(&actions) as Arc<dyn ScriptedActions>);
        for path in ["/v1/review/commit", "/v1/review/push"] {
            // 401: no Authorization header, even with a body.
            let anonymous = http_request(
                server.port,
                &format!(
                    "POST {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Type: application/json\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{{}}"
                ),
            );
            assert_eq!(status_of(&anonymous), 401, "{path}: {anonymous}");
            assert_eq!(code_of(&anonymous), "unauthorized", "{path}");
        }
        // 403: a valid shape with the wrong token never reaches the action.
        for path in ["/v1/review/commit", "/v1/review/push"] {
            let forbidden = http_request(
                server.port,
                &format!(
                    "POST {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {}\r\nContent-Type: application/json\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{{}}",
                    "0".repeat(TOKEN_BYTES * 2)
                ),
            );
            assert_eq!(status_of(&forbidden), 403, "{path}: {forbidden}");
            assert_eq!(code_of(&forbidden), "forbidden", "{path}");
        }
        // An authorized call is the first one that reaches the action seam.
        assert!(actions.calls().is_empty(), "{:?}", actions.calls());
        assert_eq!(status_of(&server.request("GET", "/v1/review/commit", None)), 405);
        assert_eq!(
            code_of(&server.request("GET", "/v1/review/push", None)),
            "method_not_allowed"
        );
    }

    #[test]
    fn review_commit_route_commits_the_message_from_the_body() {
        let actions = Arc::new(FakeActions::returning(Vec::new()));
        let server = Server::start(Arc::clone(&actions) as Arc<dyn ScriptedActions>);
        let body = json!({
            "repo": "/tmp/worktree",
            "digest": format!("sha256:{}", "a".repeat(64)),
            "message": "feat: reviewed",
            "base": "   ",
        })
        .to_string();
        let response = server.request("POST", "/v1/review/commit", Some(&body));
        assert_eq!(status_of(&response), 200, "{response}");
        let data = data_of(&response);
        assert_eq!(data["status"], json!("committed"));
        assert_eq!(
            data["sha"],
            json!("1".repeat(40)),
            "the api returns the sha verbatim"
        );
        assert_eq!(
            actions.calls(),
            vec![format!(
                "commit repo=/tmp/worktree digest=sha256:{} chars=14 base=-",
                "a".repeat(64)
            )]
        );

        // A body-only route: any query key is a contract violation.
        let with_query = server.request(
            "POST",
            "/v1/review/commit?repo=/tmp/worktree",
            Some(&body),
        );
        assert_eq!(status_of(&with_query), 400, "{with_query}");
        assert_eq!(code_of(&with_query), "invalid_query");

        // Unknown fields are refused instead of ignored.
        let unknown = server.request(
            "POST",
            "/v1/review/commit",
            Some(&json!({"repo": "/tmp", "digest": "x", "message": "y", "force": true}).to_string()),
        );
        assert_eq!(status_of(&unknown), 400, "{unknown}");
        assert_eq!(code_of(&unknown), "invalid_json");
        let empty = server.request("POST", "/v1/review/commit", Some(""));
        assert_eq!(status_of(&empty), 400, "{empty}");
        assert_eq!(code_of(&empty), "invalid_json");
        // A base is one revision, validated like the review route.
        let bad_base = server.request(
            "POST",
            "/v1/review/commit",
            Some(&json!({"repo": "/tmp", "digest": "x", "message": "y", "base": "--output=/tmp/x"}).to_string()),
        );
        assert_eq!(status_of(&bad_base), 400, "{bad_base}");
        assert_eq!(code_of(&bad_base), "review_base_invalid");
    }

    #[test]
    fn review_push_route_requires_a_sha_and_an_explicit_upstream_choice() {
        let actions = Arc::new(FakeActions::returning(Vec::new()));
        let server = Server::start(Arc::clone(&actions) as Arc<dyn ScriptedActions>);
        let sha = "2".repeat(40);
        let body = json!({
            "repo": "/tmp/worktree",
            "digest": format!("sha256:{}", "b".repeat(64)),
            "sha": sha,
            "create_upstream": true,
        })
        .to_string();
        let response = server.request("POST", "/v1/review/push", Some(&body));
        assert_eq!(status_of(&response), 200, "{response}");
        assert_eq!(data_of(&response)["status"], json!("pushed"));
        assert_eq!(
            actions.calls(),
            vec![format!(
                "push repo=/tmp/worktree digest=sha256:{} sha={} create=true",
                "b".repeat(64),
                "2".repeat(40)
            )]
        );

        // The camelCase alias is the same field.
        let aliased = json!({
            "repo": "/tmp/worktree",
            "digest": format!("sha256:{}", "b".repeat(64)),
            "sha": "2".repeat(40),
            "createUpstream": false,
        })
        .to_string();
        let camel = server.request("POST", "/v1/review/push", Some(&aliased));
        assert_eq!(status_of(&camel), 200, "{camel}");
        assert!(actions.calls()[1].ends_with("create=false"), "{:?}", actions.calls());

        // Missing sha is a body contract error, never a default.
        let missing = server.request(
            "POST",
            "/v1/review/push",
            Some(&json!({"repo": "/tmp", "digest": "x"}).to_string()),
        );
        assert_eq!(status_of(&missing), 400, "{missing}");
        assert_eq!(code_of(&missing), "invalid_json");
    }

    #[test]
    fn every_scripted_route_answers_with_the_token() {
        let repository = temp_repo();
        let repository = repository.canonicalize().unwrap();
        let actions = Arc::new(FakeActions::returning(vec![json!({
            "schema": "simplicio.goal-report/v1",
            "goal": {"status": "open"},
        })]));
        let server = Server::start(Arc::clone(&actions) as Arc<dyn ScriptedActions>);

        let run = server.request("GET", "/v1/run?selector=id:run-7", None);
        assert_eq!(status_of(&run), 200, "{run}");
        assert_eq!(data_of(&run)["goal_id"], json!("run-7"));

        let diff = server.request(
            "GET",
            &format!(
                "/v1/diff?selector=path:{}",
                query_value(&repository.to_string_lossy())
            ),
            None,
        );
        assert_eq!(status_of(&diff), 200, "{diff}");
        assert_eq!(data_of(&diff)["group"], json!("diff"));

        let receipt = server.request("GET", "/v1/receipt?selector=id:rc-1", None);
        assert_eq!(status_of(&receipt), 200, "{receipt}");
        assert_eq!(data_of(&receipt)["run_id"], json!("rc-1"));

        let report = server.request("GET", "/v1/report?selector=id:run-7", None);
        assert_eq!(status_of(&report), 200, "{report}");
        assert_eq!(data_of(&report)["run_id"], json!("run-7"));

        assert_eq!(
            actions.calls(),
            vec![
                "run repo=- id=run-7".to_string(),
                format!("diff path={} base=-", repository.display()),
                "receipt rc-1".to_string(),
                "report repo=- id=run-7".to_string(),
            ]
        );
    }

    #[test]
    fn run_reads_the_goal_report_for_each_selector_kind() {
        let repository = temp_repo();
        let repository = repository.canonicalize().unwrap();
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));

        let by_id = server.request("GET", "/v1/run?selector=id:run-7&repo=/tmp", None);
        let data = data_of(&by_id);
        assert_eq!(data["schema"], json!(RUN_SCHEMA));
        assert_eq!(data["action"], json!("open"));
        assert_eq!(data["goal_id"], json!("run-7"));
        assert_eq!(data["repo"], json!("/tmp"));
        assert!(data["wait"].is_null());
        assert_eq!(
            data["selector"],
            json!({"raw": "id:run-7", "kind": "id", "value": "run-7"})
        );

        let by_path = server.request(
            "GET",
            &format!(
                "/v1/run?selector=path:{}",
                query_value(&repository.to_string_lossy())
            ),
            None,
        );
        assert_eq!(status_of(&by_path), 200, "{by_path}");
        assert_eq!(data_of(&by_path)["goal_id"], Value::Null);
        assert_eq!(
            data_of(&by_path)["repo"],
            json!(repository.display().to_string())
        );
    }

    #[test]
    fn run_wait_idle_polls_until_the_run_is_idle() {
        let server = Server::start(Arc::new(FakeActions::returning(vec![
            json!({"goal": {"status": "open"}}),
            json!({"goal": {"status": "complete"}}),
        ])));
        let response = server.request("GET", "/v1/run?selector=id:run-7&wait=idle", None);
        assert_eq!(status_of(&response), 200, "{response}");
        let data = data_of(&response);
        assert_eq!(data["action"], json!("wait"));
        assert_eq!(data["wait"]["for"], json!("idle"));
        assert_eq!(data["wait"]["outcome"], json!("idle"));
        assert_eq!(data["wait"]["attempts"], json!(2));
    }

    #[test]
    fn run_wait_idle_gives_up_with_a_reported_timeout() {
        let server = Server::start(Arc::new(FakeActions::returning(vec![
            json!({"goal": {"status": "open"}}),
        ])));
        let response = server.request("GET", "/v1/run?selector=id:run-7&wait=idle", None);
        assert_eq!(status_of(&response), 200, "{response}");
        let data = data_of(&response);
        assert_eq!(data["wait"]["outcome"], json!("timeout"));
        assert_eq!(data["wait"]["attempts"], json!(wait_policy().attempts));
        assert_eq!(
            data["run"]["goal"]["status"],
            json!("open"),
            "a timeout still returns the last document"
        );
    }

    #[test]
    fn selectors_are_required_and_validated_on_every_scripted_route() {
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        for path in ["/v1/run", "/v1/diff", "/v1/receipt"] {
            let response = server.request("GET", path, None);
            assert_eq!(status_of(&response), 400, "{path}: {response}");
            assert_eq!(code_of(&response), "selector_required", "{path}");
        }
        for bad in ["main", "branch:main", "id:", "issue:x", "id:a%20b"] {
            for path in ["/v1/run", "/v1/diff", "/v1/receipt", "/v1/report"] {
                let response = server.request("GET", &format!("{path}?selector={bad}"), None);
                assert_eq!(status_of(&response), 400, "{path} {bad}: {response}");
                let code = code_of(&response);
                assert!(
                    matches!(code.as_str(), "invalid_selector" | "repo_path_invalid"),
                    "{path} {bad}: {code}"
                );
            }
        }
    }

    #[test]
    fn issue_and_id_selectors_resolve_worktrees_or_fail_closed() {
        let repository = temp_repo();
        let repository = repository.canonicalize().unwrap();
        let name = repository
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        let repo = query_value(&repository.to_string_lossy());

        let missing = server.request(
            "GET",
            &format!("/v1/diff?repo={repo}&selector=issue:439"),
            None,
        );
        assert_eq!(status_of(&missing), 404, "{missing}");
        assert_eq!(code_of(&missing), "worktree_not_found");

        let zero = server.request(
            "GET",
            &format!("/v1/diff?repo={repo}&selector=issue:0"),
            None,
        );
        assert_eq!(status_of(&zero), 400, "{zero}");
        assert_eq!(code_of(&zero), "issue_invalid");

        // The repository itself is a worktree of its own list, matched by name.
        let by_id = server.request(
            "GET",
            &format!("/v1/diff?repo={repo}&selector=id:{name}"),
            None,
        );
        assert_eq!(status_of(&by_id), 200, "{by_id}");
        assert_eq!(
            data_of(&by_id)["path"],
            json!(repository.display().to_string())
        );
    }

    #[test]
    fn diff_rejects_paths_that_are_not_directories_and_bad_bases() {
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        let missing = server.request("GET", "/v1/diff?selector=path:/does/not/exist", None);
        assert_eq!(status_of(&missing), 400, "{missing}");
        assert_eq!(code_of(&missing), "repo_path_invalid");
        let base = server.request("GET", "/v1/diff?selector=path:/tmp&base=--evil", None);
        assert_eq!(status_of(&base), 400, "{base}");
        assert_eq!(code_of(&base), "review_base_invalid");
    }

    #[test]
    fn receipt_requires_an_id_selector() {
        let repository = temp_repo();
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        for selector in [
            format!("path:{}", repository.display()),
            "issue:439".to_string(),
        ] {
            let response = server.request(
                "GET",
                &format!("/v1/receipt?selector={}", query_value(&selector)),
                None,
            );
            assert_eq!(status_of(&response), 400, "{selector}: {response}");
            assert_eq!(code_of(&response), "selector_kind_unsupported");
        }
    }

    #[test]
    fn post_run_accepts_a_json_body_and_rejects_ambiguous_input() {
        let server = Server::start(Arc::new(FakeActions::returning(vec![json!({
            "goal": {"status": "complete"},
        })])));
        let accepted = server.request(
            "POST",
            "/v1/run",
            Some(r#"{"selector":"id:run-7","wait":"idle"}"#),
        );
        assert_eq!(status_of(&accepted), 200, "{accepted}");
        assert_eq!(data_of(&accepted)["action"], json!("wait"));
        assert_eq!(data_of(&accepted)["wait"]["outcome"], json!("idle"));

        let ambiguous = server.request(
            "POST",
            "/v1/run?selector=id:run-7",
            Some(r#"{"selector":"id:run-7"}"#),
        );
        assert_eq!(status_of(&ambiguous), 400, "{ambiguous}");
        assert_eq!(code_of(&ambiguous), "invalid_query");

        let unknown = server.request(
            "POST",
            "/v1/run",
            Some(r#"{"selector":"id:run-7","bogus":1}"#),
        );
        assert_eq!(status_of(&unknown), 400, "{unknown}");
        assert_eq!(code_of(&unknown), "invalid_json");

        let empty = server.request("POST", "/v1/run", None);
        assert_eq!(status_of(&empty), 400, "{empty}");

        let wrong_wait = server.request("GET", "/v1/run?selector=id:x&wait=done", None);
        assert_eq!(status_of(&wrong_wait), 400, "{wrong_wait}");
        assert_eq!(code_of(&wrong_wait), "invalid_query");
    }

    #[test]
    fn path_selectors_reject_a_redundant_repo_on_every_scripted_route() {
        let repository = temp_repo();
        let repository = query_value(&repository.to_string_lossy());
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        for path in ["/v1/run", "/v1/diff", "/v1/report"] {
            let response = server.request(
                "GET",
                &format!("{path}?selector=path:{repository}&repo={repository}"),
                None,
            );
            assert_eq!(status_of(&response), 400, "{path}: {response}");
            assert_eq!(code_of(&response), "invalid_query", "{path}");
        }
    }

    #[test]
    fn report_accepts_a_run_id_with_a_repository_filter() {
        let server = Server::start(Arc::new(FakeActions::returning(Vec::new())));
        let filtered = server.request("GET", "/v1/report?selector=id:run-7&repo=/tmp", None);
        assert_eq!(status_of(&filtered), 200, "{filtered}");
        assert_eq!(data_of(&filtered)["repo"], json!("/tmp"));
        assert_eq!(data_of(&filtered)["run_id"], json!("run-7"));
        // The pre-selector contract still answers.
        let plain = server.request("GET", "/v1/report?repo=/tmp", None);
        assert_eq!(status_of(&plain), 200, "{plain}");
        assert_eq!(data_of(&plain)["repo"], json!("/tmp"));
    }

    #[test]
    fn diff_snapshot_quotes_the_repository_diff_locally() {
        let repository = temp_repo();
        let repository = repository.canonicalize().unwrap();
        let document = crate::diff_snapshot(&repository, None).unwrap();
        assert_eq!(document["schema"], json!(crate::DIFF_SCHEMA));
        assert_eq!(document["path"], json!(repository.display().to_string()));
        assert_eq!(document["truncated"], json!(false));
        assert_eq!(document["redacted"], json!(true));
        let diff = document["diff"].as_str().unwrap();
        assert!(diff.contains("+two"), "{diff}");
        assert!(document["digest"].as_str().unwrap().starts_with("sha256:"));
    }

    #[test]
    fn worktree_lookup_matches_branch_and_directory_names() {
        let repository = temp_repo();
        let repository = repository.canonicalize().unwrap();
        let name = repository
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();
        assert_eq!(
            crate::worktree_path_for(&repository.to_string_lossy(), &name),
            Ok(repository.display().to_string())
        );
        assert_eq!(
            crate::worktree_path_for(&repository.to_string_lossy(), "missing"),
            Err("worktree_not_found".to_string())
        );
        assert_eq!(
            crate::worktree_path_for(&repository.to_string_lossy(), "../escape"),
            Err("worktree_not_found".to_string())
        );
    }

    #[test]
    fn error_codes_map_to_stable_statuses() {
        for code in [
            "invalid_selector",
            "selector_required",
            "selector_kind_unsupported",
            "issue_invalid",
        ] {
            assert_eq!(error_status(code), 400, "{code}");
        }
        assert_eq!(error_status("worktree_not_found"), 404);
        for code in [
            "run_unavailable",
            "receipt_unavailable",
            "execution_report_unavailable",
            "desktop_access_unverified",
        ] {
            assert_eq!(error_status(code), 503, "{code}");
        }
    }
}
