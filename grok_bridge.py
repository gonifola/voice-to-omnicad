# Grok API integration

import json
import requests

class GrokBridge:
    """Communicates with Grok API to interpret commands and generate bpy code"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "YOUR_GROK_API_KEY_HERE"
        self.api_url = "https://api.x.ai/v1/chat/completions"
    
    def interpret_command(self, text_command):
        """Send text command to Grok, receive bpy code"""
        
        system_prompt = """You are a Blender Python (bpy) code generator.
Given a natural language command, generate ONLY the bpy code to execute it.
Do not include explanations, markdown, or code blocks - just raw executable Python.

Examples:
Input: "create a sphere"
Output: bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))

Input: "rotate 45 degrees on X"
Output: import math\nbpy.context.active_object.rotation_euler[0] = math.radians(45)
"""
        
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_command}
            ],
            "temperature": 0.3
        }
        
        try:
            # TODO: Implement actual API call when API key is configured
            # response = requests.post(self.api_url, 
            #                         headers={"Authorization": f"Bearer {self.api_key}"},
            #                         json=payload)
            # code = response.json()["choices"][0]["message"]["content"]
            
            # Placeholder response
            code = "bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))"
            return code
            
        except Exception as e:
            print(f"Grok API error: {e}")
            return None
