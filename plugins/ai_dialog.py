# -*- coding: utf-8 -*-
import wx
import pcbnew
import threading
import json
import os

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Import MCP client
try:
    from .mcp_client import MCPClient, KiCadMCPTools
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

class AIAssistantDialog(wx.Frame):
    """AI Assistant Dialog voor PCB en Schematic design hulp met 3 interactie modi"""
    
    def __init__(self, parent, context_type="pcb"):
        # Set title based on context
        title = "KIC-AI Assistant - PCB" if context_type == "pcb" else "KIC-AI Assistant - Schematic"
        super().__init__(parent, title=title, size=(850, 650))
        
        self.context_type = context_type  # "pcb" or "schematic"
        
        # AI Interaction modes
        self.ANALYSIS_MODE = "analysis"      # Safe analysis and suggestions
        self.ADVISORY_MODE = "advisory"      # Step-by-step guidance with confirmation
        self.ASSISTANT_MODE = "assistant"    # Interactive recommendations (future: with actions)
        
        self.interaction_mode = self.ANALYSIS_MODE  # Default to safest mode
        
        # MCP Integration
        self.mcp_client = None
        self.mcp_tools = None
        self.mcp_enabled = False
        
        # Language settings
        self.LANGUAGES = {
            0: {"code": "en", "name": "English"},
            1: {"code": "nl", "name": "Nederlands"},
            2: {"code": "de", "name": "Deutsch"},
            3: {"code": "es", "name": "Español"},
            4: {"code": "fr", "name": "Français"},
            5: {"code": "pt", "name": "Português"}
        }

        
        # Icon instellen (optioneel)
        self.SetIcon(wx.Icon())
        
        # Chat history voor context
        self.conversation_history = []
        
        # UI opzetten
        self.init_ui()
        
        # Initialize MCP if available
        self.init_mcp()
        
        # Centreer op scherm
        self.CenterOnScreen()
        
        # Welcome message based on context
        if context_type == "schematic":
            welcome_msg = ("Welcome to KIC-AI Assistant - Schematic Mode! 📋⚡\n\n"
                          "I can help you with:\n"
                          "• Schematic analysis and review\n"
                          "• Circuit design advice\n"
                          "• Component selection guidance\n"
                          "• Net connectivity analysis\n"
                          "• Symbol and annotation review\n\n"
                          "� Interaction Modes:\n"
                          "• Analysis: Safe recommendations only\n"
                          "• Advisory: Step-by-step guidance\n"
                          "• Assistant: Interactive help (future automation)\n\n"
                          "�💡 I remember our conversation!\n"
                          "Ask me about your circuit design!")
        else:
            welcome_msg = ("Welcome to KIC-AI Assistant - PCB Mode! 🔧🖥️\n\n"
                          "I can help you with:\n"
                          "• PCB layout analysis and advice\n"
                          "• Component placement optimization\n"
                          "• Routing suggestions\n"
                          "• Design rule checking tips\n"
                          "• Manufacturing considerations\n\n"
                          "🔧 Interaction Modes:\n"
                          "• Analysis: Safe recommendations only\n"
                          "• Advisory: Step-by-step guidance\n"
                          "• Assistant: Interactive help (future automation)\n\n"
                          "💡 I remember our conversation!\n"
                          "Ask me about your PCB design!")
        
        self.add_message("🤖 KIC-AI", welcome_msg)
        
    def init_ui(self):
        """Initialiseer de user interface"""
        panel = wx.Panel(self)
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Mode selector
        mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mode_label = wx.StaticText(panel, label="AI Interaction Mode:")
        mode_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        self.mode_choice = wx.Choice(panel, choices=[
            "🔍 Analysis Mode (Safe)",
            "📋 Advisory Mode (Guided)", 
            "🤖 Assistant Mode (Interactive)"
        ])
        self.mode_choice.SetSelection(0)  # Default to Analysis mode
        
        mode_help = wx.Button(panel, label="?", size=(30, -1))
        mode_help.SetToolTip("Click for mode explanations")
        
        mode_sizer.Add(mode_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        mode_sizer.Add(self.mode_choice, 1, wx.EXPAND | wx.RIGHT, 5)
        mode_sizer.Add(mode_help, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(mode_sizer, 0, wx.EXPAND | wx.ALL, 10)
        # Language selector
        lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_label = wx.StaticText(panel, label="Language / Taal:")
        lang_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        self.lang_choice = wx.Choice(panel, choices=[
            "🇬🇧 English",
            "🇳🇱 Nederlands", 
            "🇩🇪 Deutsch",
            "🇪🇸 Español",
            "🇫🇷 Français",
            "🇵🇹 Português"
        ])
        self.lang_choice.SetSelection(0)  # Default to English
        
        lang_sizer.Add(lang_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        lang_sizer.Add(self.lang_choice, 1, wx.EXPAND)
        
        main_sizer.Add(lang_sizer, 0, wx.EXPAND | wx.ALL, 10)

        
        # Chat area
        self.chat_ctrl = wx.TextCtrl(
            panel, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )
        self.chat_ctrl.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # Input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.input_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input_ctrl.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.input_ctrl.SetHint("Type your question here...")
        
        # Buttons
        self.send_btn = wx.Button(panel, label="Send")
        analyze_label = "Analyze Schematic" if self.context_type == "schematic" else "Analyze PCB"
        self.analyze_btn = wx.Button(panel, label=analyze_label)
        self.clear_btn = wx.Button(panel, label="Clear Chat")
        self.context_btn = wx.Button(panel, label="Show Context")
        self.config_btn = wx.Button(panel, label="⚙️ Config")
        self.config_btn.SetToolTip("Open configuration dialog")
        
        # Input layout
        input_sizer.Add(self.input_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_btn, 0, wx.RIGHT, 5)
        input_sizer.Add(self.analyze_btn, 0, wx.RIGHT, 5) 
        input_sizer.Add(self.clear_btn, 0, wx.RIGHT, 5)
        input_sizer.Add(self.context_btn, 0, wx.RIGHT, 5)
        input_sizer.Add(self.config_btn, 0)
        
        # Status bar
        self.status_text = wx.StaticText(panel, label="Ready")
        self.status_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        
        # Main layout
        main_sizer.Add(self.chat_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.status_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        panel.SetSizer(main_sizer)
        
        # Events
        self.bind_events()
        
    def init_mcp(self):
        """Initialize MCP integration if available"""
        if not MCP_AVAILABLE:
            print("MCP not available - import failed")
            return
            
        try:
            # Load MCP configuration
            config_path = os.path.join(os.path.dirname(__file__), 'mcp_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    mcp_config = json.load(f)
                
                print(f"Loaded MCP config: {list(mcp_config.get('mcp_servers', {}).keys())}")
                
                # Initialize MCP client
                self.mcp_client = MCPClient()
                
                # Connect to enabled servers
                connected_servers = []
                for server_name, server_config in mcp_config.get('mcp_servers', {}).items():
                    if server_config.get('enabled', False):
                        print(f"Attempting to connect to MCP server: {server_name}")
                        success = self.mcp_client.connect_server(server_name, server_config)
                        if success:
                            connected_servers.append(server_name)
                            print(f"✅ Connected to MCP server: {server_name}")
                        else:
                            print(f"❌ Failed to connect to MCP server: {server_name}")
                
                # Initialize KiCad MCP tools
                if self.mcp_client and connected_servers:
                    self.mcp_tools = KiCadMCPTools(self.mcp_client)
                    self.mcp_enabled = True
                    
                    # Show available tools
                    available_tools = self.mcp_client.get_available_tools()
                    print(f"MCP Tools available: {available_tools}")
                    
                    # Add welcome message about MCP
                    self.add_message("🔗 MCP Status", 
                                   f"Connected to {len(connected_servers)} MCP servers:\n" +
                                   f"• Servers: {', '.join(connected_servers)}\n" +
                                   f"• Tools: {len(available_tools)} available\n" +
                                   f"• Enhanced pricing and component data enabled!")
                else:
                    print("No MCP servers connected")
            else:
                print(f"MCP config file not found: {config_path}")
                    
        except Exception as e:
            print(f"MCP initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.mcp_enabled = False
        
    def bind_events(self):
        """Bind UI events"""
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        self.analyze_btn.Bind(wx.EVT_BUTTON, self.on_analyze)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        self.context_btn.Bind(wx.EVT_BUTTON, self.on_show_context)
        self.config_btn.Bind(wx.EVT_BUTTON, self.on_config)
        self.mode_choice.Bind(wx.EVT_CHOICE, self.on_mode_change)
        self.input_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_send)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Mode help button (find it in the parent)
        for child in self.GetChildren():
            for subchild in child.GetChildren():
                if isinstance(subchild, wx.Button) and subchild.GetLabel() == "?":
                    subchild.Bind(wx.EVT_BUTTON, self.on_mode_help)
                    break
        
    def add_message(self, sender, message):
        """Add message to chat"""
        timestamp = wx.DateTime.Now().Format("%H:%M")
        formatted_msg = f"[{timestamp}] {sender}:\n{message}\n\n"
        self.chat_ctrl.AppendText(formatted_msg)
        
    def set_status(self, status):
        """Update status tekst"""
        self.status_text.SetLabel(status)
        
    def on_send(self, event):
        """Send user message"""
        message = self.input_ctrl.GetValue().strip()
        if not message:
            return
            
        # Add message
        self.add_message("🟢 You", message)
        self.input_ctrl.Clear()
        
        # Send to AI
        self.process_user_message(message)
        
    def on_analyze(self, event):
        """Analyze current PCB"""
        self.set_status("Analyzing...")
        self.analyze_btn.Enable(False)
        
        # Start analyse in thread
        thread = threading.Thread(target=self.analyze_pcb)
        thread.daemon = True
        thread.start()
        
    def on_clear(self, event):
        """Clear chat history"""
        self.chat_ctrl.Clear()
        self.conversation_history.clear()  # Wis ook conversatie geschiedenis
        self.add_message("🤖 KIC-AI", "Chat cleared. How can I help you?")
        
    def on_mode_change(self, event):
        """Handle AI interaction mode change"""
        selection = self.mode_choice.GetSelection()
        
        if selection == 0:
            self.interaction_mode = self.ANALYSIS_MODE
            mode_name = "Analysis Mode"
            description = "Safe analysis and recommendations only"
        elif selection == 1:
            self.interaction_mode = self.ADVISORY_MODE
            mode_name = "Advisory Mode"
            description = "Step-by-step guidance with user confirmation"
        elif selection == 2:
            self.interaction_mode = self.ASSISTANT_MODE
            mode_name = "Assistant Mode"
            description = "Interactive recommendations and future automation"
        
        self.add_message("⚙️ System", f"Switched to {mode_name}: {description}")
        self.set_status(f"Mode: {mode_name}")
        
    def on_mode_help(self, event):
        """Show mode explanations"""
        help_text = """🔍 Analysis Mode (Safe):
• Analyzes your design and provides recommendations
• No modifications to your project
• Safe for all users and projects

📋 Advisory Mode (Guided):
• Provides step-by-step instructions
• Asks for confirmation before suggesting changes
• Guides you through design improvements

🤖 Assistant Mode (Interactive):
• Interactive design recommendations
• Future: Semi-automatic design assistance
• Advanced features for experienced users

Choose the mode that fits your experience level and comfort with AI assistance."""
        
        self.add_message("ℹ️ Mode Help", help_text)
        
    def on_show_context(self, event):
        """Toon huidige conversatie context"""
        if not self.conversation_history:
            self.add_message("ℹ️ Context", "No conversation history yet.")
            return
            
        context_info = f"📝 Memory: {len(self.conversation_history)//2} exchanges remembered\n\n"
        
        # Show last 4 messages (2 exchanges)
        recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 4 else self.conversation_history
        
        for entry in recent_history:
            role_emoji = "🟢" if entry['role'] == "User" else "🤖"
            content = entry['content'][:150] + "..." if len(entry['content']) > 150 else entry['content']
            context_info += f"{role_emoji} {content}\n\n"
            
        if len(self.conversation_history) > 4:
            context_info += f"(+ {len(self.conversation_history)//2 - 2} older exchanges in memory)"
            
        self.add_message("ℹ️ Context", context_info)
    
    def on_config(self, event):
        """Handle configuration button click"""
        try:
            from config_dialog import ConfigurationDialog
            
            dlg = ConfigurationDialog(self)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    # Configuration was saved, reinitialize MCP
                    self.add_message("ℹ️ System", "Configuration updated. Reinitializing MCP connections...")
                    self.init_mcp()
            finally:
                dlg.Destroy()
        except ImportError as e:
            wx.MessageBox(
                f"Configuration dialog not available: {e}",
                "Configuration Error",
                wx.OK | wx.ICON_ERROR
            )
        except Exception as e:
            wx.MessageBox(
                f"Error opening configuration: {e}",
                "Configuration Error", 
                wx.OK | wx.ICON_ERROR
            )
        
    def analyze_pcb(self):
        """Analyze current design in background thread"""
        try:
            if self.context_type == "schematic":
                # Analyze schematic
                analysis = self.collect_schematic_info()
                analysis_title = "📋 Schematic Analysis"
                ai_prompt = f"Analyze this schematic design and provide circuit advice:\n\n{analysis}"
            else:
                # Analyze PCB
                board = pcbnew.GetBoard()
                if not board:
                    wx.CallAfter(self.add_message, "❌ Error", "No PCB loaded")
                    return
                    
                analysis = self.collect_pcb_info(board)
                analysis_title = "📊 PCB Analysis"
                ai_prompt = f"Analyze this PCB and provide design advice:\n\n{analysis}"
            
            # Toon analyse
            wx.CallAfter(self.add_message, analysis_title, analysis)
            
            # Stuur naar AI voor advies
            self.send_to_ai(ai_prompt, is_analysis=True)
            
        except Exception as e:
            wx.CallAfter(self.add_message, "❌ Error", f"Analysis error: {str(e)}")
        finally:
            wx.CallAfter(self.analyze_btn.Enable, True)
            wx.CallAfter(self.set_status, "Ready")
            
    def collect_pcb_info(self, board):
        """Collect PCB information with specific component details"""
        info = []
        
        # Board info
        title = board.GetTitleBlock().GetTitle()
        info.append(f"PCB: {title if title else 'Unknown'}")
        
        # Afmetingen
        bbox = board.GetBoardEdgesBoundingBox()
        width_mm = bbox.GetWidth() / 1000000.0
        height_mm = bbox.GetHeight() / 1000000.0
        info.append(f"Dimensions: {width_mm:.1f} x {height_mm:.1f} mm")
        
        # Componenten - GEDETAILLEERDE LIJST
        footprints = list(board.GetFootprints())
        info.append(f"Components: {len(footprints)}")
        
        if footprints:
            info.append("\n=== COMPONENT DETAILS ===")
            
            # Sorteer componenten op referentie
            sorted_footprints = sorted(footprints, key=lambda fp: fp.GetReference())
            
            for fp in sorted_footprints:
                ref = fp.GetReference()
                value = fp.GetValue()
                footprint = fp.GetFPID().GetLibItemName()
                
                # Positie
                pos = fp.GetPosition()
                x_mm = pos.x / 1000000.0
                y_mm = pos.y / 1000000.0
                
                # Rotatie
                rotation = fp.GetOrientation().AsDegrees()
                
                # Layer (bovenkant/onderkant)
                layer = "Top" if fp.IsFlipped() == False else "Bottom"
                
                info.append(f"{ref}: {value}")
                info.append(f"  Footprint: {footprint}")
                info.append(f"  Position: ({x_mm:.1f}, {y_mm:.1f}) mm")
                info.append(f"  Rotation: {rotation:.0f}°, Layer: {layer}")
                
                # Pads info
                pads = list(fp.Pads())
                if pads:
                    info.append(f"  Pads: {len(pads)}")
                
                info.append("")  # Lege regel tussen componenten
        
        # Nets met details
        nets = board.GetNetInfo()
        net_count = nets.GetNetCount()
        info.append(f"\n=== NETS ({net_count}) ===")
        
        # Toon belangrijke nets
        for net_code in range(min(10, net_count)):  # Eerste 10 nets
            net = nets.GetNetItem(net_code)
            if net:
                net_name = net.GetNetname()
                if net_name and net_name != "":
                    info.append(f"Net {net_code}: {net_name}")
        
        # Tracks
        tracks = list(board.GetTracks())
        info.append(f"\nTracks: {len(tracks)}")
        
        # Layers
        layer_count = board.GetCopperLayerCount()
        info.append(f"Copper layers: {layer_count}")
        
        return "\n".join(info)
    
    def collect_schematic_info(self):
        """Collect schematic information for analysis"""
        info = []
        
        try:
            # Try to get schematic information via PCB board 
            # (KiCad stores schematic refs in PCB)
            board = pcbnew.GetBoard()
            if not board:
                info.append("No board available for schematic analysis")
                return "\n".join(info)
            
            # Board/Project info
            title = board.GetTitleBlock().GetTitle()
            info.append(f"Project: {title if title else 'Unknown'}")
            
            # Get footprints (which represent schematic symbols)
            footprints = list(board.GetFootprints())
            info.append(f"Components: {len(footprints)}")
            
            if footprints:
                info.append("\n=== SCHEMATIC COMPONENTS ===")
                
                # Group by component type
                components_by_type = {}
                
                for fp in footprints:
                    ref = fp.GetReference()
                    value = fp.GetValue()
                    footprint = fp.GetFPID().GetLibItemName()
                    
                    # Get component type from reference
                    comp_type = ref[0] if ref else "?"
                    
                    if comp_type not in components_by_type:
                        components_by_type[comp_type] = []
                    
                    components_by_type[comp_type].append({
                        'ref': ref,
                        'value': value,
                        'footprint': footprint
                    })
                
                # Show components grouped by type
                for comp_type in sorted(components_by_type.keys()):
                    components = components_by_type[comp_type]
                    info.append(f"\n{comp_type}-type components ({len(components)}):")
                    
                    for comp in sorted(components, key=lambda x: x['ref']):
                        info.append(f"  {comp['ref']}: {comp['value']} ({comp['footprint']})")
            
            # Nets (connections between components)
            nets = board.GetNetInfo()
            net_count = nets.GetNetCount()
            info.append(f"\n=== CONNECTIONS ({net_count} nets) ===")
            
            # Show important nets
            important_nets = []
            for net_code in range(min(15, net_count)):
                net = nets.GetNetItem(net_code)
                if net:
                    net_name = net.GetNetname()
                    if net_name and net_name != "":
                        important_nets.append(net_name)
            
            if important_nets:
                info.append("Key nets:")
                for net_name in important_nets:
                    info.append(f"  • {net_name}")
            
            info.append(f"\nTotal design complexity: {len(footprints)} components, {net_count} connections")
            
        except Exception as e:
            info.append(f"Schematic analysis error: {str(e)}")
            info.append("Note: Full schematic analysis requires KiCad eeschema integration")
        
        return "\n".join(info)
        
    def process_user_message(self, message):
        """Process user message"""
        self.set_status("AI thinking...")
        self.send_btn.Enable(False)
        
        # Check for component-specific guidance in Assistant mode
        specific_guidance = self.get_component_specific_guidance(message)
        if specific_guidance:
            self.add_message("🤖 Assistant", specific_guidance)
            self.send_btn.Enable(True)
            self.set_status("Ready")
            return
        # Start AI processing in thread
        thread = threading.Thread(target=self.send_to_ai, args=(message,))
        thread.daemon = True
        thread.start()
        
    def send_to_ai(self, message, is_analysis=False):
        """Send message to AI (Ollama) with design context"""
        if not REQUESTS_AVAILABLE:
            wx.CallAfter(self.add_message, "❌ Error", "Requests module not available")
            wx.CallAfter(self.send_btn.Enable, True)
            wx.CallAfter(self.set_status, "Ready")
            return
            
        try:
            # Ollama API endpoint
            url = "http://localhost:11434/api/generate"
            
            # Build simple conversation context
            conversation_context = ""
            if self.conversation_history:
                # Include last 4 exchanges (8 messages) for context
                recent_messages = self.conversation_history[-8:]
                conversation_context = "\n\nRecent conversation:\n"
                for msg in recent_messages:
                    conversation_context += f"{msg['role']}: {msg['content'][:200]}...\n"
                conversation_context += "\n"
            
            # Get current design context for user questions
            design_context = ""
            if not is_analysis:
                try:
                    if self.context_type == "schematic":
                        design_context = f"\n\nCURRENT SCHEMATIC CONTEXT:\n{self.collect_schematic_info()}\n"
                    else:
                        board = pcbnew.GetBoard()
                        if board:
                            design_context = f"\n\nCURRENT PCB CONTEXT:\n{self.collect_pcb_info(board)}\n"
                except:
                    pass  # No design available
            
            # Prepare system prompt based on context and interaction mode
            mode_instructions = self.get_mode_instructions()
            language_instructions = self.get_language_prompt()
            
            # Enhanced context with MCP data
            mcp_context = ""
            try:
                mcp_context = self.get_mcp_enhanced_context(message, design_context)
                if mcp_context:
                    print(f"DEBUG: MCP context added: {len(mcp_context)} characters")
                else:
                    print("DEBUG: No MCP context available")
            except Exception as e:
                print(f"DEBUG: MCP context error: {e}")
                mcp_context = ""
            
            # Debug: Print language instructions to verify they're working
            if language_instructions:
                print(f"DEBUG: Language instructions: {language_instructions}")
            
            if is_analysis:
                if self.context_type == "schematic":
                    system_prompt = (f"{language_instructions} "
                                   "You are an expert electronic circuit designer and schematic review specialist. "
                                   "Analyze the provided schematic data thoroughly and provide specific, practical advice. "
                                   "Look at component types, values, connections, and circuit topology. "
                                   "Focus on circuit functionality, component selection, and design best practices. "
                                   f"{mode_instructions} "
                                   "Reference previous conversation if relevant.")
                else:
                    system_prompt = (f"{language_instructions} "
                                   "You are an expert PCB design engineer. Analyze the provided PCB data thoroughly and provide specific, practical advice. "
                                   "Look at individual components, their values, positions, and relationships. "
                                   f"{mode_instructions} "
                                   "Reference previous conversation if relevant.")
            else:
                if self.context_type == "schematic":
                    system_prompt = (f"{language_instructions} "
                                   "You are a helpful schematic design assistant with access to the current schematic design. "
                                   "When users ask about specific components, circuits, or connections, reference the actual schematic data provided. "
                                   "Give specific answers about component values, connections, and circuit topology when possible. "
                                   "Focus on circuit functionality, component selection, and electrical design principles. "
                                   f"{mode_instructions} "
                                   "Remember our conversation and build upon previous topics when relevant.")
                else:
                    system_prompt = (f"{language_instructions} "
                                   "You are a helpful PCB design assistant with access to the current PCB design. "
                                   "When users ask about specific components (like resistors, capacitors, ICs), look up the actual component details from the PCB context provided. "
                                   "Give specific answers referencing actual component values, positions, and designators when possible. "
                                   "If asked about a specific component (e.g., 'R1', 'check this resistor'), find that component in the PCB data and provide detailed information about it. "
                                   f"{mode_instructions} "
                                   "Remember our conversation and build upon previous topics when relevant.")
            
            # Build final prompt with design context
            # Add language instruction again at the end for extra emphasis
            language_reminder = ""
            if language_instructions:
                language_reminder = f"\n\nREMEMBER: {language_instructions}"
            
            # Include MCP enhanced context
            enhanced_context = mcp_context if mcp_context else ""
            
            final_prompt = system_prompt + conversation_context + design_context + enhanced_context + f"\nUser question: {message}\n\nPlease provide a specific, helpful response based on the actual design data when applicable:{language_reminder}"
            
            # API request
            data = {
                "model": "llama3.2:3b",
                "prompt": final_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent language following
                    "top_p": 0.8,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.2,  # Higher penalty to avoid falling back to English
                    "top_k": 20  # Limit choices to make language instruction more effective
                }
            }
            
            # Make sure all text is ASCII-safe before sending
            try:
                # Ensure the prompt is ASCII-safe
                safe_prompt = final_prompt.encode('ascii', 'replace').decode('ascii')
                data["prompt"] = safe_prompt
            except:
                # If that fails, use original
                pass
            
            # API request with error handling
            response = requests.post(url, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'No response received').strip()
                
                # Add to conversation history
                self.conversation_history.append({"role": "User", "content": message})
                self.conversation_history.append({"role": "Assistant", "content": ai_response})
                
                # Keep only last 12 messages (6 exchanges)
                if len(self.conversation_history) > 12:
                    self.conversation_history = self.conversation_history[-12:]
                
                wx.CallAfter(self.add_message, "🤖 KIC-AI", ai_response)
            else:
                wx.CallAfter(self.add_message, "❌ Error", f"AI server error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            wx.CallAfter(self.add_message, "❌ Error", 
                        "Cannot connect to Ollama.\n"
                        "Start Ollama server:\n"
                        "  ollama serve\n"
                        "  ollama run llama3.2:3b")
        except requests.exceptions.Timeout:
            wx.CallAfter(self.add_message, "❌ Error", "AI timeout - please try again")
        except Exception as e:
            wx.CallAfter(self.add_message, "❌ Error", f"AI error: {str(e)}")
        finally:
            wx.CallAfter(self.send_btn.Enable, True)
            wx.CallAfter(self.set_status, "Ready")
    
    def get_mode_instructions(self):
        """Get instructions based on current interaction mode"""
        if self.interaction_mode == self.ANALYSIS_MODE:
            return ("ANALYSIS MODE: Provide only analysis and recommendations. "
                   "Do not suggest any direct modifications to the design. "
                   "Focus on observations and general advice.")
        
        elif self.interaction_mode == self.ADVISORY_MODE:
            return ("ADVISORY MODE: Provide step-by-step instructions when suggesting changes. "
                   "Always ask for user confirmation before proceeding with multi-step processes. "
                   "Format suggestions as clear actionable steps with safety warnings when needed. "
                   "Example: 'To remove R14: 1) First select the component 2) Press Delete 3) Update the netlist. Would you like me to guide you through this?'")
        
        elif self.interaction_mode == self.ASSISTANT_MODE:
            return ("ASSISTANT MODE: Provide interactive design assistance. "
                   "You can suggest specific actions and modifications. "
                   "When appropriate, indicate what changes could be made automatically in the future. "
                   "Be proactive in offering to help with implementation.")
        
        return ""
    
    def process_user_message(self, message):
        """Process user message with mode-specific handling"""
        self.send_btn.Enable(False)
        self.set_status("Processing...")
        
        # Check for mode-specific commands
        if self.interaction_mode == self.ADVISORY_MODE:
            if any(word in message.lower() for word in ['remove', 'delete', 'change', 'modify', 'update']):
                # Add advisory warning
                self.add_message("⚠️ Advisory", 
                               "I'll provide step-by-step guidance for this modification. "
                               "Please confirm each step before proceeding.")
        
        elif self.interaction_mode == self.ASSISTANT_MODE:
            if any(word in message.lower() for word in ['remove', 'delete', 'change', 'modify']):
                # Add assistant note
                self.add_message("🤖 Assistant", 
                               "I'll provide interactive guidance. In future versions, "
                               "I may be able to help automate some of these tasks.")
        
        # Check for component-specific guidance in Assistant mode
        specific_guidance = self.get_component_specific_guidance(message)
        if specific_guidance:
            self.add_message("🤖 Assistant", specific_guidance)
            self.send_btn.Enable(True)
            self.set_status("Ready")
            return
        # Start AI processing in thread
        thread = threading.Thread(target=self.send_to_ai, args=(message,))
        thread.daemon = True
        thread.start()
    
    def get_component_specific_guidance(self, message):
        """Provide specific guidance for common component operations"""
        if self.interaction_mode != self.ASSISTANT_MODE:
            return None
            
        message_lower = message.lower()
        
        # Check for specific component removal requests
        if any(phrase in message_lower for phrase in ['remove j', 'delete j', 'remove connector']):
            component = None
            # Extract component reference
            import re
            match = re.search(r'[jJ]\d+', message)
            if match:
                component = match.group(0).upper()
            
            if component:
                return f"""🔧 **Removing {component} - Step-by-step:**

1. **Select the component:**
   - Click on {component} in the PCB layout
   - The component should highlight in selection color

2. **Delete the component:**
   - Press **Delete** key, or
   - Right-click → Delete, or  
   - Use Edit → Delete from menu

3. **Clean up connections:**
   - Check for any remaining tracks/vias
   - Delete orphaned connections if needed

4. **Update schematic (if needed):**
   - Switch to schematic editor
   - Remove {component} from schematic too
   - Run Tools → Update PCB from Schematic

5. **Verify design:**
   - Check Design Rules (DRC)
   - Verify no missing connections

Would you like me to explain any of these steps in more detail?"""
        
        return None
    def get_language_prompt(self):
        """Get language-specific prompt addition"""
        selection = self.lang_choice.GetSelection()
        if selection == -1:
            selection = 0  # Default to English
            
        lang_info = self.LANGUAGES[selection]
        lang_code = lang_info["code"]
        
        if lang_code == "en":
            return ""  # English is default
        elif lang_code == "nl":
            return "U MOET antwoorden in het Nederlands! Alle antwoorden in het Nederlands. Nederlandse termen voor elektronica gebruiken. Niet in het Engels antwoorden."
        elif lang_code == "de":
            return "Antworten Sie auf Deutsch! Alle Antworten auf Deutsch schreiben. Deutsche Begriffe fuer Elektronik verwenden. Nicht auf Englisch antworten."
        elif lang_code == "es":
            return "Responder en espanol! Todas las respuestas en espanol. Usar terminos tecnicos en espanol. No responder en ingles."
        elif lang_code == "fr":
            return "Repondre en francais! Toutes les reponses en francais. Utiliser des termes techniques francais. Ne pas repondre en anglais."
        elif lang_code == "pt":
            return "Responder em portugues! Todas as respostas em portugues. Usar termos tecnicos em portugues. Nao responder em ingles."
        else:
            return ""
    
    def get_mcp_enhanced_context(self, message: str, design_context: str) -> str:
        """Get enhanced context using MCP tools"""
        if not self.mcp_enabled or not self.mcp_tools:
            return ""
        
        enhanced_context = "\n\n=== ENHANCED CONTEXT (via MCP) ==="
        
        try:
            # Debug: Check if MCP is working
            available_tools = self.mcp_client.get_available_tools()
            if available_tools:
                enhanced_context += f"\nMCP Status: ✅ Active ({len(available_tools)} tools available)"
                enhanced_context += f"\nAvailable tools: {', '.join(available_tools)}"
            else:
                enhanced_context += "\nMCP Status: ❌ No tools available"
                return enhanced_context
            
            # Always try to provide component pricing context for any component-related query
            if any(word in message.lower() for word in ['price', 'pricing', 'cost', 'resistor', 'component', 'expensive', 'cheap']):
                
                # Extract component references from design context
                import re
                component_refs = re.findall(r'([RCLUDQJ]\d+):', design_context)
                
                if component_refs:
                    # Get pricing for first few components
                    sample_refs = component_refs[:8]  # Increase sample size
                    enhanced_context += f"\nAnalyzing pricing for components: {sample_refs}"
                    
                    # Try component database pricing
                    try:
                        pricing_data = self.mcp_tools.get_component_pricing(sample_refs)
                        
                        if pricing_data:
                            enhanced_context += "\n\nCOMPONENT PRICING (Component Database):"
                            for ref, price_info in pricing_data.items():
                                price = price_info.get('unit_price', 'N/A')
                                stock = price_info.get('stock', 'Unknown')
                                enhanced_context += f"\n{ref}: ${price} (Stock: {stock} units)"
                        else:
                            enhanced_context += "\nNo pricing data available from component database"
                    except Exception as e:
                        enhanced_context += f"\nPricing lookup error: {e}"
                    
                    # Try Digi-Key search for common components
                    if any(word in message.lower() for word in ['resistor', 'price']):
                        try:
                            digikey_result = self.mcp_client.call_tool("search_parts", {
                                "keywords": "resistor 0805 1% smd"
                            })
                            
                            if digikey_result and 'result' in digikey_result:
                                parts = digikey_result['result'].get('parts', [])
                                if parts:
                                    enhanced_context += "\n\nDIGI-KEY RESISTOR PRICING:"
                                    for part in parts[:3]:  # Show top 3 results
                                        enhanced_context += f"\n• {part['part_number']}: ${part['unit_price']} - {part['description']}"
                                        enhanced_context += f"  Stock: {part['quantity_available']} units"
                        except Exception as e:
                            enhanced_context += f"\nDigi-Key search error: {e}"
                
                else:
                    enhanced_context += "\nNo component references found in current design"
                    # Still try to provide general pricing info
                    try:
                        # Get general resistor pricing
                        digikey_result = self.mcp_client.call_tool("search_parts", {
                            "keywords": "resistor 0805"
                        })
                        
                        if digikey_result and 'result' in digikey_result:
                            parts = digikey_result['result'].get('parts', [])
                            if parts:
                                enhanced_context += "\n\nGENERAL RESISTOR PRICING (Digi-Key):"
                                for part in parts[:2]:  # Show top 2 results
                                    enhanced_context += f"\n• {part['description']}: ${part['unit_price']}"
                    except Exception as e:
                        enhanced_context += f"\nGeneral pricing lookup error: {e}"
            
            # Component search and alternatives
            if any(word in message.lower() for word in ['suggest', 'alternative', 'replace', 'better', 'cheaper']):
                enhanced_context += "\n\nALTERNATIVE SUGGESTIONS:"
                enhanced_context += "\nMCP tools can provide component alternatives and cost optimization suggestions."
                
                # Try to get alternatives for first resistor if available
                import re
                resistors = re.findall(r'(R\d+):', design_context)
                if resistors:
                    try:
                        alt_result = self.mcp_client.call_tool("get_alternatives", {
                            "part_number": resistors[0]
                        })
                        if alt_result and 'result' in alt_result:
                            alternatives = alt_result['result'].get('alternatives', [])
                            if alternatives:
                                enhanced_context += f"\nAlternatives for {resistors[0]}:"
                                for alt in alternatives[:2]:
                                    enhanced_context += f"\n• {alt['part_number']}: ${alt['unit_price']} ({alt['manufacturer']})"
                    except Exception as e:
                        enhanced_context += f"\nAlternative lookup error: {e}"
                
        except Exception as e:
            enhanced_context += f"\n\nMCP Error: {str(e)}"
        
        return enhanced_context
    
    def on_close(self, event):
        """Sluit dialog en clean up MCP connections"""
        if self.mcp_client:
            self.mcp_client.disconnect_all()
        self.Destroy()

