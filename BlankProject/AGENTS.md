# AGENTS.md

This file contains the complete instructions for Codex when working in this project.

## Required first step: verify the Unreal setup

At the start of every session, before beginning project work, check both of these:

1. **The Unreal Engine skills are available.** The skills list must include the `unreal-engine-skills-for-codex` plugin's skills: `unreal-mcp` and `unreal-skill`. Skill names may be prefixed with the plugin name. The Codex plugin does not require `create-toolset`.
2. **The Unreal Engine MCP is working.** The `unreal-mcp` server must be connected in this session, with its tools callable (`list_toolsets`, `describe_toolset`, `call_tool`). Confirm this with a successful read-only call such as `list_toolsets`. A configured but failed or unreachable server does not count.

If either check fails, **stop project work immediately**. Do not look for workarounds, such as calling the server directly over HTTP. Tell the user which check failed and what needs fixing. Setup diagnosis and user-requested updates to these instructions are allowed while the setup is incomplete.

Common fixes:
- If skills are missing, install or enable **Unreal Engine Skills for Codex** and its two skills.
- If the MCP check fails, open the project in Unreal Editor and ensure its MCP server is running on the project's port (see "MCP port" below). Check the plugin's MCP connection in Codex, reconnect if available, or start a new session. Verify recovery with a successful read-only MCP call.

A successful check does not prove the connection reaches *this* project: if another editor holds the port, calls go to that project instead. Before changing assets, confirm the connected editor is this project, for example by checking that `/Game/` contains this project's assets or that the editor log mentions this project's path.

## What this is

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**, one of several templates in the `Unreal-Templates` repo (git root is the parent directory `D:/dev/Unreal-Templates`; the sibling `ThirdPerson/` is a separate C++ template on UE 5.7). It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` to `/Script/BlankProject`, so do not remove them.

Template baseline (inspect the current files before relying on these details as the project evolves):
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there is nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- Project asset folders are organized under `Content/_Project/`; editor-generated `Developers/` and `Collections/` folders also exist. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only), plus `ModelContextProtocol` and `AllToolsets`, which provide the `unreal-mcp` server and its tools.
- `Saved/`, `Intermediate/` and `DerivedDataCache/` must not be committed. Before staging, check the ignore rules; if this project still has no `.gitignore`, copy `../ThirdPerson/.gitignore` and review it for this project.

## Creating a new project from this template

When this folder is copied and renamed into a new project:
1. Rename `BlankProject.uproject` to `<NewName>.uproject`, point the `ActiveGameNameRedirects` in `Config/DefaultEngine.ini` at `/Script/<NewName>`, and replace the `BlankProject` names and `D:/dev/Unreal-Templates/BlankProject` paths in this file and `CLAUDE.md`.
2. **Give the project its own MCP port.** See "MCP port" below. Skipping this is what lets two open editors collide.

## MCP port

Every Unreal editor's MCP server defaults to port 8000, and the first editor to start takes it. A second editor on the same port fails to start its server without an obvious error, and agent tool calls then go to the wrong project. This template itself uses 8000, so each project made from it needs its own port:
- Pick an unused port from 8001 upward. To see which ports are taken, search the other projects under `D:/dev` for `ServerPortNumber` in `Config/DefaultEditorPerProjectUserSettings.ini` and for `127.0.0.1:` in `.mcp.json`.
- Create `Config/DefaultEditorPerProjectUserSettings.ini`:
  ```ini
  [/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
  ServerUrlPath=/mcp
  ServerPortNumber=<port>
  bAutoStartServer=True
  bEnableToolSearch=True
  ```
- Point the Codex MCP connection at `http://127.0.0.1:<port>/mcp`. For Claude Code, create a project-root `.mcp.json` with an `unreal-mcp` entry at the same URL; `CLAUDE.md` has the exact file.
- Replace the port references in this file and `CLAUDE.md`.
- Do not change MCP settings in Editor Preferences → Model Context Protocol. Doing so writes a per-user copy of every MCP setting (including the default port 8000) into `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`, which overrides the committed file. Edit the committed file instead. If a `Saved` copy exists, delete that section with the editor closed, or delete `Saved/`.
- Restart the editor and start a new agent session so both sides pick up the port. MCP clients read their configuration only when a session starts, so reconnecting a session that is already running keeps the old URL.

## Project asset organization

Create all project-specific assets under `Content/_Project/` (`/Game/_Project/` in Unreal). Keep imported Marketplace/Fab packs in their original vendor or pack folders outside `_Project`, preserving their package paths. Put project-specific child Blueprints, material instances, duplicates, and adaptations of imported assets under `_Project`; references to the original pack assets are allowed.

Use this folder structure, adding feature or asset subfolders as needed:

```text
Content/_Project/
├── AI/               BehaviorTrees, Blackboards
├── Animations/       BlendSpaces, Montages
├── Audio/            Dialogue, Music, SFX
├── Blueprints/       Characters, Components, Core, Gameplay, Interfaces
├── Cinematics/
├── Data/             Curves, DataAssets, DataTables
├── Editor/           Project editor utilities
├── Input/            Actions, MappingContexts
├── Maps/             Gameplay, Tests
├── Materials/        Functions, Instances, Master
├── Meshes/           Skeletal, Static
├── Textures/
├── UI/               Fonts, Icons, Widgets
└── VFX/              Niagara
```

Empty folders contain `.gitkeep` files so the structure survives Git checkout. These are placeholders, not Unreal assets. Use the editor/MCP to move or rename existing assets so references are updated; do not move `.uasset` or `.umap` files directly on disk.

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

The MCP server only connects while the editor is open. Once the project has its own `Config/DefaultEditorPerProjectUserSettings.ini` (see "MCP port"), the server auto-starts on that port. Until then, run `ModelContextProtocol.StartServer` in the editor console. The client connects to `http://127.0.0.1:<port>/mcp` through the configured MCP connection, which is 8000 for the template itself.

Save affected assets before bulk changes and again afterward. Serialize dependent calls and mutations that affect the same asset or editor state, wait for compilation to finish, and check whether Play-in-Editor is active before using editor-only tools.

## Coding convention
- Follow KISS and YAGNI.  Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.