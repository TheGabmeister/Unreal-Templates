# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. What the project is, how it's organized and its config baseline are in `README.md`:

@README.md

## Working in this project

- Read `Tools/README.md` before opening, testing or packaging the project, or changing assets. It covers the engine commands and `Tools/ue.py`, which drives the editor from the command line.
- Never commit `Saved/`, `Intermediate/`, `DerivedDataCache/` or other generated folders.

## Coding convention
- Follow KISS and YAGNI. Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.
