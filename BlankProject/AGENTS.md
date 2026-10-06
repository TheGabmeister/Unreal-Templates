# AGENTS.md

This file contains the complete instructions for Codex when working in this project.

## Required first step: verify the Unreal setup

At the start of every session, before beginning project work, check both of these:

1. **The Unreal Engine skills are available.** The skills list must include the `unreal-engine-skills-for-codex` plugin's skills: `unreal-mcp` and `unreal-skill`. Skill names may be prefixed with the plugin name. The Codex plugin does not require `create-toolset`.
2. **The Unreal Engine MCP is working.** The `unreal-mcp` server must be connected in this session, with its tools callable (`list_toolsets`, `describe_toolset`, `call_tool`). Confirm this with a successful read-only call such as `list_toolsets`. A configured but failed or unreachable server does not count.

If either check fails, **stop project work immediately**. Do not look for workarounds, such as calling the server directly over HTTP. Tell the user which check failed and what needs fixing. Setup diagnosis and user-requested updates to these instructions are allowed while the setup is incomplete.

Common fixes:
- If skills are missing, install or enable **Unreal Engine Skills for Codex** and its two skills.
- If the MCP check fails, open the project in Unreal Editor and ensure its MCP server is running on `127.0.0.1:8000`. Check the plugin's MCP connection in Codex, reconnect if available, or start a new session. Verify recovery with a successful read-only MCP call.

## What this is

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**, one of several templates in the `Unreal-Templates` repo (git root is the parent directory `D:/dev/Unreal-Templates`; the sibling `ThirdPerson/` is a separate C++ template on UE 5.7). It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` to `/Script/BlankProject`, so do not remove them.

Template baseline (inspect the current files before relying on these details as the project evolves):
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there is nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- `Content/` holds only editor-generated `Developers/` and `Collections/` folders. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only), plus `ModelContextProtocol` and `AllToolsets`, which provide the `unreal-mcp` server and its tools.
- `Saved/`, `Intermediate/` and `DerivedDataCache/` must not be committed. Before staging, check the ignore rules; if this project still has no `.gitignore`, copy `../ThirdPerson/.gitignore` and review it for this project.

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

`.uasset`/`.umap` files are binary, so change them through the editor, not as text. Use the `unreal-mcp` skill and its discovery flow (`list_toolsets`, `describe_toolset`, then `call_tool`) to drive the running editor. Check relevant project Agent Skills through `AgentSkillToolset` when starting unfamiliar work, and inspect tool results for explicit success before continuing.

The MCP server only connects while the editor is open. It auto-starts through `bAutoStartServer=True` in `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`. That file is per-user and not committed, so on a fresh clone run `ModelContextProtocol.StartServer` in the editor console instead. The client connects to `http://127.0.0.1:8000/mcp` through the configured MCP connection.

Save affected assets before bulk changes and again afterward. Serialize dependent calls and mutations that affect the same asset or editor state, wait for compilation to finish, and check whether Play-in-Editor is active before using editor-only tools.
