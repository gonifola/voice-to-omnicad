# Configuration file for Voice to OmniCAD

# Grok API Settings
GROK_API_KEY = "YOUR_GROK_API_KEY_HERE"  # Get from https://x.ai
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-beta"

# Voice Settings
VOICE_LANGUAGE = "en-US"
VOICE_TIMEOUT = 5  # seconds
VOICE_PHRASE_TIME_LIMIT = 10  # seconds

# Sacred Geometry Defaults
DEFAULT_RADIUS = 1.0
DEFAULT_SPACING = 3.0

# Safety Settings
MAX_EXECUTION_TIME = 5  # seconds
ALLOWED_MODULES = ['bpy', 'math', 'mathutils']
