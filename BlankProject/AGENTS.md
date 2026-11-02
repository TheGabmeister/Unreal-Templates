# AGENTS.md

This file contains the instructions for Codex on how to work in this project. Read `README.md` before starting work: it describes what the project is, how it is organized and its config baseline.

## Working in this project

- Read `Tools/README.md` before opening, testing or packaging the project, or changing assets. It covers the engine commands and `Tools/ue.py`, which drives the editor from the command line.
- The commands in `Tools/README.md` are written for bash. In PowerShell, prefix a command that starts with a quoted executable path with `&`.
- `ue.py` uses local network sockets and `start` launches the editor. If the sandbox blocks either (for example `nodes` finds nothing while the editor is open), rerun the command with escalated permissions.
- Never commit `Saved/`, `Intermediate/`, `DerivedDataCache/` or other generated folders.

## Coding convention
- Follow KISS and YAGNI. Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.
