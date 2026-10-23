# Simplicio — AI Coding Agent

Save up to 96% on AI tokens. Single binary, runs on your machine.

## Install

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

The wheel writes the single managed runtime to `~/.simplicio/bin/simplicio`
(`SIMPLICIO_BIN_DIR` overrides the directory). The `simplicio` console script
stays a thin launcher and never owns a second copy of the runtime.

Then use:

```bash
simplicio chat "build a login endpoint and test until it passes"
```

## Links

- Website: https://simpleti.com.br/simplicio/
- GitHub: https://github.com/simpletibr/simplicio
