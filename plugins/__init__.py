import pcbnew
import wx
import os
import sys

# Try to import eeschema for schematic support
try:
    import eeschema
    EESCHEMA_AVAILABLE = True
except ImportError:
    EESCHEMA_AVAILABLE = False

# Add plugin directory to sys.path for imports
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

class KicAIAssistant(pcbnew.ActionPlugin):
    """
    KIC-AI Assistant Plugin voor KiCad
    AI-powered PCB design assistant met Ollama integratie
    """
    
    def __init__(self):
        super().__init__()
        self.name = "KIC-AI Assistant" 
        self.category = "AI Tools"
        self.description = "AI assistant for PCB and Schematic design with Ollama"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "robot_icon.png")
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), "robot_icon.png")
        
    def defaults(self):
        pass  # Niet meer nodig met __init__ implementatie
        
    def Run(self):
        """Start the AI Assistant dialog"""
        try:
            # Import de dialog class
            from ai_dialog import AIAssistantDialog
            
            # Determine context - check if we're in PCB or Schematic editor
            context_type = "pcb"  # Default to PCB
            
            # Better context detection
            try:
                # Check if we have a board loaded and it has a valid filename
                board = pcbnew.GetBoard()
                if board and board.GetFileName():
                    # We have a PCB board loaded
                    footprints = list(board.GetFootprints())
                    
                    if len(footprints) == 0:
                        # No components on PCB - ask user what they want to analyze
                        dlg = wx.MessageDialog(
                            None,
                            "No components found on PCB.\n\nWhat would you like to analyze?\n\n"
                            "• Schematic/Circuit: Review component values, connections, and circuit design\n"
                            "• PCB Layout: Analyze board layout, placement, and routing\n\n"
                            "Note: Both modes use data from the loaded KiCad project.",
                            "KIC-AI Context Selection",
                            wx.YES_NO | wx.ICON_QUESTION
                        )
                        dlg.SetYesNoLabels("&Schematic/Circuit", "&PCB Layout")
                        result = dlg.ShowModal()
                        dlg.Destroy()
                        
                        context_type = "schematic" if result == wx.ID_YES else "pcb"
                    else:
                        # PCB has components - ask what to focus on
                        dlg = wx.MessageDialog(
                            None,
                            "What would you like to analyze?\n\n"
                            "• Schematic/Circuit: Review component values, connections, and circuit design\n"
                            "• PCB Layout: Analyze component placement, routing, and board layout\n\n"
                            "Note: Both modes use data from the current KiCad project.",
                            "KIC-AI Analysis Mode",
                            wx.YES_NO | wx.ICON_QUESTION
                        )
                        dlg.SetYesNoLabels("&Schematic/Circuit", "&PCB Layout")
                        result = dlg.ShowModal()
                        dlg.Destroy()
                        
                        context_type = "schematic" if result == wx.ID_YES else "pcb"
                else:
                    # No board loaded - inform user
                    wx.MessageBox(
                        "No KiCad project loaded.\n\n"
                        "Please open a KiCad project first:\n"
                        "1. Open your .kicad_pcb file in PCB Editor\n"
                        "2. Click the KIC-AI robot icon in the toolbar\n\n"
                        "The plugin will analyze both schematic and PCB data from the project.",
                        "KIC-AI: No Project Loaded",
                        wx.OK | wx.ICON_INFORMATION
                    )
                    return
                    
            except Exception as e:
                # Fallback to PCB mode
                context_type = "pcb"
            
            # Create and show dialog with detected context
            dialog = AIAssistantDialog(None, context_type=context_type)
            dialog.Show()
            
        except ImportError as e:
            wx.MessageBox(
                f"Cannot load AI dialog:\n{str(e)}\n\nPlease check plugin installation.",
                "KIC-AI Error",
                wx.OK | wx.ICON_ERROR
            )
        except Exception as e:
            wx.MessageBox(
                f"KIC-AI error:\n{str(e)}",
                "KIC-AI Error", 
                wx.OK | wx.ICON_ERROR
            )

# Registreer de plugin
KicAIAssistant().register()
