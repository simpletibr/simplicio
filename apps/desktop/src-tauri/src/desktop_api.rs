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
        .spawn(move || serve(listener, token, server_info, server_shutdown))
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

fn serve(listener: TcpListener, token: String, info: ApiInfo, shutdown: Arc<AtomicBool>) {
    let _ = listener.set_nonblocking(true);
    let (sender, receiver) = mpsc::sync_channel::<TcpStream>(WORKERS * 8);
    let receiver = Arc::new(Mutex::new(receiver));
    let mut workers = Vec::with_capacity(WORKERS);

    for _ in 0..WORKERS {
        let receiver = Arc::clone(&receiver);
        let token = token.clone();
        let info = info.clone();
        workers.push(std::thread::spawn(move || loop {
            let next = {
                let guard = match receiver.lock() {
                    Ok(guard) => guard,
                    Err(_) => break,
                };
                guard.recv()
            };
            match next {
                Ok(mut stream) => handle_connection(&mut stream, &token, &info),
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

fn handle_connection(stream: &mut TcpStream, token: &str, info: &ApiInfo) {
    let _ = stream.set_read_timeout(Some(REQUEST_TIMEOUT));
    let _ = stream.set_write_timeout(Some(REQUEST_TIMEOUT));
    let (status, body) = match read_request(stream) {
        Ok(request) => dispatch(request, token, info),
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

fn dispatch(request: Request, token: &str, info: &ApiInfo) -> (u16, Value) {
    if let Err(failure) = authorize(&request.headers, token) {
        return failure.response();
    }

    let target = match parse_target(&request.target) {
        Ok(target) => target,
        Err(failure) => return (failure.status(), failure.body()),
    };

    let allowed = match target.path.as_str() {
        "/v1/report" => &["repo"][..],
        "/v1/review" => &["repo", "base"][..],
        "/v1/worktrees" | "/v1/worktree" => &["repo"][..],
        _ => &[][..],
    };
    if target
        .query
        .keys()
        .any(|key| !allowed.contains(&key.as_str()))
    {
        return (400, error_body("invalid_query"));
    }

    let path = target.path.as_str();
    match (request.method.as_str(), path) {
        ("GET", "/v1/health") => (200, ok_body(health_data(info))),
        ("GET", "/v1/snapshot") => result_body(crate::snapshot_from_runtime()),
        ("GET", "/v1/report") => result_body(crate::execution_report_from(
            target.query.get("repo").map(String::as_str),
            None,
        )),
        ("GET", "/v1/review") => result_body(review_data(
            target.query.get("repo").map(String::as_str),
            target.query.get("base").map(String::as_str),
        )),
        ("GET", "/v1/worktrees") => {
            result_body(worktrees_data(target.query.get("repo").map(String::as_str)))
        }
        ("POST", "/v1/worktree") => result_body(worktree_data(
            &request.body,
            target.query.get("repo").map(String::as_str),
        )),
        _ if known_route(path) => (405, error_body("method_not_allowed")),
        _ => (404, error_body("not_found")),
    }
}

fn known_route(path: &str) -> bool {
    matches!(
        path,
        "/v1/health"
            | "/v1/snapshot"
            | "/v1/report"
            | "/v1/review"
            | "/v1/worktrees"
            | "/v1/worktree"
    )
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
        "invalid_json" | "invalid_query" | "invalid_repo" | "repo_path_invalid"
        | "issue_invalid" | "agent_invalid" => 400,
        "desktop_access_not_active" => 403,
        "wip_limit_reached" | "worktree_exists" | "worktree_path_invalid" => 409,
        _ if code.starts_with("runtime_")
            || code.ends_with("_unavailable")
            || code.ends_with("_failed") =>
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
        let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let token = generate_token().unwrap();
        let info = ApiInfo::new(port);
        let shutdown = Arc::new(AtomicBool::new(false));
        let server_shutdown = Arc::clone(&shutdown);
        let server_token = token.clone();
        let server_info = info.clone();
        let handle =
            std::thread::spawn(move || serve(listener, server_token, server_info, server_shutdown));

        let missing = http_request(
            port,
            "GET /v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n",
        );
        assert!(missing.starts_with("HTTP/1.1 401"), "{missing}");
        assert!(missing.contains(RESPONSE_SCHEMA));
        assert!(missing.contains("unauthorized"));

        let wrong = http_request(
            port,
            &format!(
                "GET /v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {}\r\nConnection: close\r\n\r\n",
                "0".repeat(TOKEN_BYTES * 2)
            ),
        );
        assert!(wrong.starts_with("HTTP/1.1 403"), "{wrong}");
        assert!(wrong.contains("forbidden"));

        let accepted = http_request(
            port,
            &format!(
                "GET /v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {token}\r\nConnection: close\r\n\r\n"
            ),
        );
        assert!(accepted.starts_with("HTTP/1.1 200"), "{accepted}");
        assert!(accepted.contains(RESPONSE_SCHEMA));
        assert!(accepted.contains("\"status\":\"ok\""));
        assert!(!accepted.contains(&token));

        shutdown.store(true, Ordering::SeqCst);
        handle.join().unwrap();
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
}
