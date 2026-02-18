# Grok API integration — Voice to OmniCAD
# Uses xAI Grok API for natural language → bpy code generation

import json
import os
import bpy

try:
    import requests
except ImportError:
    requests = None


class GrokBridge:
    """Communicates with xAI Grok API to interpret ANY natural language command
    and generate executable Blender Python (bpy) code.
    
    Supports:
    - Arbitrary natural language (not just keywords)
    - Multi-turn conversation context
    - Scene-aware commands ("make it bigger", "change its color")
    - Sacred geometry generation
    - Complex multi-step operations
    - Error recovery and code fixing
    """
    
    SYSTEM_PROMPT = """You are the AI brain inside "Voice to OmniCAD" — a Blender addon that lets users control Blender entirely through natural language voice commands.

Your job: take ANY natural language input and produce ONLY executable Blender Python (bpy) code. Nothing else — no markdown, no explanations, no code fences, no comments. Just raw Python that Blender can exec().

You have full access to:
- bpy (Blender Python API)
- math, mathutils
- All bpy.ops.mesh.primitive_* operations
- bpy.context and bpy.data for scene manipulation
- Material/shader node creation
- Modifiers (subdivision, mirror, boolean, array, etc.)
- Animation keyframes
- Import/export operations

## RULES:
1. Output ONLY executable Python code. No prose. No markdown. No ```python blocks.
2. Always import math or mathutils at the top if you use them.
3. For ambiguous references like "it", "that", "the object" — use bpy.context.active_object
4. For "make it bigger/smaller" — scale the active object
5. For colors — create/assign materials with the requested color
6. For sacred geometry — generate precise mathematical geometry:
   - Flower of Life: overlapping circles (radius R, 7-circle seed pattern)
   - Metatron's Cube: 13 circles with all connecting lines
   - Sri Yantra: 9 interlocking triangles
   - Seed of Life: 7 overlapping circles
   - Platonic Solids: tetrahedron, cube, octahedron, dodecahedron, icosahedron
   - Merkaba: two interpenetrating tetrahedra
   - Fibonacci Spiral: golden ratio spiral mesh
   - Torus Knot: parametric torus knots
7. For multi-step commands ("create a sphere, make it red, and duplicate it 5 times in a circle"), output ALL steps as sequential code
8. If the user says "undo" or "go back", output: bpy.ops.ed.undo()
9. If the user says "redo", output: bpy.ops.ed.redo()
10. If the user says "delete" or "remove", delete the active object or selection
11. If the user says "save", output: bpy.ops.wm.save_mainfile()
12. For STL export: bpy.ops.export_mesh.stl(filepath='/tmp/export.stl')
13. When creating multiple objects, use clear naming: obj.name = "descriptive_name"
14. Deselect all before creating new objects: bpy.ops.object.select_all(action='DESELECT')
15. If a command makes no sense in Blender context, output a print() statement explaining why, e.g.: print("I can't do that — Blender doesn't support time travel... yet.")

## SCENE CONTEXT:
You may receive scene context showing current objects, active object, and selection state. Use this to resolve references like "make it red" (= active object) or "move them apart" (= selected objects).

## CONVERSATION HISTORY:
You may receive previous commands and results. Use this for contextual commands like "now rotate that 45 degrees" or "do the same thing but bigger".
"""

    def __init__(self, api_key=None):
        from . import config
        # Priority: explicit arg > env var > config file
        self.api_key = (api_key 
                       or os.environ.get("XAI_API_KEY") 
                       or config.GROK_API_KEY)
        self.api_url = config.GROK_API_URL
        self.model = config.GROK_MODEL
        self.conversation_history = []
        self.max_history = 20  # Keep last 20 exchanges for context
    
    def get_scene_context(self):
        """Build a snapshot of the current Blender scene for Grok context"""
        ctx = []
        
        # Active object
        active = bpy.context.active_object
        if active:
            ctx.append(f"Active object: '{active.name}' (type: {active.type}, "
                      f"location: {tuple(round(v, 2) for v in active.location)}, "
                      f"scale: {tuple(round(v, 2) for v in active.scale)})")
            if active.active_material:
                ctx.append(f"  Material: '{active.active_material.name}'")
        else:
            ctx.append("No active object")
        
        # Selected objects
        selected = bpy.context.selected_objects
        if selected:
            names = [o.name for o in selected[:10]]  # Limit to 10
            ctx.append(f"Selected ({len(selected)}): {names}")
        
        # Scene objects summary
        all_objs = bpy.context.scene.objects
        type_counts = {}
        for obj in all_objs:
            type_counts[obj.type] = type_counts.get(obj.type, 0) + 1
        ctx.append(f"Scene objects ({len(all_objs)}): {dict(type_counts)}")
        
        return "\n".join(ctx)
    
    def interpret_command(self, text_command, include_context=True):
        """Send natural language command to Grok, receive executable bpy code.
        
        Args:
            text_command: Any natural language string
            include_context: Whether to include scene state and conversation history
        
        Returns:
            String of executable Python code, or None on failure
        """
        if requests is None:
            print("Voice to OmniCAD: 'requests' library not installed. "
                  "Run: pip install requests")
            return None
        
        if not self.api_key or self.api_key == "YOUR_GROK_API_KEY_HERE":
            print("Voice to OmniCAD: No API key configured. "
                  "Set env var XAI_API_KEY or update addon preferences.")
            return None
        
        # Build messages
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        # Add scene context
        if include_context:
            scene_ctx = self.get_scene_context()
            messages.append({
                "role": "system",
                "content": f"Current Blender scene state:\n{scene_ctx}"
            })
        
        # Add conversation history for multi-turn context
        for entry in self.conversation_history[-self.max_history:]:
            messages.append({"role": "user", "content": entry["command"]})
            messages.append({"role": "assistant", "content": entry["code"]})
        
        # Add current command
        messages.append({"role": "user", "content": text_command})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            code = result["choices"][0]["message"]["content"].strip()
            
            # Clean up any accidental markdown code fences
            if code.startswith("```"):
                lines = code.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                code = "\n".join(lines)
            
            # Store in conversation history
            self.conversation_history.append({
                "command": text_command,
                "code": code
            })
            
            # Trim history if too long
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            return code
            
        except requests.exceptions.Timeout:
            print("Voice to OmniCAD: Grok API timeout (30s). Try again.")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"Voice to OmniCAD: Grok API HTTP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_body = e.response.json()
                    print(f"  Detail: {err_body}")
                except Exception:
                    pass
            return None
        except Exception as e:
            print(f"Voice to OmniCAD: Grok API error: {e}")
            return None
    
    def fix_failed_code(self, original_command, failed_code, error_message):
        """Ask Grok to fix code that failed to execute.
        
        Returns corrected code or None.
        """
        fix_prompt = (f"The previous code for '{original_command}' failed with error:\n"
                     f"{error_message}\n\n"
                     f"Failed code:\n{failed_code}\n\n"
                     f"Generate corrected bpy code that fixes this error. "
                     f"Output ONLY the fixed code, nothing else.")
        
        return self.interpret_command(fix_prompt, include_context=True)
    
    def clear_history(self):
        """Reset conversation context"""
        self.conversation_history = []
