# UI Panel — Voice to OmniCAD v0.3.0

import bpy
from . import voice_engine
from . import grok_bridge
from . import executor
from . import materials
from .sacred_geometry import (
    flower_of_life, metatrons_cube, platonic_solids,
    star_mother, stellated_compound,
    sri_yantra, merkaba, fibonacci_spiral, torus_knot,
)


# ── State ────────────────────────────────────────────────────

_voice_capture = None   # singleton VoiceCapture


# ── Main Panel ───────────────────────────────────────────────

class VOICECAD_PT_MainPanel(bpy.types.Panel):
    bl_label       = "Voice to OmniCAD"
    bl_idname      = "VOICECAD_PT_main"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Voice CAD"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Say it. Build it. Print it.", icon="SPEAKER")
        layout.separator()

        # ── Voice Controls ───────────────────────────────────
        box = layout.box()
        box.label(text="Voice Input (Whisper):", icon="REC")
        row = box.row(align=True)
        row.scale_y = 1.8
        row.operator("voicecad.start_listening", text="▶ Listen", icon="PLAY")
        row.operator("voicecad.stop_listening",  text="■ Stop",   icon="SNAP_FACE")

        # ── Manual Command ───────────────────────────────────
        layout.separator()
        layout.label(text="Type a Command:")
        layout.prop(context.scene, "voicecad_manual_command", text="")
        layout.operator("voicecad.execute_command", text="Execute", icon="PLAY")

        # ── AI Backend ───────────────────────────────────────
        layout.separator()
        box = layout.box()
        box.label(text="AI Backend:", icon="SETTINGS")
        try:
            from . import config
            box.label(text=f"  {config.AI_BACKEND.upper()} — {config.CLAUDE_MODEL if config.AI_BACKEND == 'claude' else config.GROK_MODEL}")
        except Exception:
            box.label(text="  (check config.py)")

        # ── Sacred Geometry ──────────────────────────────────
        layout.separator()
        layout.label(text="Sacred Geometry:", icon="MESH_ICOSPHERE")
        col = layout.column(align=True)
        col.operator("voicecad.flower_of_life",     text="Flower of Life")
        col.operator("voicecad.metatrons_cube",     text="Metatron's Cube")
        col.operator("voicecad.platonic_solids",    text="All Platonic Solids")
        col.separator()
        col.operator("voicecad.star_mother",        text="★ Star Mother")
        col.operator("voicecad.stellated_compound", text="◆ Stellated Compound")
        col.separator()
        col.operator("voicecad.sri_yantra",         text="✦ Sri Yantra")
        col.operator("voicecad.merkaba",            text="⬡ Merkaba")
        col.operator("voicecad.fibonacci_spiral",   text="〜 Fibonacci Spiral")
        col.operator("voicecad.torus_knot",         text="∞ Torus Knot (3,2)")

        # ── Material Presets ─────────────────────────────────
        layout.separator()
        layout.label(text="Materials:", icon="MATERIAL")
        row = layout.row(align=True)
        row.operator("voicecad.mat_gold",     text="Gold")
        row.operator("voicecad.mat_crystal",  text="Crystal")
        row.operator("voicecad.mat_obsidian", text="Obsidian")

        # ── Export ───────────────────────────────────────────
        layout.separator()
        layout.operator("voicecad.export_stl", text="Export STL", icon="EXPORT")


# ── Voice operators ──────────────────────────────────────────

class VOICECAD_OT_StartListening(bpy.types.Operator):
    bl_idname = "voicecad.start_listening"
    bl_label  = "Start Voice Listening"

    def execute(self, context):
        global _voice_capture
        _voice_capture = voice_engine.VoiceCapture()

        def on_transcript(text):
            # Run command in main thread via timer
            context.scene.voicecad_manual_command = text
            bpy.ops.voicecad.execute_command("INVOKE_DEFAULT")

        _voice_capture.start_listening(callback=on_transcript)
        self.report({"INFO"}, "Listening… speak your command")
        return {"FINISHED"}


class VOICECAD_OT_StopListening(bpy.types.Operator):
    bl_idname = "voicecad.stop_listening"
    bl_label  = "Stop Voice Listening"

    def execute(self, context):
        global _voice_capture
        if _voice_capture:
            _voice_capture.stop_listening()
        self.report({"INFO"}, "Voice stopped")
        return {"FINISHED"}


class VOICECAD_OT_ExecuteCommand(bpy.types.Operator):
    bl_idname = "voicecad.execute_command"
    bl_label  = "Execute Voice Command"

    def execute(self, context):
        command = context.scene.voicecad_manual_command
        if not command:
            self.report({"WARNING"}, "No command entered")
            return {"CANCELLED"}

        bridge      = grok_bridge.AIBridge()
        code        = bridge.interpret_command(command)
        if not code:
            self.report({"ERROR"}, "AI did not return code — check API key in config.py")
            return {"CANCELLED"}

        exec_engine = executor.SafeExecutor()
        result      = exec_engine.execute(code, original_command=command)

        if result["success"]:
            self.report({"INFO"}, f"Done: {command[:60]}")
        else:
            self.report({"ERROR"}, f"Error: {result.get('error','?')}[:120]")
        return {"FINISHED"}


# ── Sacred geometry operators ────────────────────────────────

class VOICECAD_OT_FlowerOfLife(bpy.types.Operator):
    bl_idname = "voicecad.flower_of_life"
    bl_label  = "Flower of Life"
    def execute(self, context):
        flower_of_life.create_flower_of_life()
        return {"FINISHED"}

class VOICECAD_OT_MetatronsCube(bpy.types.Operator):
    bl_idname = "voicecad.metatrons_cube"
    bl_label  = "Metatron's Cube"
    def execute(self, context):
        metatrons_cube.create_metatrons_cube()
        return {"FINISHED"}

class VOICECAD_OT_PlatonicSolids(bpy.types.Operator):
    bl_idname = "voicecad.platonic_solids"
    bl_label  = "All Platonic Solids"
    def execute(self, context):
        platonic_solids.create_all_platonic_solids()
        return {"FINISHED"}

class VOICECAD_OT_StarMother(bpy.types.Operator):
    bl_idname = "voicecad.star_mother"
    bl_label  = "Star Mother"
    def execute(self, context):
        try: star_mother.main()
        except AttributeError: exec(open(star_mother.__file__).read())
        return {"FINISHED"}

class VOICECAD_OT_StellatedCompound(bpy.types.Operator):
    bl_idname = "voicecad.stellated_compound"
    bl_label  = "Stellated Compound"
    def execute(self, context):
        try: stellated_compound.main()
        except AttributeError: exec(open(stellated_compound.__file__).read())
        return {"FINISHED"}

class VOICECAD_OT_SriYantra(bpy.types.Operator):
    bl_idname = "voicecad.sri_yantra"
    bl_label  = "Sri Yantra"
    def execute(self, context):
        sri_yantra.create_sri_yantra()
        return {"FINISHED"}

class VOICECAD_OT_Merkaba(bpy.types.Operator):
    bl_idname = "voicecad.merkaba"
    bl_label  = "Merkaba"
    def execute(self, context):
        merkaba.create_merkaba()
        return {"FINISHED"}

class VOICECAD_OT_FibonacciSpiral(bpy.types.Operator):
    bl_idname = "voicecad.fibonacci_spiral"
    bl_label  = "Fibonacci Spiral"
    def execute(self, context):
        fibonacci_spiral.create_fibonacci_spiral()
        return {"FINISHED"}

class VOICECAD_OT_TorusKnot(bpy.types.Operator):
    bl_idname = "voicecad.torus_knot"
    bl_label  = "Torus Knot (3,2)"
    def execute(self, context):
        torus_knot.create_torus_knot(p=3, q=2)
        return {"FINISHED"}


# ── Material operators ────────────────────────────────────────

class VOICECAD_OT_MatGold(bpy.types.Operator):
    bl_idname = "voicecad.mat_gold"
    bl_label  = "Apply Gold"
    def execute(self, context):
        if context.active_object:
            materials.apply_gold(context.active_object)
        return {"FINISHED"}

class VOICECAD_OT_MatCrystal(bpy.types.Operator):
    bl_idname = "voicecad.mat_crystal"
    bl_label  = "Apply Crystal"
    def execute(self, context):
        if context.active_object:
            materials.apply_crystal(context.active_object)
        return {"FINISHED"}

class VOICECAD_OT_MatObsidian(bpy.types.Operator):
    bl_idname = "voicecad.mat_obsidian"
    bl_label  = "Apply Obsidian"
    def execute(self, context):
        if context.active_object:
            materials.apply_obsidian(context.active_object)
        return {"FINISHED"}


# ── Export ────────────────────────────────────────────────────

class VOICECAD_OT_ExportSTL(bpy.types.Operator):
    bl_idname = "voicecad.export_stl"
    bl_label  = "Export Active Object as STL"
    def execute(self, context):
        if not context.active_object:
            self.report({"WARNING"}, "No active object selected")
            return {"CANCELLED"}
        bpy.ops.export_mesh.stl(filepath="/tmp/omnicad_export.stl", use_selection=True)
        self.report({"INFO"}, "Exported to /tmp/omnicad_export.stl")
        return {"FINISHED"}


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
    VOICECAD_OT_SriYantra,
    VOICECAD_OT_Merkaba,
    VOICECAD_OT_FibonacciSpiral,
    VOICECAD_OT_TorusKnot,
    VOICECAD_OT_MatGold,
    VOICECAD_OT_MatCrystal,
    VOICECAD_OT_MatObsidian,
    VOICECAD_OT_ExportSTL,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.voicecad_manual_command = bpy.props.StringProperty(
        name="Command",
        description="Type or speak a natural language command",
        default="",
    )


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.voicecad_manual_command
