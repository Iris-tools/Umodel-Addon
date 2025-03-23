bl_info = {
    "name": "Auto Apply Material from Props",
    "author": "Iris",
    "version": (1, 1),
    "blender": (2, 83, 6),
    "location": "View3D > Tool Shelf",
    "description": "Apply materials to selected objects based on .props.txt files and textures",
    "category": "Material",
}

import bpy
import os
import json

from bpy.props import StringProperty
from bpy.types import Operator, Panel

def parse_props_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    texture_names = {}
    for key in ['BaseColorMap', 'NormalMap', 'RMHMap']:
        start = content.find(f"Name={key}")
        if start != -1:
            line_start = content.find("Texture2D'", start)
            line_end = content.find("'", line_start + 10)
            if line_start != -1 and line_end != -1:
                texture_full_path = content[line_start+10:line_end]
                tex_name = os.path.basename(texture_full_path)
                if '.' in tex_name:
                    tex_name = tex_name.split('.')[0]
                texture_names[key] = tex_name + '.png'
    return texture_names

def find_file_recursively(root_dir, target_filename):
    for dirpath, _, filenames in os.walk(root_dir):
        if target_filename in filenames:
            return os.path.join(dirpath, target_filename)
    return None

def create_or_update_material(obj, mat_slot_name, tex_dict, root_path):
    mat = bpy.data.materials.get(mat_slot_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_slot_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (300, 0)
    links.new(bsdf.outputs[0], output.inputs[0])

    def add_image_texture_node(label, image_path, loc):
        img = bpy.data.images.load(image_path, check_existing=True)
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.image = img
        tex_node.label = label
        tex_node.location = loc
        return tex_node

    if 'BaseColorMap' in tex_dict:
        base_path = find_file_recursively(root_path, tex_dict['BaseColorMap'])
        if base_path:
            node = add_image_texture_node("BaseColor", base_path, (-400, 200))
            links.new(node.outputs[0], bsdf.inputs['Base Color'])

    if 'NormalMap' in tex_dict:
        normal_path = find_file_recursively(root_path, tex_dict['NormalMap'])
        if normal_path:
            tex_node = add_image_texture_node("Normal", normal_path, (-400, 0))
            normal_map = nodes.new(type="ShaderNodeNormalMap")
            normal_map.location = (-200, 0)
            links.new(tex_node.outputs[0], normal_map.inputs[1])
            links.new(normal_map.outputs[0], bsdf.inputs['Normal'])

    #if 'RMHMap' in tex_dict:
    #    rmh_path = find_file_recursively(root_path, tex_dict['RMHMap'])
    #    if rmh_path:
    #        rmh_node = add_image_texture_node("RMH", rmh_path, (-400, -200))
    #        sep = nodes.new(type="ShaderNodeSeparateRGB")
    #        sep.location = (-200, -200)
    #        links.new(rmh_node.outputs[0], sep.inputs[0])
    #        links.new(sep.outputs['R'], bsdf.inputs['Roughness'])
    #        links.new(sep.outputs['G'], bsdf.inputs['Metallic'])

    return mat

class ApplyMaterialsOperator(Operator):
    bl_idname = "object.apply_materials_from_props"
    bl_label = "Apply Materials"

    def execute(self, context):
        root_path = context.scene.mat_root_path
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            for slot in obj.material_slots:
                if not slot.material:
                    continue
                mat_name = slot.name
                props_file = mat_name + ".props.txt"
                props_path = find_file_recursively(root_path, props_file)
                if not props_path:
                    self.report({'WARNING'}, f"Props not found: {props_file}")
                    continue
                tex_dict = parse_props_file(props_path)
                mat = create_or_update_material(obj, mat_name, tex_dict, root_path)
                slot.material = mat
        return {'FINISHED'}

class MaterialToolsPanel(Panel):
    bl_label = "Material Auto Loader"
    bl_idname = "VIEW3D_PT_material_auto_loader"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Material Tools'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "mat_root_path")
        layout.operator("object.apply_materials_from_props", text="Apply Materials")

def register():
    bpy.utils.register_class(ApplyMaterialsOperator)
    bpy.utils.register_class(MaterialToolsPanel)
    bpy.types.Scene.mat_root_path = StringProperty(name="Root Folder", subtype='DIR_PATH')

def unregister():
    bpy.utils.unregister_class(ApplyMaterialsOperator)
    bpy.utils.unregister_class(MaterialToolsPanel)
    del bpy.types.Scene.mat_root_path

if __name__ == "__main__":
    register()