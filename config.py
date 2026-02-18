# Configuration file for Voice to OmniCAD
import os

# xAI Grok API Settings
# Set your API key via environment variable XAI_API_KEY
# or paste it here (not recommended for public repos)
GROK_API_KEY = os.environ.get("XAI_API_KEY", "YOUR_GROK_API_KEY_HERE")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-2-latest"  # Latest Grok 2 model

# Voice Settings
VOICE_LANGUAGE = "en-US"
VOICE_TIMEOUT = 5  # seconds
VOICE_PHRASE_TIME_LIMIT = 15  # seconds (increased for longer commands)

# Sacred Geometry Defaults
DEFAULT_RADIUS = 1.0
DEFAULT_SPACING = 3.0

# Safety Settings
MAX_EXECUTION_TIME = 10  # seconds (increased for complex generations)
ALLOWED_MODULES = ['bpy', 'math', 'mathutils']

# Conversation Settings
MAX_CONVERSATION_HISTORY = 20  # Number of past exchanges to keep for context
