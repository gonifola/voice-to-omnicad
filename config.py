# Configuration — Voice to OmniCAD
import os

# ── Claude API (primary — you have credits) ─────────────────
CLAUDE_API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE")
CLAUDE_API_URL   = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL     = "claude-opus-4-5"      # best reasoning; swap to claude-haiku-3 for speed

# ── xAI Grok API (fallback) ─────────────────────────────────
GROK_API_KEY     = os.environ.get("XAI_API_KEY", "YOUR_GROK_API_KEY_HERE")
GROK_API_URL     = "https://api.x.ai/v1/chat/completions"
GROK_MODEL       = "grok-3-latest"

# ── Active backend ───────────────────────────────────────────
# "claude" | "grok"  — switch here or via env AI_BACKEND
AI_BACKEND       = os.environ.get("AI_BACKEND", "claude")

# ── Voice ───────────────────────────────────────────────────
VOICE_LANGUAGE          = "en-US"
VOICE_TIMEOUT           = 5   # seconds
VOICE_PHRASE_TIME_LIMIT = 15  # seconds

# ── Sacred geometry defaults ─────────────────────────────────
DEFAULT_RADIUS  = 1.0
DEFAULT_SPACING = 3.0

# ── Safety ──────────────────────────────────────────────────
MAX_EXECUTION_TIME = 10
ALLOWED_MODULES    = ['bpy', 'math', 'mathutils']

# ── Conversation ────────────────────────────────────────────
MAX_CONVERSATION_HISTORY = 20
