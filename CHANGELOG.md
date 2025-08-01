# Changelog

## [1.5.0-MCP] - 2025-08-01

### 🚀 Major New Features - MCP Integration
- **Model Context Protocol (MCP) Support**: Revolutionary integration enabling AI to access external tools and databases
- **Component Database Integration**: Real-time component pricing, availability, and specifications
- **Enhanced AI Analysis**: PCB analysis now includes cost estimation and stock availability
- **Smart Component Suggestions**: AI can suggest alternatives based on pricing, availability, and specifications
- **MCP Server Framework**: Extensible architecture for adding new data sources and tools

### 🔧 Technical Improvements
- **MCP Client**: Full MCP protocol implementation for external tool integration
- **Async Processing**: Non-blocking component database queries
- **Safety Controls**: User confirmation required for all automated suggestions
- **Error Handling**: Graceful fallback when MCP services are unavailable
- **Configuration System**: Easy setup and management of MCP servers

### 📊 Enhanced Capabilities
- **Cost Analysis**: "Your PCB costs €12.34 with 45 components"
- **Availability Checking**: Real-time stock level verification
- **Alternative Components**: Smart suggestions for better/cheaper parts
- **Supply Chain Intelligence**: Integration ready for Digi-Key, Mouser APIs

### 🛡️ Safety & Reliability
- **Safety Mode**: All MCP modifications require user approval
- **Backward Compatibility**: Plugin works normally without MCP
- **Graceful Degradation**: Automatic fallback to basic mode if MCP fails

### 📁 New Files
- `plugins/mcp_client.py` - MCP protocol client implementation
- `plugins/mcp_config.json` - MCP server configuration
- `mcp_servers/component_db.py` - Sample component database server
- `MCP_SETUP.md` - Installation and configuration guide

## [1.4.5] - 2025-07-31

### Documentation & UX Improvements
- **Clarified Usage Instructions**: Updated README to clearly explain plugin is accessed via PCB Editor toolbar
- **Better User Guidance**: Enhanced dialogs to explain analysis mode selection
- **Improved Error Handling**: Clear messaging when no project is loaded
- **Updated Documentation**: Accurate description of how dual-mode analysis works

### Bug Fixes
- Fixed user expectations about toolbar location (PCB Editor only, not Schematic Editor)
- Improved context selection dialog with clearer explanations
- Better handling of empty/no project scenarios

## [1.2.0] - 2025-07-30

### Major Features Added
- **Dual Analysis Mode**: Plugin now offers both PCB Layout and Schematic/Circuit analysis modes
- **Smart Context Selection**: User can choose between analyzing circuit design or PCB layout
- **Schematic Analysis**: Complete circuit analysis with component grouping, value analysis, and net connectivity
- **Enhanced User Guidance**: Clear dialogs explain analysis options and project requirements

### New Schematic/Circuit Analysis Capabilities
- Circuit component analysis grouped by type (R, C, L, U, etc.)
- Net connectivity analysis for schematic review
- Component value and footprint validation
- Circuit topology insights and design recommendations
- Circuit-focused AI prompts and responses

### Enhanced User Experience
- Context selection dialog when launching plugin
- Dynamic button labels: "Analyze PCB" or "Analyze Schematic" based on selected mode
- Mode-specific welcome messages and capabilities
- Better error handling and user guidance for project loading
- Clear instructions when no project is loaded

### Technical Improvements
- Dual-context architecture supporting both PCB and circuit analysis workflows
- Enhanced AI system prompts tailored for circuit design vs PCB layout advice
- Improved component data collection for schematic analysis
- Better integration with KiCad's design data structures

### Important Usage Notes
- Plugin is accessed through PCB Editor toolbar (KiCad limitation)
- Can analyze both schematic and PCB data from the same interface
- User selects analysis focus when plugin starts
- Requires loaded KiCad project (.kicad_pcb file)

## [1.1.3] - 2025-07-30

### Fixed
- Plugin icon now displays correctly in KiCad toolbar using Fabrication Toolkit pattern
- Implemented proper icon support with both icon_file_name and dark_icon_file_name
- Fixed ActionPlugin initialization following KiCad best practices
- All UI text and comments now in English for consistency

### Improved  
- Plugin initialization follows established KiCad plugin patterns
- Better icon handling for both light and dark themes
- Cleaner codebase with English documentation

## [1.1.2] - 2025-07-30

### Added
- Robot icon for better toolbar appearance
- Detailed component analysis with specific component information
- Enhanced AI context with full PCB data for every user question
- Specific component lookup capabilities (e.g., asking about "R1" or specific resistors)

### Improved
- AI now provides specific answers referencing actual component values and positions
- Better PCB context integration for targeted component questions
- Increased context window for more detailed analysis
- Enhanced conversation memory with PCB awareness

### Fixed
- Plugin icon now displays properly in KiCad toolbar
- AI responses now reference specific components instead of giving generic answers

## [1.1.1] - 2025-07-30log

All notable changes to the KIC-AI Assistant plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-30

### Added
- **Conversation Memory**: AI now remembers previous messages in the conversation
- **Context Management**: Maintains last 20 messages for contextual responses
- **Show Context Button**: View what the AI remembers from your conversation
- **Improved Prompting**: Enhanced system prompts for better context awareness
- **Larger Context Window**: Increased to 4096 tokens for longer conversations

### Changed
- **Enhanced AI Responses**: AI can now reference previous questions and build upon earlier discussions
- **Better Context Handling**: PCB analysis results are included in conversation context
- **Improved Welcome Message**: Updated to explain conversation memory feature

### Fixed
- **Conversation Continuity**: AI no longer treats each message as isolated
- **Memory Management**: Automatic cleanup of old messages to prevent memory issues

## [1.0.0] - 2025-07-29

### Added
- Initial release of KIC-AI Assistant
- AI-powered chat interface for PCB design assistance
- Automatic PCB analysis functionality
- Ollama integration with llama3.2:3b model
- Real-time design advice and suggestions
- English interface with larger, readable fonts
- Support for KiCad 6.0+
- Component analysis and statistics
- Net and track information display
- Board dimension reporting
- Design best practices recommendations

### Features
- **Chat Interface**: Interactive dialog for asking PCB design questions
- **PCB Analysis**: Click-button analysis of current PCB design
- **AI Responses**: Context-aware responses using local LLM
- **Privacy-First**: All AI processing happens locally via Ollama
- **User-Friendly**: Large fonts and clear English interface

### Requirements
- KiCad 6.0 or higher
- Python 3.7+
- Ollama with llama3.2:3b model
- requests Python package

### Installation
- Plugin installable via KiCad Plugin and Content Manager
- Also supports manual installation
