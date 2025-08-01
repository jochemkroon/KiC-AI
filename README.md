# KiCad AI Assistant

**Intelligent AI assistant for KiCad PCB design with real-time component pricing via Nexar API**

![KiCad Plugin](https://img.shields.io/badge/KiCad-Plugin-blue)
![AI Powered](https://img.shields.io/badge/AI-Powered-green)
![Nexar API](https://img.shields.io/badge/Nexar-API-orange)

## 🚀 Key Features

- **Real-time Component Pricing**: Multi-distributor pricing from Digi-Key, Mouser, Farnell, Newark, Arrow, etc.
- **AI-Powered Design Assistant**: Context-aware suggestions and optimizations
- **Free Tier Available**: 1,000 API calls/month with Nexar API (no credit card required)
- **Seamless Integration**: Works directly within KiCad interface
- **🌍 Multilingual Support**: Choose from 6 languages (English, Nederlands, Deutsch, Español, Français, Português)

## 📋 Quick Setup

### 1. Install Plugin
**For most users**: Download [kicad-ai-assistant.zip](kicad-ai-assistant.zip) and extract to your KiCad plugins directory:
- **Windows**: `%USERPROFILE%\Documents\KiCad\scripting\plugins\`
- **macOS**: `~/Documents/KiCad/scripting/plugins/`  
- **Linux**: `~/.kicad_plugins/`

### 2. Get Free API Access
1. Visit https://portal.nexar.com
2. Create free account (1K calls/month)
3. Create app and get API token
4. Set environment: `export NEXAR_TOKEN="your_token"`

### 3. Start Using
Open KiCad → Tools → AI Assistant and start getting real component pricing!

## 💡 Demo Mode
Works immediately without API token using realistic demo data for testing.

## 📋 Requirements

- **KiCad 9.0+**
- **Python 3.7+**
- **Ollama** with `llama3.2:3b` model
- **requests** Python package

## 🚀 Installation

### Method 1: KiCad Plugin Manager (Recommended)

1. **Download the plugin ZIP**: [kic-ai-assistant-v1.4.5-final.zip](kic-ai-assistant-v1.4.5-final.zip)
2. Open KiCad → **Plugin and Content Manager**
3. Click **Install from File**
4. Select the downloaded ZIP file
5. Restart KiCad

### Method 2: Manual Installation

1. Download and extract the plugin
2. Copy to your KiCad plugins directory:
   - **Windows**: `%APPDATA%/kicad/9.0/scripting/plugins/`
   - **macOS**: `~/Library/Application Support/kicad/9.0/scripting/plugins/`
   - **Linux**: `~/.config/kicad/9.0/scripting/plugins/`

## 🔧 Setup

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

### 2. Install AI Model

```bash
ollama pull llama3.2:3b
```

### 3. Start Ollama Server

```bash
ollama serve
```

## 💡 Usage

### How to Use KIC-AI Assistant

1. **Open your KiCad project in PCB Editor** (File → Open → your_project.kicad_pcb)
2. **Click the KIC-AI robot icon** in the PCB Editor toolbar  
3. **Choose analysis mode**:
   - **Schematic/Circuit**: Analyze component values, connections, and circuit design
   - **PCB Layout**: Analyze component placement, routing, and board layout
4. **Select language**: Choose from 6 supported languages
5. **Select AI interaction mode**:
   - **🔍 Analysis Mode**: Safe recommendations only
   - **📋 Advisory Mode**: Step-by-step guidance with confirmation
   - **🤖 Assistant Mode**: Interactive assistance and future automation
6. **Start chatting**: Ask questions or click "Analyze" for automatic analysis

### Dual Mode Capabilities

#### 📋 Schematic Mode
- Circuit analysis and component review
- Component value validation  
- Net connectivity analysis
- Circuit design recommendations
- Component selection advice

#### 🔧 PCB Mode  
- PCB layout analysis
- Component placement optimization
- Routing suggestions
- Design rule checking tips
- Manufacturing considerations

### AI Interaction Modes

#### 🔍 Analysis Mode (Safe)
- **What it does**: Analyzes your design and provides recommendations
- **Safety**: No modifications to your project
- **Best for**: All users, learning, getting design insights

#### 📋 Advisory Mode (Guided) 
- **What it does**: Provides step-by-step instructions with user confirmation
- **Safety**: Guides you through changes with clear steps
- **Best for**: Users who want detailed guidance 

#### 🤖 Assistant Mode (Interactive)
- **What it does**: Detailed step-by-step instructions and component-specific guidance
- **Safety**: Advanced features for experienced users
- **Best for**: Power users, complex design tasks

### Example Questions

**Schematic Mode:**
- "Review the power supply circuit"
- "Check if R1 value is appropriate" 
- "Analyze the op-amp configuration"
- "Are there any missing decoupling capacitors?"

**PCB Mode:**
- "How can I improve the routing on this PCB?"
- "Are there any potential EMI issues?"
- "What's the best way to place these components?"
- "Can you review my power distribution?"

## 🌍 Language Support

The plugin supports 6 languages with native AI responses:
- 🇬🇧 English
- 🇳🇱 Nederlands (Dutch)
- 🇩🇪 Deutsch (German)
- 🇪🇸 Español (Spanish)
- 🇫🇷 Français (French)
- 🇵🇹 Português (Portuguese)

## 🛠️ Troubleshooting

### Common Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`

**"Requests module not available"**
- Install requests: `pip install requests`

**Plugin doesn't appear in KiCad**
- Check plugin installation path
- Restart KiCad completely
- Check KiCad logs for errors

## 📁 Project Structure

```
kic-ai-assistant/
├── plugins/
│   ├── __init__.py          # Plugin registration
│   ├── ai_dialog.py         # Main dialog and AI integration
│   └── robot_icon.png       # Plugin icon
├── screenshots/             # Interface screenshots
├── README.md               # This file
├── INSTALL.md              # Detailed installation guide
├── CHANGELOG.md            # Version history
├── metadata.json           # Plugin metadata
└── LICENSE                 # MIT License
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for KiCad, the amazing open-source PCB design suite
- Powered by Ollama for local AI processing
- Thanks to the KiCad community for their support and feedback
