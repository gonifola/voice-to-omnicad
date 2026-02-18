# Voice to OmniCAD - Blender Addon
# Say it. Build it. Print it.

bl_info = {
    "name": "Voice to OmniCAD",
    "author": "williamjackson1111",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Voice CAD",
    "description": "Voice-controlled 3D modeling for sacred geometry",
    "category": "3D View",
}

import bpy
from . import ui_panel
from . import voice_engine
from . import grok_bridge
from . import executor
from . import sacred_geometry

def register():
    ui_panel.register()
    print("Voice to OmniCAD registered")

def unregister():
    ui_panel.unregister()
    print("Voice to OmniCAD unregistered")

if __name__ == "__main__":
    register()
