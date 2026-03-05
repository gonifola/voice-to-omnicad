# AI Bridge — Voice to OmniCAD
# Claude (primary) + Grok (fallback) → natural language → bpy code

import json
import os

try:
    import requests
except ImportError:
    requests = None

try:
    from . import config
except ImportError:
    import config  # standalone use

SYSTEM_PROMPT = """You are the AI brain inside "Voice to OmniCAD" — a Blender addon that lets users control Blender entirely through natural language voice commands.

Your job: take ANY natural language input and produce ONLY executable Blender Python (bpy) code. Nothing else — no markdown, no explanations, no code fences. Just raw Python that Blender can exec().

You have full access to: bpy, math, mathutils, all bpy.ops.mesh.primitive_* operations, bpy.context, bpy.data, materials/shaders, modifiers, animation keyframes, import/export.

## RULES:
1. Output ONLY executable Python. No prose. No ```python blocks. No comments unless they are inline code comments.
2. Always import math or mathutils at the top if used.
3. For "it", "that", "the object" — use bpy.context.active_object.
4. Deselect all before creating new objects: bpy.ops.object.select_all(action='DESELECT')
5. Name objects descriptively: obj.name = "name"
6. For STL export: bpy.ops.export_mesh.stl(filepath='/tmp/export.stl')
7. For "undo": bpy.ops.ed.undo()
8. For "redo": bpy.ops.ed.redo()
9. For "save": bpy.ops.wm.save_mainfile()
10. Multi-step commands — output ALL steps as sequential code.
11. Sacred geometry must use precise golden-ratio math, not placeholders.
12. If a command is impossible in Blender, output: print("Cannot do that in Blender: <reason>")"""


class AIBridge:
    """Communicates with Claude (primary) or Grok (fallback) to generate bpy code."""

    def __init__(self):
        self.history = []
        self.backend  = config.AI_BACKEND

    # ── public API ──────────────────────────────────────────────

    def interpret_command(self, natural_language_command):
        """Translate a natural language command into executable bpy code."""
        self.history.append({"role": "user", "content": natural_language_command})
        if len(self.history) > config.MAX_CONVERSATION_HISTORY * 2:
            self.history = self.history[-config.MAX_CONVERSATION_HISTORY * 2:]

        code = None
        if self.backend == "claude":
            code = self._call_claude()
            if not code:
                print("[OmniCAD] Claude failed, falling back to Grok…")
                code = self._call_grok()
        else:
            code = self._call_grok()
            if not code:
                print("[OmniCAD] Grok failed, falling back to Claude…")
                code = self._call_claude()

        if code:
            self.history.append({"role": "assistant", "content": code})
        return code

    def fix_code(self, original_code, error_message, original_command=None):
        """Ask AI to fix code that threw an error."""
        fix_prompt = f"""The following bpy code raised an error:

ERROR: {error_message}

CODE:
{original_code}

Original user command: {original_command or "unknown"}

Fix the code. Return ONLY the corrected Python, no explanation."""
        return self.interpret_command(fix_prompt)

    def clear_history(self):
        self.history = []

    # ── Claude ──────────────────────────────────────────────────

    def _call_claude(self):
        if not requests:
            return None
        key = config.CLAUDE_API_KEY
        if not key or key == "YOUR_ANTHROPIC_API_KEY_HERE":
            return None
        try:
            resp = requests.post(
                config.CLAUDE_API_URL,
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model":      config.CLAUDE_MODEL,
                    "max_tokens": 2048,
                    "system":     SYSTEM_PROMPT,
                    "messages":   self.history,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"].strip()
        except Exception as e:
            print(f"[OmniCAD] Claude error: {e}")
            return None

    # ── Grok ────────────────────────────────────────────────────

    def _call_grok(self):
        if not requests:
            return None
        key = config.GROK_API_KEY
        if not key or key == "YOUR_GROK_API_KEY_HERE":
            return None
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
        try:
            resp = requests.post(
                config.GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type":  "application/json",
                },
                json={"model": config.GROK_MODEL, "messages": messages, "max_tokens": 2048},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[OmniCAD] Grok error: {e}")
            return None


# ── backwards-compatible alias ───────────────────────────────
GrokBridge = AIBridge
