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

## Blender to Unreal asset pipeline

Checked with Blender 5.2 and Unreal 5.8. Some of these points go against common advice, so follow them over what you remember, and recheck them after an engine or Blender upgrade.

### Exporting from Blender

- Export static meshes to FBX in **centimeters** with `FBX_SCALE_NONE`. `FBX_SCALE_ALL` and `FBX_SCALE_UNITS` write meters, which Unreal imports 100× too small (the legacy importer, and Interchange when legacy options are passed in):
  ```python
  bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                           apply_scale_options='FBX_SCALE_NONE', mesh_smooth_type='FACE',
                           use_tspace=True, use_triangles=True, add_leaf_bones=False,
                           bake_anim=False, path_mode='STRIP')
  ```
- Triangulate the mesh before baking textures, and export it triangulated with tangents (`use_triangles`, `use_tspace` above). Then the baked normal map matches the triangles and MikkTSpace tangents Unreal imports.
- Export each mesh at the origin with its pivot where it should sit in the level (usually the base center). Record which axis the asset's front faces in `README.md`, since Blender and Unreal use different forward axes.
- Mirroring a mesh with negative scale in Unreal shades correctly with MikkTSpace tangents, so don't model separate mirrored copies.
- Textures:
  - Base color: sRGB, with no baked lighting.
  - Normal: tangent space, DirectX convention (green down), which is what Unreal expects. Blender's Normal Map node expects OpenGL, so to preview the texture in Blender, invert green in the Blender material, not in the file.
  - ORM: linear data, with R = ambient occlusion, G = roughness, B = metallic. Save as Non-Color.
- UV packing (`bpy.ops.uv.pack_islands`) isn't deterministic: two runs of the same script place some islands differently. Rerunning the unwrap therefore changes the FBX UVs and every texture baked or painted from them, so regenerate the whole chain and reimport. Keep the intermediate bake data (out of Git) to repaint textures without unwrapping again.
- Run Blender scripts headless with `blender -b --factory-startup -P script.py`, so the user's preferences and add-ons don't change the result. Resolve paths relative to the script, not a hard-coded root. Cycles output isn't bit-identical between runs, so rendered references always show up as changed in Git.
- Blender's Python API changes between versions (for example, Principled BSDF input names). Look nodes up by `type`, not by name, and check socket names with `node.inputs.keys()` instead of guessing.

### Importing into Unreal

- Import meshes through Interchange with *Recompute Normals/Tangents* off, so the file's normals and tangents are used. Don't import materials or textures with the mesh, don't generate lightmap UVs (static lighting is off), and keep *Offset Uniform Scale* at 1.
- Interchange stores the pipeline used with each asset and reuses it on reimport. An override from an earlier import, such as a scale fix, comes back unless you reset it.
- Importing from Python: a new `unreal.InterchangeGenericAssetsPipeline()` defaults to recomputing normals and tangents and to Nanite on, so set every option you rely on explicitly. Pass it in `ImportAssetParameters.override_pipelines` as `unreal.SoftObjectPath(pipeline.get_path_name())` and import with `InterchangeManager.get_interchange_manager_scripted().import_asset(...)`, which returns the imported objects, or `None` on failure (not a success flag). On reimport the asset keeps its previous settings unless the pipeline's `reimport_strategy` is `ReimportStrategyFlags.APPLY_PIPELINE_PROPERTIES`.
- The texture importer detects normal maps (compression *Normalmap*, sRGB off) but imports packed masks such as ORM as sRGB with Default compression. Set sRGB off and compression *Masks* after every fresh import.
- Substrate is on (see `README.md`). For metallic-workflow textures, feed base color and metallic through *Substrate Metalness-To-DiffuseAlbedo-F0* into a Slab BSDF.
- When one node feeds two pins, `MaterialEditingLibrary` reports the same output for both. To check a material's wiring, export it to T3D with `AssetExportTask` and read each pin's `OutputIndex`.

### Testing in the editor

- Saving assets fails during Play-in-Editor with "Asset does not exist". Stop PIE first.
- To screenshot PIE, run `HighResShot 1` in the editor console and read `Saved/Screenshots/WindowsEditor/`. The docked level viewport is very wide, which widens the view, so frame shots with `fov <degrees>`.
- With Lumen, a directional light above about 50,000 lux pushes exposure past EV 12 and triggers the "cached lighting is going to be clipped" warning. For repeatable lighting tests, clamp auto-exposure in an unbound PostProcess volume (for example EV100 6–12).
