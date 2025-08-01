# KIC-AI v2.3.0 - Configuration Update

## ✨ New Features

### 🔧 Complete Configuration System
- **Advanced Config Dialog**: Tabbed interface with API Settings, General Settings, and Info
- **Nexar API Key Management**: Store and manage your Nexar API key
- **Persistent Settings**: Configuration saved to `~/.kic-ai/config.json`
- **Demo/API Mode Toggle**: Automatic switching between demo and real API mode

### ⚙️ Configuration Features
- **API Settings Tab**:
  - Nexar API key input (with password masking)
  - Demo mode checkbox
  - Connection testing
  - Status indicators
  
- **General Settings Tab**:
  - AI Mode selection (Analysis, Chat, Expert)
  - Language selection (English, Nederlands, Deutsch, Français)
  
- **Info Tab**:
  - Feature overview
  - Configuration help
  - Contact information

### 🔄 Smart API Integration
- **Automatic Mode Detection**: Uses real API when key is configured, demo otherwise
- **Environment Variable Support**: Falls back to `NEXAR_TOKEN` environment variable
- **Embedded Server Enhancement**: API key passed to embedded Nexar server
- **Status Reporting**: Clear indication of demo vs API mode

## 📋 Usage Instructions

### 1. Install the Plugin
Extract `kicad-ai-assistant-v2.3.0-with-config.zip` to your KiCad plugins directory

### 2. Access Configuration
1. Open KiCad PCBNew or Eeschema
2. Click the robot icon to open KIC-AI Assistant
3. Click the **⚙️ Config** button
4. Navigate through the tabs to configure your settings

### 3. Configure Nexar API (Optional)
1. Go to [Nexar API](https://nexar.com/api) to get your free API key
2. In the Config dialog, enter your API key in the "API Settings" tab
3. Click "💾 Save" to store your configuration
4. Test pricing functionality with real API data

### 4. Demo Mode (Default)
- Works immediately without any API keys
- Provides realistic demo pricing data
- Perfect for testing and evaluation

## 🔧 Technical Details

### Configuration File
- Location: `~/.kic-ai/config.json`
- Contains: API keys, preferences, UI settings
- Automatically created on first save

### API Key Priority
1. Configuration dialog setting
2. Environment variable `NEXAR_TOKEN`
3. Demo mode (fallback)

### New Files Added
- `plugins/config_manager.py`: Complete configuration management system
- Enhanced `plugins/ai_dialog.py`: Integration with config system
- Enhanced `plugins/simple_mcp_client_embedded.py`: API key support

## 🎯 Benefits

1. **Easy API Key Management**: No need to edit files or set environment variables
2. **Persistent Configuration**: Settings remembered across KiCad sessions
3. **Flexible Setup**: Works in demo mode or with real API keys
4. **User-Friendly Interface**: Professional tabbed configuration dialog
5. **Backwards Compatible**: Existing installations continue to work

## 🧪 Testing

The configuration system has been tested with:
- ✅ API key storage and retrieval
- ✅ Demo mode fallback
- ✅ Settings persistence
- ✅ UI integration
- ✅ Embedded server API key passing

## 🚀 Getting Started

1. **Quick Start**: Install and use immediately in demo mode
2. **Full Setup**: Add your Nexar API key for real pricing data
3. **Customize**: Configure AI mode and language preferences

---

**Previous Version**: v2.2.1 (Basic config info dialog)
**Current Version**: v2.3.0 (Full configuration system)
**Next**: Advanced features and additional API integrations
