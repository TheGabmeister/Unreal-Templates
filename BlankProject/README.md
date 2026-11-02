# BlankProject

`BlankProject` is a **Blueprint-only Unreal Engine 5.8 project template**. It was created from Epic's `TP_BlankBP` template; `DefaultEngine.ini` keeps `ActiveGameNameRedirects` from `TP_BlankBP` → `/Script/BlankProject`, so don't remove them.

Engine install: `C:/Program Files/Epic Games/UE_5.8`.

## Template baseline

These details describe the template as created; check the current files before relying on them, since the project will evolve.
- No `Source/` folder and no `Modules` in `BlankProject.uproject`, so there's nothing to compile. Adding the first C++ class (Tools → New C++ Class in the editor) creates `Source/`, `*.Target.cs` files and a module entry in the `.uproject`. After that the project needs a C++ build before it will open.
- Project assets go under `Content/_Project/` (see below). Editor-generated `Developers/` and `Collections/` folders also exist. The startup map is the engine's `/Engine/Maps/Templates/OpenWorld` (`GameDefaultMap` in `Config/DefaultEngine.ini`), not a project asset.
- Extra plugins: `ModelingToolsEditorMode` (editor-only) and `PythonScriptPlugin` (editor Python, with remote execution enabled by `bRemoteExecution=True` in `Config/DefaultEngine.ini`).
- `Tools/ue.py` runs Python inside this project's editor from the command line, so agents can change assets without the MCP server. `Tools/README.md` covers it and the engine commands.
- `.gitignore` excludes `Saved/`, `Intermediate/`, `DerivedDataCache/` and other generated files.

## Project asset organization

All project-specific assets live under `Content/_Project/` (`/Game/_Project/` in Unreal). Imported Marketplace/Fab packs stay in their original vendor or pack folders outside `_Project`, so their package paths stay unchanged. Project-specific child Blueprints, material instances, duplicates and adaptations of imported assets go under `_Project`; they may reference the original pack assets.

The folder structure, with feature or asset subfolders added as needed:

```text
Content/_Project/
├── Blueprints/       Characters, Components, Core, Gameplay, Interfaces
├── Data/
├── Input/
├── Maps/
├── Materials/
└── UI/
```

Empty folders hold `.gitkeep` files so the structure survives a Git checkout. They're placeholders, not Unreal assets.

## Rendering and config baseline

`Config/DefaultEngine.ini` targets high-end desktop. Assets and settings added to the project should stay compatible with these settings:
- Static lighting is disabled (`r.AllowStaticLighting=False`). Lighting is Lumen GI and reflections (`DynamicGlobalIlluminationMethod=1`, `ReflectionMethod=1`), with Virtual Shadow Maps and mesh distance fields.
- Hardware ray tracing is on, and **Substrate** materials are enabled (`r.Substrate=True`). New materials are authored as Substrate, not legacy shading models.
- Windows uses DX12 with SM6; Linux targets Vulkan SM6 and Mac targets Metal SM6.
- Input uses Enhanced Input (`DefaultPlayerInputClass`/`DefaultInputComponentClass` in `Config/DefaultInput.ini`). Use Input Actions and Mapping Contexts, not legacy axis/action mappings.
- `Config/DefaultGame.ini` contains CommonUI settings.

## Creating a new project from this template

When this folder is copied and renamed into a new project, rename `BlankProject.uproject` to `<NewName>.uproject`, point the `ActiveGameNameRedirects` in `Config/DefaultEngine.ini` at `/Script/<NewName>`, and replace the `BlankProject` names and `D:/dev/Unreal-Templates/BlankProject` paths in `README.md` and `Tools/README.md`.

No port or agent configuration is needed: `Tools/ue.py` finds the project from its own location and the project's editor by its path.
