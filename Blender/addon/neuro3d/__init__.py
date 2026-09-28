"""Blender adapter for the Neuro3D CPU preview.

The addon never starts GPU computation automatically. Its first operator creates
an emissive CPU-preview scene; the dormant shader is a separate future gate.
"""

from __future__ import annotations

from pathlib import Path
import sys

bl_info = {
    "name": "Neuro3D",
    "author": "Neuro3D contributors",
    "version": (0, 1, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Neuro3D",
    "description": "CPU-preview adapter for an optical-like neural galaxy",
    "category": "3D View",
}

_CORE = Path(__file__).resolve().parents[2] / "core"
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))

from photonic_model import build_deterministic_graph, snapshot, step  # noqa: E402

try:
    import bpy
except ImportError:  # Static tests can import the module without Blender.
    bpy = None


GPU_ENABLED_BY_DEFAULT = False


def build_cpu_preview_scene(neuron_count: int = 64, edges_per_neuron: int = 4):
    """Build a CPU-generated scene only when explicitly called from Blender."""

    if bpy is None:
        raise RuntimeError("Este operador debe ejecutarse dentro de Blender.")

    graph = build_deterministic_graph(neuron_count, edges_per_neuron)
    collection = bpy.data.collections.get("Neuro3D")
    if collection is None:
        collection = bpy.data.collections.new("Neuro3D")
        bpy.context.scene.collection.children.link(collection)

    material = bpy.data.materials.get("Neuro3D CPU Preview") or bpy.data.materials.new("Neuro3D CPU Preview")
    material.diffuse_color = (0.03, 0.25, 1.0, 1.0)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Emission Color"].default_value = (0.01, 0.2, 1.0, 1.0)
        principled.inputs["Emission Strength"].default_value = 4.0

    for index, neuron in enumerate(graph.neurons):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=8.0, location=neuron.position)
        obj = bpy.context.object
        obj.name = f"NebulaNeuron_{index:04d}"
        obj.data.materials.append(material)
        for collection_link in list(obj.users_collection):
            collection_link.objects.unlink(obj)
        collection.objects.link(obj)

    return snapshot(graph)


if bpy is not None:
    class NEBULA_OT_build_cpu_preview(bpy.types.Operator):
        bl_idname = "nebula.build_cpu_preview"
        bl_label = "Build CPU Preview"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            build_cpu_preview_scene()
        self.report({"INFO"}, "Neuro3D CPU preview created; GPU remains dormant.")
            return {"FINISHED"}


    class NEBULA_PT_panel(bpy.types.Panel):
        bl_label = "Neuro3D"
        bl_idname = "NEBULA_PT_santo_grial"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Nebula"

        def draw(self, context):
            self.layout.label(text="CPU preview only")
            self.layout.operator(NEBULA_OT_build_cpu_preview.bl_idname)


    _CLASSES = (NEBULA_OT_build_cpu_preview, NEBULA_PT_panel)

    def register():
        for cls in _CLASSES:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in reversed(_CLASSES):
            bpy.utils.unregister_class(cls)
else:
    _CLASSES = ()

    def register():
        raise RuntimeError("Blender no está disponible; registro omitido en pruebas estáticas.")

    def unregister():
        return None
