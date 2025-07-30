import wx
import pcbnew
import threading
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
        
        # Icon instellen (optioneel)
        self.SetIcon(wx.Icon())
        
        # Chat history voor context
        self.conversation_history = []
        
        # UI opzetten
        self.init_ui()
        
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
        
        # Input layout
        input_sizer.Add(self.input_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_btn, 0, wx.RIGHT, 5)
        input_sizer.Add(self.analyze_btn, 0, wx.RIGHT, 5) 
        input_sizer.Add(self.clear_btn, 0, wx.RIGHT, 5)
        input_sizer.Add(self.context_btn, 0)
        
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
        
    def bind_events(self):
        """Bind UI events"""
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        self.analyze_btn.Bind(wx.EVT_BUTTON, self.on_analyze)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        self.context_btn.Bind(wx.EVT_BUTTON, self.on_show_context)
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
        
    def on_close(self, event):
        """Sluit dialog"""
        self.Destroy()
        
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
            
            if is_analysis:
                if self.context_type == "schematic":
                    system_prompt = ("You are an expert electronic circuit designer and schematic review specialist. "
                                   "Analyze the provided schematic data thoroughly and provide specific, practical advice. "
                                   "Look at component types, values, connections, and circuit topology. "
                                   "Focus on circuit functionality, component selection, and design best practices. "
                                   f"{mode_instructions} "
                                   "Reference previous conversation if relevant.")
                else:
                    system_prompt = ("You are an expert PCB design engineer. Analyze the provided PCB data thoroughly and provide specific, practical advice. "
                                   "Look at individual components, their values, positions, and relationships. "
                                   f"{mode_instructions} "
                                   "Reference previous conversation if relevant.")
            else:
                if self.context_type == "schematic":
                    system_prompt = ("You are a helpful schematic design assistant with access to the current schematic design. "
                                   "When users ask about specific components, circuits, or connections, reference the actual schematic data provided. "
                                   "Give specific answers about component values, connections, and circuit topology when possible. "
                                   "Focus on circuit functionality, component selection, and electrical design principles. "
                                   f"{mode_instructions} "
                                   "Remember our conversation and build upon previous topics when relevant.")
                else:
                    system_prompt = ("You are a helpful PCB design assistant with access to the current PCB design. "
                                   "When users ask about specific components (like resistors, capacitors, ICs), look up the actual component details from the PCB context provided. "
                                   "Give specific answers referencing actual component values, positions, and designators when possible. "
                                   "If asked about a specific component (e.g., 'R1', 'check this resistor'), find that component in the PCB data and provide detailed information about it. "
                                   f"{mode_instructions} "
                                   "Remember our conversation and build upon previous topics when relevant.")
            
            # Build final prompt with design context
            final_prompt = system_prompt + conversation_context + design_context + f"\nUser question: {message}\n\nPlease provide a specific, helpful response based on the actual design data when applicable:"
            
            # API request
            data = {
                "model": "llama3.2:3b",
                "prompt": final_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "num_ctx": 4096,  # Verhoogd voor meer context
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(url, json=data, timeout=60)  # Langere timeout
            
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
        
        # Start AI processing in thread
        thread = threading.Thread(target=self.send_to_ai, args=(message,))
        thread.daemon = True
        thread.start()
