# Safe code executor for bpy commands — Voice to OmniCAD

import bpy
import traceback
import time


class SafeExecutor:
    """Executes generated bpy code with safety checks and auto-retry via Grok."""
    
    ALLOWED_MODULES = ['bpy', 'math', 'mathutils']
    FORBIDDEN_PATTERNS = [
        'import os', 'import sys', 'import subprocess',
        'import shutil', 'import socket', 'import http',
        '__import__', 'open(',  # prevent file I/O except bpy
        'exec(', 'eval(',       # prevent nested execution
    ]
    
    def __init__(self):
        self.history = []
        self.grok_bridge = None  # Set by addon init
    
    def execute(self, code, original_command=None, auto_retry=True):
        """Execute bpy code with safety sandbox.
        
        Args:
            code: Python code string to execute
            original_command: The NL command that produced this code (for error recovery)
            auto_retry: If True, ask Grok to fix failed code and retry once
        
        Returns:
            dict with 'success', 'code', and optionally 'error'
        """
        if not code or not code.strip():
            return {"success": False, "error": "Empty code received"}
        
        # Safety check
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in code:
                return {"success": False, "error": f"Blocked: {pattern}"}
        
        try:
            # Create restricted namespace
            namespace = {
                'bpy': bpy,
                '__builtins__': {
                    'range': range,
                    'len': len,
                    'print': print,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'tuple': tuple,
                    'dict': dict,
                    'set': set,
                    'True': True,
                    'False': False,
                    'None': None,
                    'abs': abs,
                    'min': min,
                    'max': max,
                    'round': round,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sorted': sorted,
                    'reversed': reversed,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                }
            }
            
            # Allow math and mathutils
            if 'math' in code:
                import math
                namespace['math'] = math
            
            if 'mathutils' in code:
                import mathutils
                namespace['mathutils'] = mathutils
            
            # Execute with timeout tracking
            start_time = time.time()
            exec(code, namespace)
            exec_time = time.time() - start_time
            
            # Log success
            self.history.append({
                "command": original_command or "(direct code)",
                "code": code,
                "success": True,
                "exec_time": round(exec_time, 3)
            })
            
            return {"success": True, "code": code, "exec_time": exec_time}
            
        except Exception as e:
            error_msg = str(e)
            full_traceback = traceback.format_exc()
            print(f"Voice to OmniCAD execution error: {error_msg}")
            
            # Log failure
            self.history.append({
                "command": original_command or "(direct code)",
                "code": code,
                "success": False,
                "error": error_msg
            })
            
            # Auto-retry: ask Grok to fix the code
            if (auto_retry and self.grok_bridge and original_command):
                print("Voice to OmniCAD: Asking Grok to fix the error...")
                fixed_code = self.grok_bridge.fix_failed_code(
                    original_command, code, error_msg
                )
                if fixed_code and fixed_code != code:
                    print("Voice to OmniCAD: Retrying with fixed code...")
                    return self.execute(
                        fixed_code, 
                        original_command=original_command,
                        auto_retry=False  # Only retry once
                    )
            
            return {"success": False, "error": error_msg, "code": code}
    
    def undo_last(self):
        """Undo the last executed command"""
        bpy.ops.ed.undo()
        if self.history:
            self.history.pop()
    
    def get_history(self, limit=10):
        """Get recent execution history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear execution history"""
        self.history = []
