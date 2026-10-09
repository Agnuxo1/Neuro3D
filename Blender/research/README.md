# Preserved local research (2026-10-06)
These files were recovered unchanged from the original Neuro3D working tree.
Inclusion preserves provenance; it does not establish scientific validation or
make every historical experiment portable.
- exp003/fixture.py and fixture.json match the historical frozen fixture branch.
- optical_mesh contains exploratory CPU/CUDA/Blender work and a digits example.
- optical_mesh/blender_mesh_scene.py contains a historical absolute output path
  and executes scene-building code at import time. Do not import it during test
  discovery or run it against an unsaved interactive scene.
- Compiled Python caches were excluded. Original Python/JSON bytes were preserved.
See [current status](../../Docs/PROJECT_STATUS_2026-10-06.md).
