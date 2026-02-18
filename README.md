# 🔺 Voice to OmniCAD

**"Say it. Build it. Print it."**

Voice-controlled 3D modeling addon for Blender focused on sacred geometry. Powered by Grok AI.

## Features

- 🎙️ **Voice Control**: Speak natural commands to create and manipulate 3D objects
- 🧠 **Grok AI Brain**: Interprets natural language and generates Blender Python code
- 🔺 **Sacred Geometry Library**: Pre-built templates for Flower of Life, Metatron's Cube, Platonic Solids, and more
- 🔒 **Safe Execution**: Sandboxed code executor prevents dangerous operations
- ⚡ **Real-time**: See your creations appear instantly in the Blender viewport

## Installation

1. Download this repository as a ZIP file
2. Open Blender → Edit → Preferences → Add-ons
3. Click "Install..." and select the ZIP file
4. Enable "Voice to OmniCAD" checkbox
5. Find the panel in 3D View → Sidebar (press N) → Voice CAD tab

## Usage

### Voice Commands (Coming Soon)

```
"Create a sphere"
"Rotate 45 degrees on X"
"Scale up 2x"
"Make it gold"
"Create Flower of Life"
"Export as STL"
```

### Manual Testing

For now, use the manual command input:

1. Open the Voice CAD panel in the sidebar
2. Type a command in the text field
3. Click "Execute"

### Sacred Geometry Quick Menu

Click the buttons to instantly create:

- **Flower of Life**: 7 circles in hexagonal pattern
- **Metatron's Cube**: 13-circle sacred pattern containing all Platonic solids
- **Platonic Solids**: All 5 perfect solids (Tetrahedron, Cube, Octahedron, Dodecahedron, Icosahedron)

## Configuration

To enable Grok API integration:

1. Get your API key from [x.ai](https://x.ai)
2. Edit `grok_bridge.py`
3. Replace `YOUR_GROK_API_KEY_HERE` with your actual key

## Tech Stack

- **Blender Python API** (bpy) - 3D operations
- **Grok API** (xAI) - Natural language interpretation
- **speech_recognition** - Voice capture (planned)
- **Sacred geometry algorithms** - Parametric generators

## Roadmap

### Phase 1: MVP (Current)
- ✅ Blender addon scaffold
- ✅ UI panel and manual command input
- ⏳ Grok API integration
- ⏳ Voice capture (speech-to-text)
- ⏳ 3 sacred geometry templates

### Phase 2: Polish
- Full sacred geometry library (10+ templates)
- Material presets (gold, crystal, obsidian)
- Undo/redo voice commands
- Command history
- Auto-render previews

### Phase 3: OmniCAD
- OpenSCAD export (precision parametric)
- Tinkercad browser automation (beginner mode)
- Web interface option
- Community gallery

## Sacred Geometry Templates

### Launch
- Flower of Life
- Metatron's Cube
- Seed of Life
- Platonic Solids (all 5)
- Sri Yantra

### Post-Launch
- Merkaba
- Fibonacci Spiral
- Torus Knot
- Tree of Life
- Vesica Piscis

## Contributing

This is an open build-in-public project. PRs welcome!

## License

MIT

## Credits

Built with ❤️ by [@williamjackson1111](https://github.com/williamjackson1111)

Powered by [Grok AI](https://x.ai)
