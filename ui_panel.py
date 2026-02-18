# Blender UI Panel

import bpy
from . import voice_engine
from . import grok_bridge
from . import executor

class VOICECAD_PT_MainPanel(bpy.types.Panel):
    """Voice to OmniCAD control panel"""
    bl_label = "Voice to OmniCAD"
    bl_idname = "VOICECAD_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Voice CAD'
    
    def draw(self, context):
        layout = self.layout
        
        # Title
        layout.label(text="Say it. Build it. Print it.", icon='SPEAKER')
        layout.separator()
        
        # Voice controls
        row = layout.row()
        row.scale_y = 2.0
        row.operator("voicecad.start_listening", text="Start Voice", icon='REC')
        
        row = layout.row()
        row.operator("voicecad.stop_listening", text="Stop Voice", icon='SNAP_FACE')
        
        layout.separator()
        
        # Manual text input (for testing)
        layout.label(text="Manual Command:")
        layout.prop(context.scene, "voicecad_manual_command", text="")
        layout.operator("voicecad.execute_command", text="Execute", icon='PLAY')
        
        layout.separator()
        
        # Sacred geometry quick menu
        layout.label(text="Sacred Geometry:", icon='MESH_ICOSPHERE')
        layout.operator("voicecad.flower_of_life", text="Flower of Life")
        layout.operator("voicecad.metatrons_cube", text="Metatron's Cube")
        layout.operator("voicecad.platonic_solids", text="Platonic Solids")

class VOICECAD_OT_StartListening(bpy.types.Operator):
    bl_idname = "voicecad.start_listening"
    bl_label = "Start Voice Listening"
    
    def execute(self, context):
        # TODO: Start voice capture
        self.report({'INFO'}, "Voice listening started")
        return {'FINISHED'}

class VOICECAD_OT_StopListening(bpy.types.Operator):
    bl_idname = "voicecad.stop_listening"
    bl_label = "Stop Voice Listening"
    
    def execute(self, context):
        # TODO: Stop voice capture
        self.report({'INFO'}, "Voice listening stopped")
        return {'FINISHED'}

class VOICECAD_OT_ExecuteCommand(bpy.types.Operator):
    bl_idname = "voicecad.execute_command"
    bl_label = "Execute Voice Command"
    
    def execute(self, context):
        command = context.scene.voicecad_manual_command
        
        if not command:
            self.report({'WARNING'}, "No command entered")
            return {'CANCELLED'}
        
        # Send to Grok
        bridge = grok_bridge.GrokBridge()
        code = bridge.interpret_command(command)
        
        if not code:
            self.report({'ERROR'}, "Failed to interpret command")
            return {'CANCELLED'}
        
        # Execute bpy code
        exec_engine = executor.SafeExecutor()
        result = exec_engine.execute(code)
        
        if result["success"]:
            self.report({'INFO'}, f"Executed: {command}")
        else:
            self.report({'ERROR'}, f"Error: {result.get('error', 'Unknown')}")
        
        return {'FINISHED'}

class VOICECAD_OT_FlowerOfLife(bpy.types.Operator):
    bl_idname = "voicecad.flower_of_life"
    bl_label = "Create Flower of Life"
    
    def execute(self, context):
        # TODO: Import sacred_geometry module
        self.report({'INFO'}, "Flower of Life created")
        return {'FINISHED'}

class VOICECAD_OT_MetatronsCube(bpy.types.Operator):
    bl_idname = "voicecad.metatrons_cube"
    bl_label = "Create Metatron's Cube"
    
    def execute(self, context):
        # TODO: Import sacred_geometry module
        self.report({'INFO'}, "Metatron's Cube created")
        return {'FINISHED'}

class VOICECAD_OT_PlatonicSolids(bpy.types.Operator):
    bl_idname = "voicecad.platonic_solids"
    bl_label = "Create Platonic Solids"
    
    def execute(self, context):
        # TODO: Import sacred_geometry module
        self.report({'INFO'}, "Platonic Solids created")
        return {'FINISHED'}

def register():
    # Register property for manual command input
    bpy.types.Scene.voicecad_manual_command = bpy.props.StringProperty(
        name="Command",
        description="Enter a voice command manually",
        default=""
    )
    
    bpy.utils.register_class(VOICECAD_PT_MainPanel)
    bpy.utils.register_class(VOICECAD_OT_StartListening)
    bpy.utils.register_class(VOICECAD_OT_StopListening)
    bpy.utils.register_class(VOICECAD_OT_ExecuteCommand)
    bpy.utils.register_class(VOICECAD_OT_FlowerOfLife)
    bpy.utils.register_class(VOICECAD_OT_MetatronsCube)
    bpy.utils.register_class(VOICECAD_OT_PlatonicSolids)

def unregister():
    del bpy.types.Scene.voicecad_manual_command
    
    bpy.utils.unregister_class(VOICECAD_PT_MainPanel)
    bpy.utils.unregister_class(VOICECAD_OT_StartListening)
    bpy.utils.unregister_class(VOICECAD_OT_StopListening)
    bpy.utils.unregister_class(VOICECAD_OT_ExecuteCommand)
    bpy.utils.unregister_class(VOICECAD_OT_FlowerOfLife)
    bpy.utils.unregister_class(VOICECAD_OT_MetatronsCube)
    bpy.utils.unregister_class(VOICECAD_OT_PlatonicSolids)
