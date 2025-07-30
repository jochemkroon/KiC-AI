# KIC-AI Assistant Installation Guide

## Quick Install (Recommended)

1. **Download** the latest release: `kic-ai-assistant-v1.3.0-with-screenshots.zip`
2. **Open KiCad** → Plugin and Content Manager
3. **Click** "Install from File"
4. **Select** the downloaded ZIP file
5. **Restart KiCad**

## Prerequisites

Before using the plugin, ensure you have:

### 1. Ollama Setup
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2:3b
ollama serve
```

### 2. Python Requirements
```bash
pip install requests
```

## Manual Installation

If the Plugin Manager doesn't work:

### Windows
Copy plugin to: `%APPDATA%/kicad/9.0/scripting/plugins/`

### macOS
Copy plugin to: `~/Library/Application Support/kicad/9.0/scripting/plugins/`

### Linux
Copy plugin to: `~/.config/kicad/9.0/scripting/plugins/`

## First Run

1. **Open PCB Editor** (not Schematic Editor!)
2. **Look for robot icon** 🤖 in toolbar
3. **Choose interaction mode**:
   - 🔍 Analysis (Safe for beginners)
   - 📋 Advisory (Step-by-step guidance)
   - 🤖 Assistant (Advanced features)

## Troubleshooting

### Plugin doesn't appear
- ✅ Check KiCad version (9.0+ required)
- ✅ Restart KiCad after installation
- ✅ Look in PCB Editor, not Schematic Editor

### AI doesn't respond
- ✅ Start Ollama: `ollama serve`
- ✅ Install model: `ollama pull llama3.2:3b`
- ✅ Check internet connection
- ✅ Install requests: `pip install requests`

### Permission errors
- ✅ Run KiCad as administrator (Windows)
- ✅ Check plugin directory permissions
- ✅ Use Plugin Manager instead of manual copy

## Support

- 📖 See README.md for detailed usage
- 🔄 Check CHANGELOG.md for latest features  
- 📋 Read UPGRADE_NOTES.md for version changes
- 🐛 Report issues on GitHub

---
**Quick Start**: Install → Start Ollama → Open PCB Editor → Click 🤖 → Choose Analysis Mode → Start chatting!
