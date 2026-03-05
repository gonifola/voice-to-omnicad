# UI Panel — Voice to OmniCAD

import bpy
from . import voice_engine
from . import grok_bridge
from . import executor
from .sacred_geometry import (
    flower_of_life, metatrons_cube, platonic_solids, star_mother, stellated_compound
)


# ── Main Panel ───────────────────────────────────────────────

class VOICECAD_PT_MainPanel(bpy.types.Panel):
    bl_label      = "Voice to OmniCAD"
    bl_idname     = "VOICECAD_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = 'Voice CAD'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Say it. Build it. Print it.", icon='SPEAKER')
        layout.separator()

        # Voice controls
        row = layout.row()
        row.scale_y = 2.0
        row.operator("voicecad.start_listening", text="▶  Start Voice", icon='REC')
        row = layout.row()
        row.operator("voicecad.stop_listening",  text="■  Stop Voice",  icon='SNAP_FACE')
        layout.separator()

        # Manual text input
        layout.label(text="Manual Command:")
        layout.prop(context.scene, "voicecad_manual_command", text="")
        layout.operator("voicecad.execute_command", text="Execute", icon='PLAY')
        layout.separator()

        # AI backend indicator
        prefs_box = layout.box()
        prefs_box.label(text="AI Backend:", icon='SETTINGS')
        try:
            from . import config
            prefs_box.label(text=f"  {config.AI_BACKEND.upper()} → {config.CLAUDE_MODEL if config.AI_BACKEND == 'claude' else config.GROK_MODEL}")
        except Exception:
            prefs_box.label(text="  (check config.py)")
        layout.separator()

        # Sacred geometry quick buttons
        layout.label(text="Sacred Geometry:", icon='MESH_ICOSPHERE')
        col = layout.column(align=True)
        col.operator("voicecad.flower_of_life",      text="Flower of Life")
        col.operator("voicecad.metatrons_cube",      text="Metatron's Cube")
        col.operator("voicecad.platonic_solids",     text="All Platonic Solids")
        col.separator()
        col.operator("voicecad.star_mother",         text="★ Star Mother")
        col.operator("voicecad.stellated_compound",  text="◆ Stellated Compound")

        layout.separator()
        layout.operator("voicecad.export_stl", text="Export STL", icon='EXPORT')


# ── Operators ────────────────────────────────────────────────

class VOICECAD_OT_StartListening(bpy.types.Operator):
    bl_idname = "voicecad.start_listening"
    bl_label  = "Start Voice Listening"

    def execute(self, context):
        ve = voice_engine.VoiceCapture()
        ve.start_listening()
        self.report({'INFO'}, "Voice listening started")
        return {'FINISHED'}


class VOICECAD_OT_StopListening(bpy.types.Operator):
    bl_idname = "voicecad.stop_listening"
    bl_label  = "Stop Voice Listening"

    def execute(self, context):
        self.report({'INFO'}, "Voice listening stopped")
        return {'FINISHED'}


class VOICECAD_OT_ExecuteCommand(bpy.types.Operator):
    bl_idname = "voicecad.execute_command"
    bl_label  = "Execute Voice Command"

    def execute(self, context):
        command = context.scene.voicecad_manual_command
        if not command:
            self.report({'WARNING'}, "No command entered")
            return {'CANCELLED'}

        bridge = grok_bridge.AIBridge()
        code   = bridge.interpret_command(command)
        if not code:
            self.report({'ERROR'}, "AI did not return code — check API key in config.py")
            return {'CANCELLED'}

        exec_engine = executor.SafeExecutor()
        result      = exec_engine.execute(code, original_command=command)

        if result["success"]:
            self.report({'INFO'}, f"Done: {command[:60]}")
        else:
            self.report({'ERROR'}, f"Error: {result.get('error','?')}")
        return {'FINISHED'}


# Sacred geometry quick-launch operators

class VOICECAD_OT_FlowerOfLife(bpy.types.Operator):
    bl_idname = "voicecad.flower_of_life"
    bl_label  = "Flower of Life"
    def execute(self, context):
        flower_of_life.create_flower_of_life()
        return {'FINISHED'}


class VOICECAD_OT_MetatronsCube(bpy.types.Operator):
    bl_idname = "voicecad.metatrons_cube"
    bl_label  = "Metatron's Cube"
    def execute(self, context):
        metatrons_cube.create_metatrons_cube()
        return {'FINISHED'}


class VOICECAD_OT_PlatonicSolids(bpy.types.Operator):
    bl_idname = "voicecad.platonic_solids"
    bl_label  = "All Platonic Solids"
    def execute(self, context):
        platonic_solids.create_all_platonic_solids()
        return {'FINISHED'}


class VOICECAD_OT_StarMother(bpy.types.Operator):
    bl_idname = "voicecad.star_mother"
    bl_label  = "Star Mother (All 5 Nested Solids)"
    def execute(self, context):
        # star_mother.py is a self-contained script — call its main entry point
        try:
            star_mother.main()
        except AttributeError:
            # If no main(), exec it as a script
            import types
            ns = types.ModuleType("star_mother_run")
            ns.bpy = __import__("bpy")
            ns.bmesh = __import__("bmesh")
            ns.math  = __import__("math")
            exec(open(star_mother.__file__).read(), vars(ns))
        return {'FINISHED'}


class VOICECAD_OT_StellatedCompound(bpy.types.Operator):
    bl_idname = "voicecad.stellated_compound"
    bl_label  = "Stellated Ico-Dodec Compound"
    def execute(self, context):
        try:
            stellated_compound.main()
        except AttributeError:
            import types
            ns = types.ModuleType("stellated_run")
            ns.bpy = __import__("bpy")
            ns.bmesh = __import__("bmesh")
            ns.math  = __import__("math")
            exec(open(stellated_compound.__file__).read(), vars(ns))
        return {'FINISHED'}


class VOICECAD_OT_ExportSTL(bpy.types.Operator):
    bl_idname  = "voicecad.export_stl"
    bl_label   = "Export Active Object as STL"
    bl_description = "Exports the active (selected) object to /tmp/omnicad_export.stl"
    def execute(self, context):
        if not context.active_object:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        bpy.ops.export_mesh.stl(filepath="/tmp/omnicad_export.stl", use_selection=True)
        self.report({'INFO'}, "Exported to /tmp/omnicad_export.stl")
        return {'FINISHED'}


# ── Registration ─────────────────────────────────────────────

CLASSES = [
    VOICECAD_PT_MainPanel,
    VOICECAD_OT_StartListening,
    VOICECAD_OT_StopListening,
    VOICECAD_OT_ExecuteCommand,
    VOICECAD_OT_FlowerOfLife,
    VOICECAD_OT_MetatronsCube,
    VOICECAD_OT_PlatonicSolids,
    VOICECAD_OT_StarMother,
    VOICECAD_OT_StellatedCompound,
    VOICECAD_OT_ExportSTL,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.voicecad_manual_command = bpy.props.StringProperty(
        name="Command",
        description="Type a natural language command",
        default="",
    )


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.voicecad_manual_command
