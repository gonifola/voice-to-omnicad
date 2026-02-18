# Safe code executor for bpy commands

import bpy
import traceback

class SafeExecutor:
    """Executes generated bpy code with safety checks"""
    
    ALLOWED_MODULES = ['bpy', 'math', 'mathutils']
    
    def __init__(self):
        self.history = []
    
    def execute(self, code):
        """Execute bpy code with safety sandbox"""
        
        # Basic safety check - prevent dangerous operations
        forbidden = ['import os', 'import sys', 'exec(', 'eval(', '__import__']
        for bad in forbidden:
            if bad in code:
                return {"success": False, "error": f"Forbidden operation: {bad}"}
        
        try:
            # Create restricted namespace
            namespace = {
                'bpy': bpy,
                '__builtins__': {
                    'range': range,
                    'len': len,
                    'print': print,
                }
            }
            
            # Allow math for rotations
            if 'math' in code:
                import math
                namespace['math'] = math
            
            if 'mathutils' in code:
                import mathutils
                namespace['mathutils'] = mathutils
            
            # Execute
            exec(code, namespace)
            
            # Log to history
            self.history.append({
                "code": code,
                "success": True,
                "timestamp": bpy.context.scene.frame_current
            })
            
            return {"success": True, "code": code}
            
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"Execution error: {error_msg}")
            
            self.history.append({
                "code": code,
                "success": False,
                "error": str(e),
                "timestamp": bpy.context.scene.frame_current
            })
            
            return {"success": False, "error": str(e)}
    
    def undo_last(self):
        """Undo the last executed command"""
        bpy.ops.ed.undo()
        if self.history:
            self.history.pop()
