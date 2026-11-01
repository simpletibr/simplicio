#!/usr/bin/env python3
"""Benchmark: create then edit an HTML user listing, with/without Simplicio MCP.

Measures, per phase (create, edit) and per condition:
  wall time, child CPU time, peak RSS, per-request p50/p99 latency,
  input/output/reasoning/cache tokens, total cost.

Conditions:
  no-mcp            -> native OpenCode tools only
  simplicio-3.9.2   -> Simplicio MCP from the isolated 3.9.2 sandbox
  simplicio-3.10.2  -> Simplicio MCP from the isolated 3.10.2 sandbox
  simplicio-3.10.7  -> Simplicio MCP from the isolated 3.10.7 sandbox
  simplicio-candidate -> Simplicio MCP from the binary named by run_candidate.sh
  proto             -> proto_mcp.py, a design probe of the flow, not a Simplicio version

Usage (every round writes to its own --out folder, so earlier results stay intact):
  python3 bench.py --reps 5 --out artifacts-<date>
  python3 bench.py --reps 1 --conditions no-mcp --out artifacts-<date>-smoke
  python3 bench.py --reps 5 --model opencode/deepseek-v4.1-flash-free --out artifacts-<date>-free

A provider usage limit stops the run with exit code 3; the session that hit it is not saved.
Sandboxes read the host login through SIMPLICIO_AUTH_FILE (see run.sh); nothing copies it.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import shutil
import socket
import sqlite3
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import check_page

ROOT = Path(__file__).resolve().parent
STATE = Path(os.environ.get("BENCH_STATE") or Path(tempfile.gettempdir()) / "opencode" / "bench-state")
SANDBOX = Path(os.environ.get("BENCH_SANDBOX") or Path.home() / "Projetos/ai/sandbox-simplicio-mcp")
OPENCODE = shutil.which("opencode") or os.path.expanduser("~/.opencode/bin/opencode")
DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
MODEL = "opencode-go/deepseek-v4.1-flash"
OPENROUTER_PREFIX = "openrouter/"
# One endpoint for every session: OpenRouter would otherwise route each request to the cheapest
# host, and the comparison would change host between conditions. Cloudflare passes the account's
# no-training guardrail, and its output and cache prices match the table in flow.py.
# One fixed endpoint per model, so sessions of a model stay comparable. Each was pinged on 2026-11-01.
OPENROUTER_ENDPOINTS = {
    "anthropic/claude-haiku-5.5": "google-vertex/global",
    "anthropic/claude-sonnet-5.5": "google-vertex/global",
    "deepseek/deepseek-v4.1-flash-1017": "cloudflare",
    "meta/muse-glimmer-30b": "deepinfra/bf16",
    "meta/muse-spark-1.3": "meta",
    "openai/gpt-6-luna": "azure",
    "openai/gpt-6.1-terra": "azure/eu",
    "qwen/qwen3.8-27b": "primeintellect/fp8",
    "x-ai/grok-4.3": "xai/zdr",
    "x-ai/grok-4.7": "xai/zdr",
}
SERVER_PASSWORD = "bench-local"

CREATE_PROMPT = (
    "Crie o arquivo users.html na raiz deste projeto. Ele deve ser uma pagina HTML "
    "standalone, sem CDN e sem dependencias externas, que abre direto do disco (file://). "
    "Incorpore os dados de users.json no proprio HTML e renderize uma tabela com nome, "
    "email, papel, status e data de criacao. Inclua busca em tempo real por nome ou email "
    "e ordenacao por coluna ao clicar no cabecalho. Layout limpo e responsivo. "
    "Nao altere users.json. Ao terminar, responda apenas OK."
)

EDIT_PROMPT = (
    "Na mesma users.html, adicione um filtro por status com as opcoes todos, ativo e inativo, "
    "e um contador no formato 'X de Y usuarios' que respeite a busca e o filtro juntos. "
    "Preserve todo o comportamento existente, inclusive a ordenacao. Nao altere users.json. "
    "Ao terminar, responda apenas OK."
)

# A page task that took no part in building the generator: other data, other language.
CATALOG_CREATE_PROMPT = (
    "Create catalog.html in the project root. It must be a standalone HTML page, no CDN and no external "
    "dependencies, that opens directly from disk. Embed the data from products.json in the HTML and render "
    "a table with sku, name, category, price and stock. Add live search by name and column sorting when "
    "clicking a header. Keep the layout clean and responsive. Do not change products.json. When finished, "
    "reply only OK."
)

CATALOG_EDIT_PROMPT = (
    "In the same catalog.html, add a filter by category and a counter in the format 'X of Y products' that "
    "respects the search and the filter together. Keep all existing behavior, including sorting. Do not "
    "change products.json. When finished, reply only OK."
)

# Control task: no generator covers it, so it shows what the map hop costs when it cannot help.
CONTROL_CREATE_PROMPT = (
    "Crie o arquivo stats.py na raiz deste projeto: um script Python 3 sem dependencias externas que "
    "le users.json e imprime, em JSON, o total de usuarios e a contagem por papel, no formato "
    '{"total": N, "por_papel": {"Admin": N}}. Nao altere users.json. Ao terminar, responda apenas OK.'
)

CONTROL_EDIT_PROMPT = (
    "No mesmo stats.py, adicione uma opcao --status que limita a contagem aos usuarios com aquele "
    'status, e inclua no JSON a chave "status" com o valor usado, ou null sem a opcao. Preserve o '
    "comportamento existente. Nao altere users.json. Ao terminar, responda apenas OK."
)

ROLES = ["Admin", "Editor", "Viewer", "Analyst", "Support"]
STATUSES = ["ativo", "inativo"]
FIRST = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela", "Henrique",
         "Isabela", "Joao", "Karina", "Lucas", "Mariana", "Nicolas", "Olivia", "Paulo",
         "Queren", "Rafael", "Sofia", "Tiago", "Ursula", "Vitor", "Wesley", "Yara"]
LAST = ["Almeida", "Barbosa", "Costa", "Dias", "Esteves", "Ferreira", "Gomes", "Horta"]
USERS = []
for i, first in enumerate(FIRST):
    USERS.append({
        "id": i + 1,
        "nome": first + " " + LAST[i % len(LAST)],
        "email": first.lower() + "." + LAST[i % len(LAST)].lower() + "@example.com",
        "papel": ROLES[i % len(ROLES)],
        "status": STATUSES[i % len(STATUSES)],
        "criado_em": "2026-%02d-%02d" % ((i % 12) + 1, (i % 27) + 1),
    })


def server_command(condition: str) -> list | None:
    if condition == "proto":
        return ["/usr/bin/python3", str(ROOT / "proto_mcp.py")]
    if condition == "simplicio-candidate":
        return ["/bin/bash", str(ROOT / "run_candidate.sh")]
    if condition.startswith("simplicio-"):
        return ["/bin/bash", str(SANDBOX / "run.sh"), condition.split("-", 1)[1]]
    return None


CATEGORIES = ["Books", "Games", "Music"]
ADJECTIVES = ["Amber", "Brisk", "Cedar", "Dusty", "Early", "Fable", "Golden", "Hollow", "Ivory", "Jolly"]
NOUNS = ["Atlas", "Chess", "Violin"]
PRODUCTS = []
for i, adjective in enumerate(ADJECTIVES):
    for j, noun in enumerate(NOUNS):
        PRODUCTS.append({
            "sku": "SKU-%03d" % (len(PRODUCTS) + 1),
            "name": adjective + " " + noun,
            "category": CATEGORIES[j],
            "price": round(9.5 + 3.25 * (len(PRODUCTS) % 11), 2),
            "stock": (len(PRODUCTS) * 7) % 23,
        })


def condition_config(condition: str, model: str = MODEL) -> dict:
    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": model,
        "snapshots": False,
        "update": "notify",
        "mcp": {"servers": {}},
    }
    if model.startswith(OPENROUTER_PREFIX):
        name = model[len(OPENROUTER_PREFIX):]
        config["providers"] = {
            "openrouter": {
                "env": ["OPENROUTER_API_KEY"],
                "body": {"provider": {"order": [OPENROUTER_ENDPOINTS[name]], "allow_fallbacks": False}},
                "models": {name: {}},
            }
        }
    command = server_command(condition)
    if command:
        config["mcp"]["servers"]["simplicio"] = {
            "type": "local",
            "command": command,
            "timeout": {"startup": 45000, "catalog": 30000, "execution": 600000},
        }
    return config


def seed_work(work: Path, name: str = "users.json", rows: list = USERS) -> None:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (work / name).write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    (work / "README.md").write_text("# Listing benchmark\n\nSeed data: %s\n" % name)
    subprocess.run(["git", "init", "-q"], cwd=str(work), check=True)


class Sampler(threading.Thread):
    def __init__(self, pids: list):
        super().__init__(daemon=True)
        self.pids = pids
        self.peak_kb = 0
        self.stop = False
        self.samples = 0

    def _tree_kb(self) -> int:
        try:
            out = subprocess.run(
                ["ps", "-axo", "pid,ppid,rss"],
                capture_output=True, text=True, timeout=10,
            ).stdout
        except Exception:
            return 0
        rows = {}
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                pid, ppid, rss = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                continue
            rows[pid] = (ppid, rss)
        children = {}
        for pid, (ppid, _rss) in rows.items():
            children.setdefault(ppid, []).append(pid)
        stack = list(self.pids)
        seen = set()
        total = 0
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            total += rows.get(current, (0, 0))[1]
            stack.extend(children.get(current, []))
        return total

    def run(self) -> None:
        while not self.stop:
            self.peak_kb = max(self.peak_kb, self._tree_kb())
            self.samples += 1
            time.sleep(0.25)


QUOTA_ERRORS = {"provider.quota", "provider.free-limit"}


class QuotaExhausted(RuntimeError):
    """The provider's usage limit is spent; the next session would fail the same way."""

    def __init__(self, where: str, retry_ms: int | None = None):
        super().__init__(where)
        self.retry_ms = retry_ms


def quota_exhausted(stdout: str) -> bool:
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "error" and (event.get("error") or {}).get("type") in QUOTA_ERRORS:
            return True
    return False


def session_env(work: Path, config_dir: Path) -> dict:
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = str(config_dir)
    env["PWD"] = str(work)
    env["INIT_CWD"] = str(work)
    env["OPENCODE_PASSWORD"] = SERVER_PASSWORD
    return env


class OpencodeServer:
    """One private server per session, so the MCP server stays connected across both phases.

    `opencode run --standalone` per phase restarts the MCP server between the prompts: the second
    prompt then reaches the model before the catalog is back, which a real session never does.
    """

    def __init__(self, work: Path, config_dir: Path, needs_mcp: bool):
        self.work = work
        self.env = session_env(work, config_dir)
        self.needs_mcp = needs_mcp
        config_dir.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        self.url = "http://127.0.0.1:%d" % port
        self.proc = subprocess.Popen(
            [OPENCODE, "serve", "--hostname", "127.0.0.1", "--port", str(port)],
            cwd=str(self.work), env=self.env,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.wait_ready()
        return self

    def __exit__(self, *_exc):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()

    def mcp_status(self) -> dict | None:
        done = subprocess.run(
            [OPENCODE, "api", "--server", self.url, "-H", "x-opencode-directory:%s" % self.work, "mcp.list"],
            cwd=str(self.work), env=self.env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20,
        )
        try:
            servers = json.loads(done.stdout)["data"]
        except (ValueError, KeyError, TypeError):
            return None
        return {server["name"]: server["status"]["status"] for server in servers}

    def wait_ready(self, limit_s: float = 30.0) -> None:
        deadline = time.monotonic() + limit_s
        statuses = None
        while time.monotonic() < deadline:
            statuses = self.mcp_status()
            if statuses and "pending" not in statuses.values():
                if self.needs_mcp and statuses.get("simplicio") != "connected":
                    raise RuntimeError("MCP server not connected: %s" % statuses)
                return
            time.sleep(0.25)
        if self.needs_mcp and (statuses or {}).get("simplicio") != "connected":
            raise RuntimeError("MCP server not connected: %s" % statuses)


def retry_after_ms(stdout: str) -> int | None:
    """The wait the provider asked for in a limit error, in milliseconds."""
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        wait = (event.get("error") or {}).get("retryAfterMs") if event.get("type") == "error" else None
        if isinstance(wait, int):
            return wait
    return None


def run_phase(server: OpencodeServer, prompt: str, title: str, session: str | None, model: str = MODEL) -> dict:
    cmd = [
        OPENCODE, "run", "--server", server.url, "--format", "json",
        "--model", model, "--auto", "--title", title,
    ]
    if session:
        cmd.extend(["--session", session])
    cmd.append(prompt)

    started = time.monotonic()
    proc = subprocess.Popen(
        cmd, cwd=str(server.work), env=server.env,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    sampler = Sampler([proc.pid, server.proc.pid])
    sampler.start()
    try:
        stdout, stderr = proc.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    wall = time.monotonic() - started
    sampler.stop = True
    sampler.join(timeout=5)

    session_id = session
    if not session_id:
        for line in stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("sessionID"):
                session_id = event["sessionID"]
                break

    return {
        "exit": proc.returncode,
        "wall_s": round(wall, 3),
        "peak_rss_mb": round(sampler.peak_kb / 1024.0, 1),
        "session_id": session_id,
        "quota_exhausted": proc.returncode != 0 and quota_exhausted(stdout),
        "retry_after_ms": retry_after_ms(stdout),
        "stdout_tail": stdout[-1500:],
        "stderr_tail": stderr[-1500:],
    }


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * (p / 100.0)
    low = int(k)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (k - low)


def read_session(session_id: str, attempts: int = 20) -> dict:
    con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = None
    for _ in range(attempts):
        row = con.execute("select * from session_v2 where id=?", (session_id,)).fetchone()
        if row:
            break
        time.sleep(0.25)
    if not row:
        return {"error": "session not found", "create": [], "edit": [], "session": None}

    rows = list(con.execute(
        "select type, seq, data from session_message where session_id=? order by seq",
        (session_id,),
    ))
    users = [r for r in rows if r["type"] == "user"]
    split = users[1]["seq"] if len(users) >= 2 else None

    phases = {"create": [], "edit": []}
    for r in rows:
        if r["type"] != "assistant":
            continue
        try:
            data = json.loads(r["data"])
        except json.JSONDecodeError:
            continue
        timing = data.get("time") or {}
        created = timing.get("created")
        completed = timing.get("completed") or timing.get("streamed")
        latency = None
        if created and completed:
            latency = max(0.0, (completed - created) / 1000.0)
        record = {
            "seq": r["seq"],
            "latency_s": latency,
            "tokens": data.get("tokens") or {},
            "cost": data.get("cost") or 0.0,
        }
        key = "edit" if split is not None and r["seq"] > split else "create"
        phases[key].append(record)

    session = {
        "cost": row["cost"],
        "tokens_input": row["tokens_input"],
        "tokens_output": row["tokens_output"],
        "tokens_reasoning": row["tokens_reasoning"],
        "tokens_cache_read": row["tokens_cache_read"],
        "tokens_cache_write": row["tokens_cache_write"],
        "time_created": row["time_created"],
        "time_idle": row["time_idle"],
    }
    return {"error": None, "create": phases["create"], "edit": phases["edit"], "session": session}


def phase_metrics(records: list) -> dict:
    latencies = [r["latency_s"] for r in records if r["latency_s"] is not None]
    tokens = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    cost = 0.0
    for r in records:
        t = r["tokens"] or {}
        tokens["input"] += int(t.get("input") or 0)
        tokens["output"] += int(t.get("output") or 0)
        tokens["reasoning"] += int(t.get("reasoning") or 0)
        cache = t.get("cache") or {}
        tokens["cache_read"] += int(cache.get("read") or 0)
        tokens["cache_write"] += int(cache.get("write") or 0)
        cost += float(r["cost"] or 0)
    return {
        "requests": len(records),
        "p50_s": percentile(latencies, 50),
        "p99_s": percentile(latencies, 99),
        "latencies_s": latencies,
        "tokens": tokens,
        "cost": round(cost, 8),
    }


USERS_SPEC = check_page.PageSpec(
    values=[user["email"] for user in USERS], search_term="ana", sort_header="nome",
    filter_value="inativo", filter_rows=sum(user["status"] == "inativo" for user in USERS), connector="de",
)
CATALOG_SPEC = check_page.PageSpec(
    values=[product["sku"] for product in PRODUCTS], search_term="chess", sort_header="name",
    filter_value="Music", filter_rows=sum(product["category"] == "Music" for product in PRODUCTS), connector="of",
)


def validate_page(work: Path, page: str, spec: check_page.PageSpec, data: str, rows: list, edited: bool) -> dict:
    """Delivery check, after the phase's wall clock: the page must work and the data must not change."""
    result = check_page.check(work / page, spec, edited)
    result["data_intact"] = json.loads((work / data).read_text()) == rows
    result["ok"] = result["ok"] and result["data_intact"]
    return result


def validate(work: Path, edited: bool) -> dict:
    return validate_page(work, "users.html", USERS_SPEC, "users.json", USERS, edited)


def validate_catalog(work: Path, edited: bool) -> dict:
    return validate_page(work, "catalog.html", CATALOG_SPEC, "products.json", PRODUCTS, edited)


def run_stats(work: Path, *options: str) -> dict | None:
    try:
        done = subprocess.run(["python3", "stats.py", *options], cwd=str(work), stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=20)
        return json.loads(done.stdout)
    except (subprocess.TimeoutExpired, ValueError):
        return None


def validate_control(work: Path, edited: bool) -> dict:
    """The script must count correctly, and after the edit honour --status."""
    def counts(users: list) -> dict:
        roles: dict = {}
        for user in users:
            roles[user["papel"]] = roles.get(user["papel"], 0) + 1
        return roles

    full = run_stats(work) or {}
    result = {"exists": (work / "stats.py").exists(), "total": full.get("total")}
    ok = full.get("total") == len(USERS) and full.get("por_papel") == counts(USERS)
    if edited:
        inactive = [user for user in USERS if user["status"] == "inativo"]
        scoped = run_stats(work, "--status", "inativo") or {}
        result["scoped_total"] = scoped.get("total")
        ok = (ok and full.get("status") is None and scoped.get("total") == len(inactive)
              and scoped.get("por_papel") == counts(inactive) and scoped.get("status") == "inativo")
    result["users_json_intact"] = json.loads((work / "users.json").read_text()) == USERS
    result["ok"] = bool(ok and result["users_json_intact"])
    return result


SCENARIOS = {
    "page": (CREATE_PROMPT, EDIT_PROMPT, validate, "users.json", USERS),
    "catalog": (CATALOG_CREATE_PROMPT, CATALOG_EDIT_PROMPT, validate_catalog, "products.json", PRODUCTS),
    "control": (CONTROL_CREATE_PROMPT, CONTROL_EDIT_PROMPT, validate_control, "users.json", USERS),
}


def keep_delivered(work: Path, target: Path, data_name: str) -> None:
    """Copy what the session created, for the screenshots and videos of the round."""
    seed = {data_name, "README.md", "opencode.json"}
    target.mkdir(parents=True, exist_ok=True)
    for path in work.iterdir():
        if path.is_file() and path.name not in seed:
            shutil.copy2(path, target / path.name)


def session_folder(condition: str, rep: int) -> Path:
    """One folder per session: harnesses sharing a folder wipe each other's files and model settings."""
    parent = STATE / "work" / condition
    parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="rep-%02d-" % rep, dir=parent))


def run_one(condition: str, rep: int, keep: bool, model: str = MODEL, scenario: str = "page") -> dict:
    create_prompt, edit_prompt, check, data_name, data_rows = SCENARIOS[scenario]
    work = session_folder(condition, rep)
    config_dir = STATE / "config" / condition
    print("\n== %s rep %d ==" % (condition, rep), flush=True)
    seed_work(work, data_name, data_rows)
    (work / "opencode.json").write_text(json.dumps(condition_config(condition, model), indent=2) + "\n")

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    with OpencodeServer(work, config_dir, server_command(condition) is not None) as server:
        create = run_phase(server, create_prompt, "bench-%s-%02d-create" % (condition, rep), None, model)
        if create["quota_exhausted"]:
            raise QuotaExhausted("%s rep %d create" % (condition, rep), create.get("retry_after_ms"))
        create_files = check(work, edited=False)
        session_id = create.get("session_id")
        edit = {"exit": None, "wall_s": None, "peak_rss_mb": None,
                "session_id": session_id, "stdout_tail": "", "stderr_tail": ""}
        if session_id:
            edit = run_phase(server, edit_prompt, "bench-%s-%02d-edit" % (condition, rep), session_id, model)
            if edit["quota_exhausted"]:
                raise QuotaExhausted("%s rep %d edit" % (condition, rep), edit.get("retry_after_ms"))
        edit_files = check(work, edited=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)

    db = read_session(session_id) if session_id else {"error": "no session", "create": [], "edit": [], "session": None}
    record = {
        "condition": condition,
        "rep": rep,
        "create_run": create,
        "edit_run": edit,
        "create_phase": phase_metrics(db.get("create", [])),
        "edit_phase": phase_metrics(db.get("edit", [])),
        "session": db.get("session"),
        "session_cpu_s": round((after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime), 3),
        "files_after_create": create_files,
        "files_after_edit": edit_files,
        "db_error": db.get("error"),
    }
    print(json.dumps({
        "condition": condition, "rep": rep,
        "create": {k: record["create_phase"][k] for k in ("requests", "p50_s", "p99_s", "cost")},
        "edit": {k: record["edit_phase"][k] for k in ("requests", "p50_s", "p99_s", "cost")},
        "files": edit_files,
    }), flush=True)
    delivered = os.environ.get("BENCH_DELIVERED")
    if delivered:
        keep_delivered(work, Path(delivered) / ("%s-rep-%02d" % (condition, rep)), data_name)
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return record


def summarize(records: list) -> str:
    lines = []
    header = "| condicao | fase | sessoes | req | wall_s | cpu_sessao_s | rss_mb | p50_s | p99_s | in | out | reason | cache_r | cache_w | custo_usd |"
    sep = "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines += [header, sep]
    conditions = sorted({r["condition"] for r in records})
    for condition in conditions:
        subset = [r for r in records if r["condition"] == condition]
        for phase in ("create", "edit"):
            rows = [r for r in subset if r.get(phase + "_phase", {}).get("requests")]
            if not rows:
                continue
            walls = [r[phase + "_run"]["wall_s"] for r in rows if r.get(phase + "_run", {}).get("wall_s") is not None]
            cpus = [r["session_cpu_s"] for r in rows if r.get("session_cpu_s") is not None]
            rss = [r[phase + "_run"]["peak_rss_mb"] for r in rows if r.get(phase + "_run", {}).get("peak_rss_mb") is not None]
            reqs = sum(r[phase + "_phase"]["requests"] for r in rows)
            lat = []
            for r in rows:
                lat.extend(r[phase + "_phase"]["latencies_s"])
            tokens = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
            cost = 0.0
            for r in rows:
                for key in tokens:
                    tokens[key] += r[phase + "_phase"]["tokens"][key]
                cost += r[phase + "_phase"]["cost"]
            cells = [
                condition, phase, str(len(rows)), str(reqs),
                "%.1f" % (sum(walls) / len(walls)) if walls else "-",
                "%.1f" % (sum(cpus) / len(cpus)) if cpus else "-",
                "%.0f" % (sum(rss) / len(rss)) if rss else "-",
                "%.2f" % percentile(lat, 50) if lat else "-",
                "%.2f" % percentile(lat, 99) if lat else "-",
                str(tokens["input"]), str(tokens["output"]), str(tokens["reasoning"]),
                str(tokens["cache_read"]), str(tokens["cache_write"]),
                "%.4f" % cost,
            ]
            lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def save_results(out: Path, new_records: list) -> tuple[list, str]:
    merged = {}
    existing = out / "results.json"
    if existing.exists():
        for old in json.loads(existing.read_text()):
            merged[(old.get("condition"), old.get("rep"))] = old
    for record in new_records:
        merged[(record.get("condition"), record.get("rep"))] = record
    ordered = sorted(merged.values(), key=lambda r: (str(r.get("condition")), r.get("rep", 0)))
    payload = json.dumps(ordered, indent=2) + "\n"
    summary = summarize(ordered)
    out.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    for folder in (out, STATE):
        (folder / "results.json").write_text(payload)
        (folder / "summary.md").write_text(summary + "\n")
    return ordered, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--conditions", default="no-mcp,simplicio-3.9.2,simplicio-3.10.7")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="page")
    parser.add_argument("--out", type=Path, required=True,
                        help="new folder for this round's results.json and summary.md")
    args = parser.parse_args()

    STATE.mkdir(parents=True, exist_ok=True)
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    # One rep of every condition at a time: a route that drifts during the round hits them all alike.
    for rep in range(args.start, args.start + args.reps):
        for condition in conditions:
            try:
                record = run_one(condition, rep, args.keep, args.model, args.scenario)
            except QuotaExhausted as exc:
                print("STOP: provider usage limit reached at", exc, "retry_after_ms=%s" % exc.retry_ms, flush=True)
                print("nothing was saved for that session; after the reset, rerun with --start %d "
                      "and the same --conditions" % rep, flush=True)
                return 3
            except Exception as exc:
                record = {"condition": condition, "rep": rep, "error": repr(exc)}
                print("FAILED:", condition, rep, repr(exc), flush=True)
            ordered, summary = save_results(args.out, [record])
            print("\n" + summary, flush=True)

    print("\nwrote", args.out / "results.json", "and", args.out / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
