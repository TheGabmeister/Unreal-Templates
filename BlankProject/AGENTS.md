# AGENTS.md

This file contains the complete instructions for Codex when working in this project.

## What this is

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**. It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` to `/Script/BlankProject`, so do not remove them.

Template baseline (inspect the current files before relying on these details as the project evolves):
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there is nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- Project asset folders are organized under `Content/_Project/`; editor-generated `Developers/` and `Collections/` folders also exist. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only) and `PythonScriptPlugin` (editor Python, used by `Tools/ue.py`).
- `Tools/ue.py` lets agents drive the editor from the command line (see "Editing assets").
- `.gitignore` excludes `Saved/`, `Intermediate/`, `DerivedDataCache/` and other generated files. Never commit those folders.

## Creating a new project from this template

When this folder is copied and renamed into a new project, rename `BlankProject.uproject` to `<NewName>.uproject`, point the `ActiveGameNameRedirects` in `Config/DefaultEngine.ini` at `/Script/<NewName>`, and replace the `BlankProject` names and `D:/dev/Unreal-Templates/BlankProject` paths in this file and `CLAUDE.md`.

No port or agent configuration is needed: `Tools/ue.py` finds the project from its own location and the project's editor by its path.

## Project asset organization

Create all project-specific assets under `Content/_Project/` (`/Game/_Project/` in Unreal). Keep imported Marketplace/Fab packs in their original vendor or pack folders outside `_Project`, preserving their package paths. Put project-specific child Blueprints, material instances, duplicates, and adaptations of imported assets under `_Project`; references to the original pack assets are allowed.

Use this folder structure, adding feature or asset subfolders as needed:

```text
Content/_Project/
├── Blueprints/       Characters, Components, Core, Gameplay, Interfaces
├── Data/
├── Input/
├── Maps/
├── Materials/
└── UI/
```

Empty folders contain `.gitkeep` files so the structure survives Git checkout. These are placeholders, not Unreal assets. Use the editor (for example `unreal.EditorAssetLibrary.rename_asset` through `Tools/ue.py`) to move or rename existing assets so references are updated; do not move `.uasset` or `.umap` files directly on disk.

## Engine and commands

Engine install: `C:/Program Files/Epic Games/UE_5.8`.

```powershell
# Open the editor
& "C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject"

# Run automation tests headlessly (replace the filter with a test name or prefix)
& "C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -ExecCmds="Automation RunTests Project; Quit" -unattended -nullrhi -nosplash -log

# Cook and package for Windows
& "C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project="D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -platform=Win64 -clientconfig=Development -cook -stage -pak -archive -archivedirectory="D:/dev/Unreal-Templates/BlankProject/Build"
```

Logs go to `Saved/Logs/BlankProject.log`.

## Rendering and config baseline

`Config/DefaultEngine.ini` targets high-end desktop. Assets and settings added to the template should stay compatible with these settings:
- Static lighting is disabled (`r.AllowStaticLighting=False`). Lighting is Lumen GI and reflections (`DynamicGlobalIlluminationMethod=1`, `ReflectionMethod=1`), with Virtual Shadow Maps and mesh distance fields.
- Hardware ray tracing is on, and **Substrate** materials are enabled (`r.Substrate=True`). New materials are authored as Substrate, not legacy shading models.
- Windows uses DX12 with SM6; Linux targets Vulkan SM6 and Mac targets Metal SM6.
- Input uses Enhanced Input (`DefaultPlayerInputClass`/`DefaultInputComponentClass` in `Config/DefaultInput.ini`). Use Input Actions and Mapping Contexts, not legacy axis/action mappings.
- `Config/DefaultGame.ini` contains CommonUI settings.

## Editing assets

`.uasset`/`.umap` files are binary, so change them through the editor, not as text. `Tools/ue.py` runs Python inside this project's editor through Unreal's built-in Python remote execution (`PythonScriptPlugin`, enabled by `bRemoteExecution=True` in `Config/DefaultEngine.ini`). Run it from the project root:

```powershell
# List running editors that accept commands ("this_project" marks this one)
python Tools/ue.py nodes

# Run Python in this project's open editor, windowed or headless
python Tools/ue.py exec "import unreal; print(unreal.EditorAssetLibrary.list_assets('/Game/_Project'))"
python Tools/ue.py exec -f path/to/script.py

# Start a headless editor (no window, no rendering), and quit it again
python Tools/ue.py start --headless
python Tools/ue.py stop

# One-off headless run when no editor is open; nothing stays running afterward
python Tools/ue.py run -f path/to/script.py
```

`exec` and `run` read the code from stdin when given neither code nor `-f`, which suits multi-line scripts.

- **Pick the mode.** If this project's editor is open, use `exec`. Otherwise use `run` for a single change, or `start --headless` followed by `exec` calls for a series of changes. Each `run` and `start` loads the project, which takes about 15 seconds for this template and longer as content grows. Only one editor may have the project open, so `run` and `start` refuse while one is.
- **Several projects at once.** Each editor is found by its project path, so editors for different projects run side by side with no port setup. Calls to the same project wait for each other.
- **Output.** Only what the script prints is returned, plus Python warnings and errors, and a failed script exits with code 1. Print short results, such as names or counts, rather than whole objects. Logs: `Saved/Logs/BlankProject.log` for the editor, `Saved/Logs/ue_run.log` for the last `run`.
- **Saving.** Nothing is saved automatically. Save with `unreal.EditorAssetLibrary.save_asset()` or `save_directory()`. `run` discards unsaved changes when it exits, and `stop` refuses while packages are unsaved unless given `--discard`.
- **Headless limits.** Headless editors do not render, so there are no viewport screenshots, thumbnails or GPU work. `stop` only quits headless editors; leave a windowed editor for the user to close.
- **Python API.** Always `import unreal`. Check names with `help()` or `dir()` through `exec` instead of guessing. Prefer editor subsystems such as `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)`; the Editor Scripting Utilities libraries (`EditorLevelLibrary` and similar) are deprecated in 5.8.
- **Python version.** `ue.py` needs Python 3.8 or later. If `python` is not installed, use the engine's `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe`.
- **Sandbox.** `ue.py` uses local network sockets and `start` launches the editor. If the sandbox blocks either (for example `nodes` finds nothing while the editor is open), rerun the command with escalated permissions.
- **Security.** Remote execution runs any code it receives, without authentication. Keep the engine defaults that limit it to this machine (Multicast Bind Address `127.0.0.1`, TTL `0`).

Save affected assets before bulk changes and again afterward. Serialize dependent calls and mutations that affect the same asset or editor state, wait for compilation to finish, and check whether Play-in-Editor is active before changing the level.

## Coding convention
- Follow KISS and YAGNI.  Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.