from pathlib import Path

ROOT = Path(__file__).parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_no_standalone_loop_binary_is_downloaded_or_listed():
    for installer in ("install.sh", "install.ps1"):
        text = _read(installer)
        assert "simplicio-loop-$OS-$ARCH" not in text, installer
        assert "simplicio-loop-windows-x64.exe" not in text, installer
        assert "standalone binary" not in text, installer
    assert "simplicio-loop" not in _read("SHA256SUMS")


def test_unix_installer_installs_loop_from_pypi_into_a_dedicated_venv():
    text = _read("install.sh")
    assert 'LOOP_VENV="$PURGE_DIR/loop-venv"' in text
    assert "sys.version_info >= (3, 11)" in text
    assert 'fail_install "loop_python_missing"' in text
    assert '"$LOOP_PY" -m venv "$LOOP_VENV"' in text
    assert '"$LOOP_VENV/bin/python" -m pip install --disable-pip-version-check --quiet simplicio-loop' in text
    assert "for LOOP_CMD in simplicio-loop simplicio-mapper simplicio-dev-cli; do" in text
    assert 'ln -sf "$LOOP_VENV/bin/$LOOP_CMD" "$BIN_DIR/$LOOP_CMD"' in text
    assert '"$BIN_DIR/simplicio-loop" install --global' in text
    assert '"$BIN_DIR/simplicio-loop" doctor </dev/null; then' in text
    assert 'warn "simplicio-loop doctor reportou falhas' in text


def test_windows_installer_installs_loop_from_pypi_and_rejects_store_alias():
    text = _read("install.ps1")
    assert "function Find-LoopPython" in text
    assert "WindowsApps" in text
    assert "sys.version_info >= (3, 11)" in text
    assert '"loop_python_missing"' in text
    assert "-m venv $LoopVenv" in text
    assert "-m pip install --disable-pip-version-check --quiet simplicio-loop" in text
    assert "& $LoopCli install --global" in text
    assert "& $LoopCli doctor" in text


def test_install_docs_describe_the_pypi_loop_path_not_a_binary():
    text = _read("INSTALL.md")
    assert "simplicio-loop" in text
    assert "PyPI" in text
    assert "Python 3.11" in text
    assert "instalados via `pip`" not in text
