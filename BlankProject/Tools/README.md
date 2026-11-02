# Command-line tools

How to open, test, package and edit this project from the command line. Run the commands from the project root.

## Engine commands

```bash
# Open the editor
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject"

# Run automation tests headlessly (replace the filter with a test name or prefix to run one test)
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -ExecCmds="Automation RunTests Project; Quit" -unattended -nullrhi -nosplash -log

# Cook and package for Windows
"C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project="D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -platform=Win64 -clientconfig=Development -cook -stage -pak -archive -archivedirectory="D:/dev/Unreal-Templates/BlankProject/Build"
```

## Editing assets with `ue.py`

`.uasset`/`.umap` files are binary, so change them through the editor and not as text. Move or rename assets through the editor too (for example `unreal.EditorAssetLibrary.rename_asset`) so references get updated; never move `.uasset` or `.umap` files directly on disk.

`ue.py` runs Python inside this project's editor through Unreal's built-in Python remote execution:

```bash
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
- **Saving.** Nothing is saved automatically. Save with `unreal.EditorAssetLibrary.save_asset()` or `save_directory()`, before bulk changes and again afterward. `run` discards unsaved changes when it exits, and `stop` refuses while packages are unsaved unless given `--discard`.
- **Order.** Run dependent calls, and changes that touch the same asset or editor state, one at a time. Wait for compilation to finish, and check whether Play-in-Editor is running before changing the level.
- **Headless limits.** Headless editors don't render, so there are no viewport screenshots, thumbnails or GPU work. `stop` only quits headless editors; leave a windowed editor for the user to close.
- **Python API.** Always `import unreal`. Check names with `help()` or `dir()` through `exec` instead of guessing. Prefer editor subsystems such as `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)`; the Editor Scripting Utilities libraries (`EditorLevelLibrary` and similar) are deprecated in 5.8.
- **Python version.** `ue.py` needs Python 3.8 or later. If `python` isn't installed, use the engine's `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe`.
- **Security.** Remote execution runs any code it receives, without authentication. Keep the engine defaults that limit it to this machine (Multicast Bind Address `127.0.0.1`, TTL `0`).
