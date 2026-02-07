bl_info = {
    "name": "Sloths Blender Tools",
    "author": "Nw Stoner",
    "version": (1, 4, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar (N) > Sloth's Carx Tools",
    "description": "Sloth's Carx Blender Tools.",
    "category": "Object",
}

import bpy
import os
import bmesh
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, PointerProperty, FloatProperty


# =====================================================
# Settings (shared UI properties)
# =====================================================
class SLOTHS_Settings(PropertyGroup):

    # Tool #2
    disconnect_alpha_inputs: BoolProperty(
        name="Disconnect Alpha Inputs",
        description="Remove node links feeding Principled Alpha",
        default=True,
    )

    # Tool #3
    roughness_value: FloatProperty(
        name="Roughness",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )
    disconnect_roughness_inputs: BoolProperty(
        name="Disconnect Roughness Inputs",
        default=True,
    )

    # Tool #4
    png_convert_dds: BoolProperty(name=".dds → .png", default=True)
    png_convert_jpg: BoolProperty(name=".jpg/.jpeg → .png", default=True)
    png_convert_webp: BoolProperty(name=".webp → .png", default=True)

    # Tool #5
    clean_trees_area_threshold: FloatProperty(
        name="Area Threshold",
        description="Smaller = stricter face similarity",
        default=0.01,
        min=0.0,
        max=1.0,
    )


# =====================================================
# Tool #1 — Clear Custom Split Normals
# =====================================================
class SLOTHS_OT_clear_custom_split_normals_selected(Operator):
    bl_idname = "sloths.clear_custom_split_normals_selected"
    bl_label = "Clear Custom Split Normals (Selected)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == "MESH"]
        if not meshes:
            self.report({"WARNING"}, "No mesh objects selected")
            return {"CANCELLED"}

        view_layer = context.view_layer
        original_active = view_layer.objects.active
        original_mode = context.mode

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        for obj in meshes:
            view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.mode_set(mode="OBJECT")

        if original_active:
            view_layer.objects.active = original_active
        if original_mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")

        self.report({"INFO"}, f"Cleared split normals on {len(meshes)} objects")
        return {"FINISHED"}


# =====================================================
# Tool #2 — Remove Alpha
# =====================================================
class SLOTHS_OT_remove_alpha_all_materials(Operator):
    bl_idname = "sloths.remove_alpha_all_materials"
    bl_label = "Remove Alpha From All Materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        s = context.scene.sloths_settings
        changed = 0

        for mat in bpy.data.materials:
            if not mat:
                continue

            if hasattr(mat, "blend_method"):
                mat.blend_method = "OPAQUE"
            if hasattr(mat, "shadow_method"):
                mat.shadow_method = "OPAQUE"

            if mat.use_nodes and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        alpha = node.inputs.get("Alpha")
                        if alpha:
                            alpha.default_value = 1.0
                            if s.disconnect_alpha_inputs and alpha.is_linked:
                                for l in list(alpha.links):
                                    mat.node_tree.links.remove(l)
                        changed += 1
                        break

        self.report({"INFO"}, f"Updated {changed} materials")
        return {"FINISHED"}


# =====================================================
# Tool #3 — Set Roughness
# =====================================================
class SLOTHS_OT_set_all_materials_roughness(Operator):
    bl_idname = "sloths.set_all_materials_roughness"
    bl_label = "Set Roughness For All Materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        s = context.scene.sloths_settings
        changed = 0

        for mat in bpy.data.materials:
            if mat and mat.use_nodes and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        rough = node.inputs.get("Roughness")
                        if rough:
                            rough.default_value = s.roughness_value
                            if s.disconnect_roughness_inputs and rough.is_linked:
                                for l in list(rough.links):
                                    mat.node_tree.links.remove(l)
                            changed += 1
                        break

        self.report({"INFO"}, f"Roughness set on {changed} materials")
        return {"FINISHED"}


# =====================================================
# Tool #4 — Remap Image Paths
# =====================================================
class SLOTHS_OT_remap_image_paths_to_png(Operator):
    bl_idname = "sloths.remap_image_paths_to_png"
    bl_label = "Remap Image Paths to .png"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        s = context.scene.sloths_settings
        convert_ext = set()

        if s.png_convert_dds:
            convert_ext.add(".dds")
        if s.png_convert_jpg:
            convert_ext.update({".jpg", ".jpeg"})
        if s.png_convert_webp:
            convert_ext.add(".webp")

        changed = 0

        for mat in bpy.data.materials:
            if not mat or not mat.use_nodes:
                continue

            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
                    base, ext = os.path.splitext(node.image.filepath)
                    if ext.lower() in convert_ext:
                        new_path = base + ".png"
                        node.image.filepath = new_path
                        node.name = os.path.basename(new_path)
                        node.image.name = node.name
                        changed += 1

        self.report({"INFO"}, f"Remapped {changed} textures")
        return {"FINISHED"}


# =====================================================
# Tool #5 — Clean Trees
# =====================================================
class SLOTHS_OT_clean_trees_selected(Operator):
    bl_idname = "sloths.clean_trees_selected"
    bl_label = "Clean Trees (Selected)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        threshold = context.scene.sloths_settings.clean_trees_area_threshold
        meshes = [o for o in context.selected_objects if o.type == "MESH"]
        view_layer = context.view_layer
        original_active = view_layer.objects.active

        bpy.ops.object.mode_set(mode="OBJECT")

        for obj in meshes:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(type="FACE")

            bm = bmesh.from_edit_mesh(obj.data)
            if not bm.faces:
                bpy.ops.object.mode_set(mode="OBJECT")
                continue

            for f in bm.faces:
                f.select = False

            largest = max(bm.faces, key=lambda f: f.calc_area())
            largest.select = True
            bmesh.update_edit_mesh(obj.data)

            bpy.ops.mesh.select_similar(type="AREA", threshold=threshold)
            bpy.ops.mesh.select_all(action="INVERT")
            bpy.ops.mesh.delete(type="FACE")

            bpy.ops.object.mode_set(mode="OBJECT")

        if original_active:
            view_layer.objects.active = original_active

        self.report({"INFO"}, f"Cleaned {len(meshes)} tree objects")
        return {"FINISHED"}


# =====================================================
# UI Panel (FIXED VIEW_3D)
# =====================================================
class SLOTHS_PT_tools_panel(Panel):
    bl_label = "Sloth's Tools"
    bl_idname = "SLOTHS_PT_tools_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sloth's Tools"

    def draw(self, context):
        s = context.scene.sloths_settings
        layout = self.layout

        box = layout.box()
        box.label(text="Geometry")
        box.operator("sloths.clear_custom_split_normals_selected")

        box = layout.box()
        box.label(text="Materials")
        box.prop(s, "disconnect_alpha_inputs")
        box.operator("sloths.remove_alpha_all_materials")
        box.separator()
        box.prop(s, "roughness_value")
        box.prop(s, "disconnect_roughness_inputs")
        box.operator("sloths.set_all_materials_roughness")

        box = layout.box()
        box.label(text="Textures")
        row = box.row()
        row.prop(s, "png_convert_dds")
        row.prop(s, "png_convert_jpg")
        row.prop(s, "png_convert_webp")
        box.operator("sloths.remap_image_paths_to_png")

        box = layout.box()
        box.label(text="Clean Trees")
        box.prop(s, "clean_trees_area_threshold")
        box.operator("sloths.clean_trees_selected")


# =====================================================
# Registration
# =====================================================
classes = (
    SLOTHS_Settings,
    SLOTHS_OT_clear_custom_split_normals_selected,
    SLOTHS_OT_remove_alpha_all_materials,
    SLOTHS_OT_set_all_materials_roughness,
    SLOTHS_OT_remap_image_paths_to_png,
    SLOTHS_OT_clean_trees_selected,
    SLOTHS_PT_tools_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sloths_settings = PointerProperty(type=SLOTHS_Settings)

def unregister():
    del bpy.types.Scene.sloths_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
