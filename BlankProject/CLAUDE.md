# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Required first step: verify the Unreal setup

At the start of every session, before doing anything else, check both of these:

1. **The Unreal Engine skills are available.** The skills list must include the `unreal-engine-skills-for-claude-code` plugin's skills: `unreal-mcp`, `create-toolset` and `unreal-skill`.
2. **The Unreal Engine MCP is working.** The `unreal-mcp` server must be connected in this session, with its tools callable (`list_toolsets`, `describe_toolset`, `call_tool`). Confirm this with a successful read-only call such as `list_toolsets`. A server that is configured but shown as failed or unreachable does not count.

If either check fails, **stop immediately**. Don't start the task and don't look for workarounds, such as calling the server directly over HTTP. Tell the user that the setup isn't complete, say which check failed, and explain that they must fix the setup before you can continue. Common fixes:
- The skills are missing: install or enable the `unreal-engine-skills-for-claude-code` plugin.
- The MCP check fails: open the project in the editor so the server starts on `127.0.0.1:8000`, then type `/mcp` in the session and reconnect `unreal-mcp`, or start a new session. A session that started before the editor did won't retry the connection by itself.

## What this is

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**, one of several templates in the `Unreal-Templates` repo (git root is the parent directory `D:/dev/Unreal-Templates`; the sibling `ThirdPerson/` is a separate C++ template on UE 5.7). It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` → `/Script/BlankProject`, so don't remove them.

Current state:
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there's nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- `Content/` holds only editor-generated `Developers/` and `Collections/` folders. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only), plus `ModelContextProtocol` and `AllToolsets`, which provide the `unreal-mcp` server and its tools.
- Unlike `ThirdPerson/`, this project has no `.gitignore` yet. `Saved/`, `Intermediate/` and `DerivedDataCache/` exist on disk and must not be committed; copy `../ThirdPerson/.gitignore` before staging.

## Engine and commands

Engine install: `C:/Program Files/Epic Games/UE_5.8`.

```bash
# Open the editor
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject"

# Run automation tests headlessly (replace the filter with a test name or prefix to run one test)
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -ExecCmds="Automation RunTests Project; Quit" -unattended -nullrhi -nosplash -log

# Cook and package for Windows
"C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project="D:/dev/Unreal-Templates/BlankProject/BlankProject.uproject" -platform=Win64 -clientconfig=Development -cook -stage -pak -archive -archivedirectory="D:/dev/Unreal-Templates/BlankProject/Build"
```

Logs go to `Saved/Logs/BlankProject.log`.

## Rendering and config baseline

`Config/DefaultEngine.ini` targets high-end desktop. Assets and settings added to the template should stay compatible with these settings:
- Static lighting is disabled (`r.AllowStaticLighting=False`). Lighting is Lumen GI and reflections (`DynamicGlobalIlluminationMethod=1`, `ReflectionMethod=1`), with Virtual Shadow Maps and mesh distance fields.
- Hardware ray tracing is on, and **Substrate** materials are enabled (`r.Substrate=True`). New materials are authored as Substrate, not legacy shading models.
- Windows uses DX12 with SM6; Linux targets Vulkan SM6 and Mac targets Metal SM6.
- Input uses Enhanced Input (`DefaultPlayerInputClass`/`DefaultInputComponentClass` in `DefaultInput.ini`). Use Input Actions and Mapping Contexts, not legacy axis/action mappings.
- `DefaultGame.ini` contains CommonUI settings.

## Editing assets

`.uasset`/`.umap` files are binary, so change them through the editor and not as text. The `unreal-mcp` server lets Claude drive a running editor (spawn actors, edit Blueprints and materials, and so on), but it only connects while the editor is open. The server auto-starts through `bAutoStartServer=True` in `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`. That file is per-user and not committed, so on a fresh clone run `ModelContextProtocol.StartServer` in the editor console instead. The client connects to `http://127.0.0.1:8000/mcp`.

## Coding convention
- Follow KISS and YAGNI.  Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.