# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Required first step: verify the Unreal setup

At the start of every session, before doing anything else, check both of these:

1. **The Unreal Engine skills are available.** The skills list must include the `unreal-engine-skills-for-claude-code` plugin's skills: `unreal-mcp`, `create-toolset` and `unreal-skill`.
2. **The Unreal Engine MCP is working.** The `unreal-mcp` server must be connected in this session, with its tools callable (`list_toolsets`, `describe_toolset`, `call_tool`). Confirm this with a successful read-only call such as `list_toolsets`. A server that is configured but shown as failed or unreachable does not count.

If either check fails, **stop immediately**. Don't start the task and don't look for workarounds, such as calling the server directly over HTTP. Tell the user that the setup isn't complete, say which check failed, and explain that they must fix the setup before you can continue. Common fixes:
- The skills are missing: install or enable the `unreal-engine-skills-for-claude-code` plugin.
- The MCP check fails: open the project in the editor so the server starts on the project's port (see "MCP port" below), then type `/mcp` in the session and reconnect `unreal-mcp`, or start a new session. A session that started before the editor did won't retry the connection by itself.

A successful check doesn't prove you're connected to *this* project: if another editor holds the port, calls go to that project instead. Before changing assets, confirm the connected editor is this project, for example by checking that `/Game/` contains this project's assets or that the editor log mentions this project's path.

## What this is

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**, one of several templates in the `Unreal-Templates` repo (git root is the parent directory `D:/dev/Unreal-Templates`; the sibling `ThirdPerson/` is a separate C++ template on UE 5.7). It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` → `/Script/BlankProject`, so don't remove them.

Template baseline (check the current files before relying on these details, since the project will evolve):
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there's nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- Project assets go under `Content/_Project/` (see below). Editor-generated `Developers/` and `Collections/` folders also exist. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only), plus `ModelContextProtocol` and `AllToolsets`, which provide the `unreal-mcp` server and its tools.
- `.gitignore` excludes `Saved/`, `Intermediate/`, `DerivedDataCache/` and other generated files. Never commit those folders.

## Creating a new project from this template

When this folder is copied and renamed into a new project:
1. Rename `BlankProject.uproject` to `<NewName>.uproject`, point the `ActiveGameNameRedirects` in `Config/DefaultEngine.ini` at `/Script/<NewName>`, and replace the `BlankProject` names and `D:/dev/Unreal-Templates/BlankProject` paths in this file and `AGENTS.md`.
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
- Create `.mcp.json` in the project root. It overrides the user-level `unreal-mcp` entry, which points at 8000:
  ```json
  {
    "mcpServers": {
      "unreal-mcp": { "type": "http", "url": "http://127.0.0.1:<port>/mcp" }
    }
  }
  ```
- Replace the port references in this file and `AGENTS.md`, including the Codex connection URL.
- A value set in Editor Preferences → Model Context Protocol is saved to the per-user `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini` and overrides the committed one, so keep that port the same, or leave it unset.
- Restart the editor and start a new agent session so both sides pick up the port.

## Project asset organization

Create all project-specific assets under `Content/_Project/` (`/Game/_Project/` in Unreal). Keep imported Marketplace/Fab packs in their original vendor or pack folders outside `_Project`, so their package paths stay unchanged. Put project-specific child Blueprints, material instances, duplicates and adaptations of imported assets under `_Project`; they may reference the original pack assets.

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

Empty folders hold `.gitkeep` files so the structure survives a Git checkout. They're placeholders, not Unreal assets. Move or rename assets through the editor or MCP so references get updated; never move `.uasset` or `.umap` files directly on disk.

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
- Input uses Enhanced Input (`DefaultPlayerInputClass`/`DefaultInputComponentClass` in `Config/DefaultInput.ini`). Use Input Actions and Mapping Contexts, not legacy axis/action mappings.
- `Config/DefaultGame.ini` contains CommonUI settings.

## Editing assets

`.uasset`/`.umap` files are binary, so change them through the editor and not as text. Use the `unreal-mcp` skill and its discovery flow (`list_toolsets`, `describe_toolset`, then `call_tool`) to drive the running editor. When starting unfamiliar work, check `AgentSkillToolset` for relevant project Agent Skills. Check each tool result for explicit success before continuing.

The MCP server only connects while the editor is open. Once the project has its own `Config/DefaultEditorPerProjectUserSettings.ini` (see "MCP port"), the server auto-starts on that port. Until then, run `ModelContextProtocol.StartServer` in the editor console. The client connects to `http://127.0.0.1:<port>/mcp`, which is 8000 for the template itself.

Save affected assets before bulk changes and again afterward. Run dependent calls, and changes that touch the same asset or editor state, one at a time. Wait for compilation to finish, and check whether Play-in-Editor is running before using editor-only tools.

## Coding convention
- Follow KISS and YAGNI. Use DRY when something repeats 3 or more times.
- Follow Unreal Engine architecture best practices.
