"""Blender adapter for a scene-driven optical circuit and legacy CPU preview."""

from __future__ import annotations

from pathlib import Path
import sys

bl_info = {
    "name": "Neuro3D",
    "author": "Neuro3D contributors",
    "version": (0, 2, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Neuro3D",
    "description": "Scene-driven CPU optical circuit and neural preview",
    "category": "3D View",
}

_CORE = Path(__file__).resolve().parents[2] / "core"
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))
_ADDON = Path(__file__).resolve().parent
if str(_ADDON) not in sys.path:
    sys.path.insert(0, str(_ADDON))

from photonic_model import build_deterministic_graph, snapshot, step  # noqa: E402
from optical_scene import create_circuit, trace_circuit  # noqa: E402

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
    class NEURO3D_OT_create_optical_circuit(bpy.types.Operator):
        bl_idname = "neuro3d.create_optical_circuit"
        bl_label = "Create Optical Circuit"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            create_circuit(bpy, context.scene)
            self.report({"INFO"}, "Created a three-object CPU optical circuit.")
            return {"FINISHED"}


    class NEURO3D_OT_trace_optical_circuit(bpy.types.Operator):
        bl_idname = "neuro3d.trace_optical_circuit"
        bl_label = "Trace Optical Pulse (CPU)"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            try:
                result = trace_circuit(bpy, context.scene)
            except (KeyError, TypeError, ValueError) as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
            self.report({"INFO"}, f"{result.reason}: received intensity {result.intensity:.6f}")
            return {"FINISHED"}


    class NEBULA_OT_build_cpu_preview(bpy.types.Operator):
        bl_idname = "nebula.build_cpu_preview"
        bl_label = "Build Legacy Visual Preview"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            build_cpu_preview_scene()
            self.report({"INFO"}, "Neuro3D CPU preview created; GPU remains dormant.")
            return {"FINISHED"}


    class NEBULA_PT_panel(bpy.types.Panel):
        bl_label = "Neuro3D"
        bl_idname = "NEURO3D_PT_panel"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Neuro3D"

        def draw(self, context):
            self.layout.label(text="Scene-driven optical circuit (CPU)")
            self.layout.operator(NEURO3D_OT_create_optical_circuit.bl_idname)
            self.layout.operator(NEURO3D_OT_trace_optical_circuit.bl_idname)
            self.layout.separator()
            self.layout.label(text="Legacy visual preview")
            self.layout.operator(NEBULA_OT_build_cpu_preview.bl_idname)


    _CLASSES = (
        NEURO3D_OT_create_optical_circuit,
        NEURO3D_OT_trace_optical_circuit,
        NEBULA_OT_build_cpu_preview,
        NEBULA_PT_panel,
    )

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
