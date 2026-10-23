//! Authorized pause/resume of one worker on one allowlisted remote runtime.
//!
//! The only remote effect this Desktop can send. It is deliberately narrow:
//! one worker, two actions (`pause`, `resume`), one bounded `POST`, no retry and
//! no client-side receipt. The receipt id in the answer belongs to the Runtime,
//! exactly the one its event stream puts in the activity timeline.
//!
//! Fail-closed rules:
//! - the machine must be in `~/.simplicio/desktop-remotes.json`;
//! - the token comes from the machine's `token_env` and is resolved in-process;
//!   without it no request is sent (`fleet_steer_unauthorized`);
//! - `401`/`403` is `fleet_steer_unauthorized`, other statuses are
//!   `fleet_steer_remote_error`, and a `2xx` without a receipt is
//!   `fleet_steer_receipt_missing` — never a success.
use crate::remote_fleet::{self, Remote};
use serde_json::{json, Value};
use std::{
    env,
    io::Read,
    time::{Duration, Instant},
};

const STEER_SCHEMA: &str = "simplicio.desktop-fleet-steer/v1";
const MAX_RESPONSE_BYTES: u64 = 16_384;
const MAX_LATENCY_MS: u64 = 60_000;
const TIMEOUT: Duration = Duration::from_secs(3);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum Action {
    Pause,
    Resume,
}

impl Action {
    pub(crate) fn parse(value: &str) -> Result<Self, String> {
        match value {
            "pause" => Ok(Self::Pause),
            "resume" => Ok(Self::Resume),
            _ => Err("fleet_steer_action_invalid".into()),
        }
    }

    fn path(self) -> &'static str {
        match self {
            Self::Pause => "pause",
            Self::Resume => "resume",
        }
    }

    fn label(self) -> &'static str {
        self.path()
    }
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

/// The token for one remote, resolved from the environment inside the native
/// process. It is never persisted, logged or returned over IPC.
fn resolve_token(remote: &Remote) -> Result<String, String> {
    let name = remote
        .token_env
        .as_deref()
        // A tokenless machine can never be acted on: loopback without `token_env`
        // is readable but not steerable.
        .ok_or("fleet_steer_unauthorized")?;
    match env::var(name) {
        Ok(value)
            if !value.trim().is_empty()
                && value.len() <= 4_096
                && !value.chars().any(char::is_control) =>
        {
            Ok(value)
        }
        _ => Err("fleet_steer_unauthorized".into()),
    }
}

fn read_bounded(reader: impl Read) -> Result<Vec<u8>, String> {
    let mut bytes = Vec::new();
    reader
        .take(MAX_RESPONSE_BYTES + 1)
        .read_to_end(&mut bytes)
        .map_err(|_| "fleet_steer_remote_error".to_string())?;
    if bytes.len() as u64 > MAX_RESPONSE_BYTES {
        return Err("fleet_steer_remote_error".into());
    }
    Ok(bytes)
}

/// Strict response parser. `receipt_id` (or `receiptId`) is mandatory and
/// bounded; a response that does not echo the worker, when it echoes anything,
/// is rejected instead of trusted.
pub(crate) fn parse_response(body: &[u8], worker_id: &str) -> Result<String, String> {
    let value: Value = serde_json::from_slice(body).map_err(|_| "fleet_steer_response_invalid")?;
    let object = value.as_object().ok_or("fleet_steer_response_invalid")?;
    let echo = object
        .get("worker_id")
        .or_else(|| object.get("workerId"))
        .and_then(Value::as_str);
    if echo.is_some_and(|echo| echo != worker_id) {
        return Err("fleet_steer_response_mismatch".into());
    }
    let receipt = object
        .get("receipt_id")
        .or_else(|| object.get("receiptId"))
        .and_then(Value::as_str)
        .ok_or("fleet_steer_receipt_missing")?;
    if !remote_fleet::valid_receipt_id(receipt) {
        return Err("fleet_steer_receipt_missing".into());
    }
    Ok(receipt.to_string())
}

/// One bounded `POST <url>/v1/workers/<worker>/<action>`. `token` is optional
/// only so the API test can prove the remote rejects an unauthenticated call;
/// production always passes the resolved token, and `None` still fails closed
/// with `fleet_steer_unauthorized` — it never produces a receipt.
pub(crate) fn post_steer(
    base_url: &str,
    token: Option<&str>,
    worker_id: &str,
    action: Action,
) -> Result<(u16, Vec<u8>), String> {
    if !valid_worker_id(worker_id) {
        return Err("fleet_steer_worker_invalid".into());
    }
    let client = reqwest::blocking::Client::builder()
        .timeout(TIMEOUT)
        .redirect(reqwest::redirect::Policy::none())
        .build()
        .map_err(|_| "fleet_steer_remote_error".to_string())?;
    let mut request = client
        .post(format!(
            "{}/v1/workers/{}/{}",
            base_url.trim_end_matches('/'),
            url_encode(worker_id),
            action.path()
        ))
        .header("Accept", "application/json")
        .header("Content-Length", "0");
    if let Some(token) = token {
        request = request.bearer_auth(token);
    }
    let response = match request.send() {
        Ok(response) => response,
        Err(_) => return Err("fleet_steer_unreachable".into()),
    };
    let status = response.status().as_u16();
    let body = read_bounded(response).unwrap_or_default();
    Ok((status, body))
}

/// Percent-encodes the characters a worker id may contain that are not
/// URL-path safe. Ids are validated first, so this is belt and braces.
fn url_encode(value: &str) -> String {
    let mut encoded = String::with_capacity(value.len());
    for byte in value.bytes() {
        match byte {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'.' | b'_' | b'-' => {
                encoded.push(byte as char)
            }
            b':' => encoded.push_str("%3A"),
            other => encoded.push_str(&format!("%{other:02X}")),
        }
    }
    encoded
}

/// Maps an HTTP observation to a receipt or a stable error. Split from the
/// transport so the authorization rule is testable without a socket.
pub(crate) fn interpret(status: u16, body: &[u8], worker_id: &str) -> Result<String, String> {
    if matches!(status, 401 | 403) {
        return Err("fleet_steer_unauthorized".into());
    }
    if !(200..300).contains(&status) {
        return Err("fleet_steer_remote_error".into());
    }
    parse_response(body, worker_id)
}

/// Full steer call: allowlist entry in, Runtime receipt out.
pub(crate) fn steer(remote: &Remote, worker_id: &str, action: Action) -> Result<Value, String> {
    if !valid_worker_id(worker_id) {
        return Err("fleet_steer_worker_invalid".into());
    }
    let token = resolve_token(remote)?;
    let started = Instant::now();
    let (status, body) = post_steer(&remote.base_url, Some(token.as_str()), worker_id, action)?;
    let receipt_id = interpret(status, &body, worker_id)?;
    Ok(json!({
        "schema": STEER_SCHEMA,
        "machineId": remote.id,
        "workerId": worker_id,
        "action": action.label(),
        "receiptId": receipt_id,
        "status": "sent",
        "latencyMs": started.elapsed().as_millis().min(MAX_LATENCY_MS as u128) as u64,
    }))
}

/// Entry point used by the Tauri command: resolves the machine from the local
/// allowlist and never accepts a URL or a token from the WebView.
pub(crate) fn steer_machine(
    machine_id: &str,
    worker_id: &str,
    action: &str,
) -> Result<Value, String> {
    let action = Action::parse(action)?;
    let home = remote_fleet::default_home().ok_or("remote_fleet_home_unavailable")?;
    let remote = remote_fleet::find_remote(&home, machine_id)?;
    steer(&remote, worker_id, action)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        io::{Read, Write},
        net::TcpListener,
        thread::JoinHandle,
    };

    struct MockServer {
        base_url: String,
        handle: JoinHandle<String>,
    }

    impl MockServer {
        fn join(self) -> String {
            self.handle.join().unwrap_or_default()
        }
    }

    /// One-request loopback server. `require_auth` makes it answer `401` when
    /// the request carries no `Authorization: Bearer` header, which is exactly
    /// the rule the remote runtime enforces.
    fn mock_server(status: u16, body: &'static str, require_auth: bool) -> MockServer {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind loopback");
        let port = listener.local_addr().expect("local addr").port();
        let handle = std::thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0_u8; 8_192];
            let read = stream.read(&mut buffer).unwrap_or(0);
            let request = String::from_utf8_lossy(&buffer[..read]).to_string();
            let authorized = request
                .to_ascii_lowercase()
                .contains("authorization: bearer ");
            let (line, payload) = if require_auth && !authorized {
                ("HTTP/1.1 401 Unauthorized", "{\"error\":\"unauthorized\"}")
            } else {
                let line = if status == 200 {
                    "HTTP/1.1 200 OK"
                } else {
                    "HTTP/1.1 500 Internal Server Error"
                };
                (line, body)
            };
            let response = format!(
                "{line}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{payload}",
                payload.len()
            );
            let _ = stream.write_all(response.as_bytes());
            let _ = stream.flush();
            request
        });
        MockServer {
            base_url: format!("http://127.0.0.1:{port}"),
            handle,
        }
    }

    fn remote(token_env: Option<&str>, base_url: &str) -> Remote {
        Remote {
            id: "studio".into(),
            label: "Studio".into(),
            base_url: base_url.to_string(),
            token_env: token_env.map(str::to_string),
        }
    }

    #[test]
    fn rejects_an_unauthenticated_call_at_the_api() {
        let server = mock_server(
            200,
            "{\"worker_id\":\"w-1\",\"receipt_id\":\"rcpt-1\"}",
            true,
        );
        let (status, body) = post_steer(&server.base_url, None, "w-1", Action::Pause).unwrap();
        let request = server.join();
        assert_eq!(status, 401, "the remote must answer 401 without a token");
        assert_eq!(
            interpret(status, &body, "w-1").unwrap_err(),
            "fleet_steer_unauthorized"
        );
        assert!(
            request.starts_with("POST /v1/workers/w-1/pause "),
            "{request}"
        );
        assert!(!request.to_ascii_lowercase().contains("authorization:"));
    }

    #[test]
    fn sends_an_authenticated_pause_and_returns_the_runtime_receipt() {
        let server = mock_server(
            200,
            "{\"worker_id\":\"w-1\",\"receipt_id\":\"rcpt-9f2\"}",
            true,
        );
        let (status, body) =
            post_steer(&server.base_url, Some("token-abc"), "w-1", Action::Pause).unwrap();
        let request = server.join().to_ascii_lowercase();
        assert!(
            request.contains("authorization: bearer token-abc"),
            "{request}"
        );
        assert!(
            request.starts_with("post /v1/workers/w-1/pause "),
            "{request}"
        );
        assert_eq!(interpret(status, &body, "w-1").unwrap(), "rcpt-9f2");
    }

    #[test]
    fn resume_uses_the_resume_path_only() {
        let server = mock_server(200, "{\"receipt_id\":\"rcpt-r\"}", true);
        let (status, _body) =
            post_steer(&server.base_url, Some("token-abc"), "w-1", Action::Resume).unwrap();
        let request = server.join();
        assert_eq!(status, 200);
        assert!(
            request.starts_with("POST /v1/workers/w-1/resume "),
            "{request}"
        );
    }

    #[test]
    fn refuses_to_send_when_no_token_can_be_resolved() {
        // No `token_env`: loopback can be read but never steered.
        let tokenless = remote(None, "http://127.0.0.1:1");
        assert_eq!(
            steer(&tokenless, "w-1", Action::Pause).unwrap_err(),
            "fleet_steer_unauthorized"
        );
        // A named variable that is absent fails closed before any request.
        let unset = remote(
            Some("SIMPLICIO_TEST_ABSENT_TOKEN_468"),
            "http://127.0.0.1:1",
        );
        assert_eq!(
            steer(&unset, "w-1", Action::Pause).unwrap_err(),
            "fleet_steer_unauthorized"
        );
    }

    #[test]
    fn rejects_a_2xx_without_a_receipt_or_with_a_foreign_receipt() {
        assert_eq!(
            interpret(200, b"{\"status\":\"ok\"}", "w-1").unwrap_err(),
            "fleet_steer_receipt_missing"
        );
        assert_eq!(
            interpret(200, b"{\"receipt_id\":\"\"}", "w-1").unwrap_err(),
            "fleet_steer_receipt_missing"
        );
        assert_eq!(
            interpret(200, b"not-json", "w-1").unwrap_err(),
            "fleet_steer_response_invalid"
        );
        assert_eq!(
            interpret(
                200,
                b"{\"worker_id\":\"w-2\",\"receipt_id\":\"r-1\"}",
                "w-1"
            )
            .unwrap_err(),
            "fleet_steer_response_mismatch"
        );
    }

    #[test]
    fn maps_remote_failures_instead_of_inventing_success() {
        assert_eq!(
            interpret(403, b"", "w-1").unwrap_err(),
            "fleet_steer_unauthorized"
        );
        assert_eq!(
            interpret(500, b"{\"receipt_id\":\"r-1\"}", "w-1").unwrap_err(),
            "fleet_steer_remote_error"
        );
    }

    #[test]
    fn accepts_only_pause_and_resume_for_a_bounded_worker_id() {
        assert_eq!(Action::parse("pause").unwrap(), Action::Pause);
        assert_eq!(Action::parse("resume").unwrap(), Action::Resume);
        assert_eq!(
            Action::parse("delete").unwrap_err(),
            "fleet_steer_action_invalid"
        );
        let remote = remote(
            Some("SIMPLICIO_TEST_ABSENT_TOKEN_468"),
            "http://127.0.0.1:1",
        );
        for worker in ["", "w/../escape", "w 1", "w-1\u{7f}"] {
            assert_eq!(
                steer(&remote, worker, Action::Pause).unwrap_err(),
                "fleet_steer_worker_invalid",
                "worker {worker:?} must be refused"
            );
        }
    }

    #[test]
    fn url_encoding_keeps_ids_in_one_path_segment() {
        assert_eq!(url_encode("w-1.a_b:c"), "w-1.a_b%3Ac");
        // `/` can never split the path: ids with a slash fail validation first.
        assert_eq!(url_encode("../admin"), "..%2Fadmin");
    }
}
