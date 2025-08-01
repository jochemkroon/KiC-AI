#!/usr/bin/env python3
"""
Configuration Manager for KIC-AI
Handles saving and loading of API keys and settings
"""

import os
import json
import wx

class ConfigManager:
    """Manages configuration settings for KIC-AI"""
    
    def __init__(self):
        # Configuration file path
        self.config_dir = os.path.expanduser("~/.kic-ai")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Default configuration
        self.default_config = {
            "nexar_api_key": "",
            "ai_mode": "analysis",
            "language": "English",
            "context_type": "pcb",
            "use_demo_mode": True,
            "pricing_providers": ["nexar"],
            "last_updated": ""
        }
        
        # Load existing config
        self.config = self.load_config()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Return default config if loading fails
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            self.ensure_config_dir()
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
    
    def get_nexar_api_key(self):
        """Get Nexar API key (from config or environment)"""
        # Check config first
        api_key = self.config.get("nexar_api_key", "")
        if api_key:
            return api_key
        
        # Fallback to environment variable
        return os.getenv("NEXAR_TOKEN", "")
    
    def set_nexar_api_key(self, api_key):
        """Set Nexar API key"""
        self.config["nexar_api_key"] = api_key
        # Update demo mode based on whether we have an API key
        self.config["use_demo_mode"] = not bool(api_key.strip())
    
    def is_demo_mode(self):
        """Check if we're in demo mode"""
        return self.config.get("use_demo_mode", True) or not self.get_nexar_api_key()


class ConfigDialog(wx.Dialog):
    """Configuration dialog for KIC-AI settings"""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, title="KIC-AI Configuration", 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                         size=(500, 400))
        
        self.config_manager = config_manager
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the user interface"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="🔧 KIC-AI Configuration")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Notebook for different sections
        notebook = wx.Notebook(panel)
        
        # API Settings Tab
        api_panel = wx.Panel(notebook)
        self.create_api_panel(api_panel)
        notebook.AddPage(api_panel, "API Settings")
        
        # General Settings Tab
        general_panel = wx.Panel(notebook)
        self.create_general_panel(general_panel)
        notebook.AddPage(general_panel, "General")
        
        # Info Tab
        info_panel = wx.Panel(notebook)
        self.create_info_panel(info_panel)
        notebook.AddPage(info_panel, "Info")
        
        main_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.test_btn = wx.Button(panel, label="🧪 Test Connection")
        self.save_btn = wx.Button(panel, wx.ID_OK, label="💾 Save")
        self.cancel_btn = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
        
        btn_sizer.Add(self.test_btn, 0, wx.RIGHT, 10)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.cancel_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.save_btn, 0)
        
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Bind events
        self.test_btn.Bind(wx.EVT_BUTTON, self.on_test_connection)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        
        panel.SetSizer(main_sizer)
    
    def create_api_panel(self, panel):
        """Create API settings panel"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Nexar API section
        nexar_box = wx.StaticBox(panel, label="Nexar API Settings")
        nexar_sizer = wx.StaticBoxSizer(nexar_box, wx.VERTICAL)
        
        # API Key input
        key_label = wx.StaticText(panel, label="API Key:")
        self.api_key_ctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(300, -1))
        self.api_key_ctrl.SetHint("Enter your Nexar API key (optional)")
        
        # Demo mode checkbox
        self.demo_mode_cb = wx.CheckBox(panel, label="Use demo mode (no API key required)")
        
        # Status text
        self.status_text = wx.StaticText(panel, label="")
        
        # Help text
        help_text = wx.StaticText(panel, label=
            "• Leave empty to use demo mode with sample data\n"
            "• Get your free API key at: https://nexar.com/api\n"
            "• Demo mode provides realistic pricing for testing")
        help_text.SetForegroundColour(wx.Colour(100, 100, 100))
        
        nexar_sizer.Add(key_label, 0, wx.ALL, 5)
        nexar_sizer.Add(self.api_key_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        nexar_sizer.Add(self.demo_mode_cb, 0, wx.ALL, 5)
        nexar_sizer.Add(self.status_text, 0, wx.ALL, 5)
        nexar_sizer.Add(help_text, 0, wx.ALL, 5)
        
        sizer.Add(nexar_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
    
    def create_general_panel(self, panel):
        """Create general settings panel"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Mode selection
        mode_box = wx.StaticBox(panel, label="AI Mode")
        mode_sizer = wx.StaticBoxSizer(mode_box, wx.VERTICAL)
        
        self.mode_choice = wx.Choice(panel, choices=["analysis", "chat", "expert"])
        mode_sizer.Add(self.mode_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(mode_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Language selection
        lang_box = wx.StaticBox(panel, label="Language")
        lang_sizer = wx.StaticBoxSizer(lang_box, wx.VERTICAL)
        
        self.lang_choice = wx.Choice(panel, choices=["English", "Nederlands", "Deutsch", "Français"])
        lang_sizer.Add(self.lang_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(lang_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
    
    def create_info_panel(self, panel):
        """Create info panel"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        info_text = wx.StaticText(panel, label=
            "🔧 KIC-AI Assistant\n\n"
            "An AI-powered assistant for KiCad PCB design.\n\n"
            "Features:\n"
            "• Component analysis and recommendations\n"
            "• Real-time pricing from multiple distributors\n"
            "• Design rule checking and suggestions\n"
            "• Multi-language support\n\n"
            "Configuration:\n"
            "• Settings are saved to ~/.kic-ai/config.json\n"
            "• Environment variables are supported\n"
            "• Demo mode works without API keys\n\n"
            "Need help? Check the documentation or report issues on GitHub.")
        
        sizer.Add(info_text, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        # API key
        api_key = self.config_manager.get_nexar_api_key()
        self.api_key_ctrl.SetValue(api_key)
        
        # Demo mode
        demo_mode = self.config_manager.is_demo_mode()
        self.demo_mode_cb.SetValue(demo_mode)
        
        # AI mode
        ai_mode = self.config_manager.get("ai_mode", "analysis")
        mode_choices = ["analysis", "chat", "expert"]
        if ai_mode in mode_choices:
            self.mode_choice.SetSelection(mode_choices.index(ai_mode))
        
        # Language
        language = self.config_manager.get("language", "English")
        lang_choices = ["English", "Nederlands", "Deutsch", "Français"]
        if language in lang_choices:
            self.lang_choice.SetSelection(lang_choices.index(language))
        
        # Update status
        self.update_status()
    
    def update_status(self):
        """Update the status text"""
        api_key = self.api_key_ctrl.GetValue().strip()
        if api_key:
            self.status_text.SetLabel("✅ API key configured - Real Nexar API will be used")
            self.status_text.SetForegroundColour(wx.Colour(0, 128, 0))
        else:
            self.status_text.SetLabel("ℹ️ Demo mode - Using sample pricing data")
            self.status_text.SetForegroundColour(wx.Colour(0, 100, 200))
    
    def on_test_connection(self, event):
        """Test the API connection"""
        api_key = self.api_key_ctrl.GetValue().strip()
        
        if not api_key:
            wx.MessageBox("No API key entered. Demo mode will be used.",
                         "Test Result", wx.OK | wx.ICON_INFORMATION)
            return
        
        # Simple test - just check if key format looks valid
        if len(api_key) < 10:
            wx.MessageBox("API key seems too short. Please check your key.",
                         "Test Result", wx.OK | wx.ICON_WARNING)
            return
        
        # For now, just show success (real API testing would require actual Nexar API call)
        wx.MessageBox("API key format looks valid!\n\n"
                     "Note: Actual connection testing requires implementing "
                     "Nexar API authentication.",
                     "Test Result", wx.OK | wx.ICON_INFORMATION)
    
    def on_save(self, event):
        """Save the configuration"""
        try:
            # Save API key
            api_key = self.api_key_ctrl.GetValue().strip()
            self.config_manager.set_nexar_api_key(api_key)
            
            # Save AI mode
            mode_selection = self.mode_choice.GetSelection()
            if mode_selection != wx.NOT_FOUND:
                ai_mode = ["analysis", "chat", "expert"][mode_selection]
                self.config_manager.set("ai_mode", ai_mode)
            
            # Save language
            lang_selection = self.lang_choice.GetSelection()
            if lang_selection != wx.NOT_FOUND:
                language = ["English", "Nederlands", "Deutsch", "Français"][lang_selection]
                self.config_manager.set("language", language)
            
            # Save to file
            if self.config_manager.save_config():
                wx.MessageBox("Configuration saved successfully!",
                             "Success", wx.OK | wx.ICON_INFORMATION)
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox("Error saving configuration!",
                             "Error", wx.OK | wx.ICON_ERROR)
        
        except Exception as e:
            wx.MessageBox(f"Error saving configuration: {str(e)}",
                         "Error", wx.OK | wx.ICON_ERROR)
