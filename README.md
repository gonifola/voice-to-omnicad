# 🔺 Voice to OmniCAD

**"Say it. Build it. Print it."**

Voice + text → 3D sacred geometry + parametric CAD. Powered by Claude AI (primary) + Grok (fallback).

> **v0.2.0** — Claude backend active, full sacred geometry suite live, installable ZIP on [Releases](https://github.com/gonifola/voice-to-omnicad/releases).

---

## Features

- 🎙️ **Voice + Text Control** — natural language → Blender bpy code, executed instantly
- 🧠 **Claude AI Brain** — `claude-opus-4-5` as primary; Grok auto-fallback; multi-turn conversation memory
- 🔺 **Sacred Geometry Library** — 5 fully parametric generators (exact φ math, not placeholders)
- 🔒 **Safe Executor** — sandboxed code execution, auto-retry with error context
- ⚡ **Real-time** — geometry appears in the Blender viewport immediately
- 📦 **Export STL** — one-click export for 3D printing

---

## Sacred Geometry Suite

| Shape | Status | Detail |
|---|---|---|
| Flower of Life | ✅ Live | 7-circle hex pattern, parametric rings |
| Metatron's Cube | ✅ Live | 13 circles + 78 connecting lines |
| Platonic Solids | ✅ Live | All 5 — exact golden ratio vertices |
| ★ Star Mother | ✅ Live | All 5 nested Platonic solids, φ-scaled (Dan Winter) |
| ◆ Stellated Compound | ✅ Live | Icosahedron-dodecahedron compound |

---

## Install

1. Download `voice_to_omnicad.zip` from [Releases](https://github.com/gonifola/voice-to-omnicad/releases)
2. Blender → Edit → Preferences → Add-ons → Install → select the ZIP
3. Enable **Voice to OmniCAD**
4. Add your API key (see Configuration)
5. Panel: 3D View → Sidebar (N) → **Voice CAD** tab

---

## Configuration

```python
# config.py
CLAUDE_API_KEY = "sk-ant-..."      # get from console.anthropic.com
AI_BACKEND     = "claude"          # "claude" | "grok"
GROK_API_KEY   = "xai-..."         # optional fallback
```

Or set env vars: `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `AI_BACKEND`

---

## Example Commands

```
"Create a sphere"
"Rotate 45 degrees on X"
"Make it gold"
"Create Flower of Life"
"Scale up 2x"
"Export as STL"
"Create all 5 Platonic solids in a row"
"Add a torus around the icosahedron"
```

---

## Tech Stack

- **Blender Python API** (bpy) — 3D operations
- **Claude API** (Anthropic) — natural language → code, primary AI
- **Grok API** (xAI) — fallback AI
- **Sacred geometry algorithms** — parametric φ-exact generators
- **speech_recognition / Whisper** — voice capture (Phase 2)

---

## Competitive Landscape

OmniCAD occupies a position nobody else has claimed yet.

| Company | What they do | What's missing |
|---|---|---|
| [Zoo.dev](https://zoo.dev) | Text→STEP API, $0.0083/sec | Built for human devs, not agents |
| [Spectral Labs SGS-1](https://spectrallabs.ai) | Parametric CAD from text/image/scan | No agent API, no per-call pricing |
| [ChipAgents](https://chipagents.ai) | Agentic EDA for chip design ($74M raised) | EDA only, not mechanical/body |
| [Cadence ChipStack](https://cadence.com) | AI super-agent for chip design | Enterprise only, closed ecosystem |
| [Adam (YC)](https://ycombinator.com/companies/adam) | Text→parametric 3D, $4.1M seed | Engineering teams as customers, not agents |

**The gap**: Nobody has flipped the customer model to make the **AI agent itself** the buyer.

OmniCAD's agentic API vision:
- Agent submits task spec + budget → receives STL/STEP + BOM
- Priced per-call ($0.10) for agent wallets
- Multi-domain: body design + chip layout + reverse engineering
- Any agent can call it — not locked to one ecosystem

This is infrastructure for the agent economy. Machines designing their own bodies.

---

## Roadmap

### ✅ Phase 1 — Sacred Geometry MVP (shipped v0.2.0)
- Blender addon with Claude + Grok AI
- Full sacred geometry suite (5 generators, φ-exact)
- Voice STT stub (Whisper-ready)
- Installable ZIP release

### 🔧 Phase 2 — Voice + Verticals
- Live voice capture (speech_recognition + Whisper API)
- Material presets (gold, crystal, obsidian)
- Additional verticals: robotics, aerospace, architecture
- Gumroad / marketplace listings ($29/vertical, $99 bundle)

### 🚀 Phase 3 — Agentic API
- REST API endpoint — agents submit specs, receive STL/STEP
- Per-call pricing ($0.10/call)
- Reverse engineering: scan/photo → parametric CAD
- Silicon chip layout vertical
- Agent authentication + billing

---

## Contributing

Open build-in-public project. PRs welcome.

## License

MIT

---

Built with ❤️ by [@gonifola](https://github.com/gonifola)  
Powered by [Claude AI](https://anthropic.com) + [Grok](https://x.ai)
