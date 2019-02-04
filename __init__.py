bl_info = {
    "name": "Aspect Ratio Calculator",
    "author": "Spencer Magnusson",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "description": "Calculates and Generates Settings for Specific Aspect Ratio",
    "support": "COMMUNITY",
    "category": "Render"
}

import bpy
from statistics import median

class ARN_OT_aspect_ratio_node(bpy.types.Operator):
    bl_idname = "node.arn_ot_aspect_ratio_node"
    bl_label = "Create Aspect Ratio Node";
    bl_description = 'Creates Box Matte Node based on given aspect ratio';
    bl_options = {'REGISTER', 'UNDO'}
    
    ratio_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 2,
        step = 1
    )
    
    def execute(self, context):
        # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        #check for box mask and composite nodes
        box_node_label = "Aspect Ratio Mask"
        comp_node = tree.nodes.get('Composite')
        box_node = color_node = tree.nodes.get(box_node_label)

        if box_node is None:
            box_node = tree.nodes.new(type='CompositorNodeBoxMask')
            box_node.name = box_node_label
            box_node.location = -400, 0
            
        if comp_node is None:
            comp_node = tree.nodes.new(type='CompositorNodeComposite')
    
        scene = bpy.context.scene
        #set up aspect ratio node
        if self.ratio_float < (scene.render.resolution_x / scene.render.resolution_y):
            box_node.height = scene.render.resolution_y / scene.render.resolution_x 
            box_node.width = box_node.height * self.ratio_float
        else:
            box_node.width = 1.1
            box_node.height = 1 / self.ratio_float
        box_node.label = str(round(self.ratio_float, 3)) + ":1 aspect ratio"
        
        invert_node_label = "Invert Aspect Ratio mask"
        invert_node = tree.nodes.get(invert_node_label)
        
        if invert_node is None:
            invert_node = tree.nodes.new(type='CompositorNodeInvert')
            invert_node.name = invert_node_label
            invert_node.label = invert_node_label
            invert_node.location = -200, 0
        
        #set up color balance node that uses mask
        ar_node_label = "Aspect Ratio"
        color_node = tree.nodes.get(ar_node_label)

        if color_node is None:
            color_node = tree.nodes.new(type='CompositorNodeColorBalance')
            color_node.label = ar_node_label
            color_node.name = ar_node_label
            color_node.correction_method = 'OFFSET_POWER_SLOPE'
            color_node.slope = (0.0, 0.0, 0.0)
            
        prev_node = comp_node.inputs[0].links[0].from_node
        
        tree.links.new(box_node.outputs[0], invert_node.inputs[1])
        tree.links.new(invert_node.outputs[0], color_node.inputs[0])
        tree.links.new(color_node.outputs[0], comp_node.inputs[0])
        
        if prev_node is not None:
            if prev_node.name != color_node.name:
                tree.links.new(prev_node.outputs[0], color_node.inputs[1])
        
        return {'FINISHED'}

class ARP_PT_aspect_ratio_node(bpy.types.Panel):
    bl_idname = "node.arp_pt_aspect_ratio"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "Aspect Ratio Node"
    bl_category = "Aspect Ratio"
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.tree_type == 'CompositorNodeTree'
    
    def draw(self, context):
        layout = self.layout
        layout.label('Aspect Ratio Node')
        layout.operator(ARN_OT_aspect_ratio_node.bl_idname, text = '4:3 Fullscreen', icon = "OUTLINER_OB_CAMERA").ratio_float = 4 / 3
        layout.operator(ARN_OT_aspect_ratio_node.bl_idname, text = '16:9 Widescreen', icon = "OUTLINER_OB_CAMERA").ratio_float = 16 / 9
        layout.operator(ARN_OT_aspect_ratio_node.bl_idname, text = '21:9 Cinemascope', icon = "OUTLINER_OB_CAMERA").ratio_float = 21 / 9
        layout.prop(context.scene, 'custom_ar_float')
        layout.operator(ARN_OT_aspect_ratio_node.bl_idname, text = 'Custom Aspect Ratio', icon = "CAMERA_DATA").ratio_float = context.scene.custom_ar_float
        
        
class ARRC_OT_aspect_ratio_resolution_calc(bpy.types.Operator):
    bl_idname = "render.arrc_ot_aspect_ratio_resolution_calc"
    bl_label = "Calculates Aspect Ratio Resolution";
    bl_description = 'Calculates the aspect ratio for the render';
    bl_options = {'REGISTER', 'UNDO'}
    
    ratio_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 4,
        step = 1
    )
    
    def execute(self, context):
        # Get the scene
        scene = bpy.context.scene

        # Set render resolution
        scene.render.resolution_y = round(scene.render.resolution_x / self.ratio_float)
        return {'FINISHED'}

class ARRP_PT_aspect_ratio_resolution_panel(bpy.types.Panel):
    bl_idname = "render.arrp_pt_aspect_ratio_resolution_panel"
    bl_label = "Aspect Ratio Calculator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(ARRC_OT_aspect_ratio_resolution_calc.bl_idname, text = '4:3 Fullscreen', icon = "OUTLINER_OB_CAMERA").ratio_float = 4 / 3
        layout.operator(ARRC_OT_aspect_ratio_resolution_calc.bl_idname, text = '16:9 Widescreen', icon = "OUTLINER_OB_CAMERA").ratio_float = 16 / 9
        layout.operator(ARRC_OT_aspect_ratio_resolution_calc.bl_idname, text = '21:9 Cinemascope', icon = "OUTLINER_OB_CAMERA").ratio_float = 21 / 9
        layout.prop(context.scene, 'custom_ar_float')
        layout.operator(ARRC_OT_aspect_ratio_resolution_calc.bl_idname, text = 'Custom Aspect Ratio', icon = "CAMERA_DATA").ratio_float = context.scene.custom_ar_float

classes = (ARN_OT_aspect_ratio_node, ARP_PT_aspect_ratio_node, ARRC_OT_aspect_ratio_resolution_calc, ARRP_PT_aspect_ratio_resolution_panel)

def register():
    # To show the input in the left tool shelf, store 'bpy.props.~'.
    #   In draw() in the subclass of Panel, access the input value by 'context.scene'.
    #   In execute() in the class, access the input value by 'context.scene.float_input'.
    bpy.types.Scene.custom_ar_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 4,
        step = 1
    )
    
    for cls in classes:
        bpy.utils.register_class(cls)
    
 
def unregister():
    del bpy.types.Scene.custom_ar_float
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
