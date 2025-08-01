# -*- coding: utf-8 -*-
"""
Configuration Dialog for KIC-AI Assistant
Allows users to configure MCP servers, API keys, and other settings
"""

import wx
import json
import os
from typing import Dict, List, Any

class MCPServerConfigPanel(wx.Panel):
    """Panel for configuring a single MCP server"""
    
    def __init__(self, parent, server_name: str, server_config: Dict[str, Any]):
        super().__init__(parent)
        self.server_name = server_name
        self.server_config = server_config.copy()
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Initialize the UI for this server config"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Server header
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Enable checkbox
        self.enabled_cb = wx.CheckBox(self, label=f"Enable {self.server_name}")
        self.enabled_cb.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Delete button
        self.delete_btn = wx.Button(self, label="🗑️", size=(30, -1))
        self.delete_btn.SetToolTip("Delete this server configuration")
        
        header_sizer.Add(self.enabled_cb, 1, wx.EXPAND | wx.RIGHT, 5)
        header_sizer.Add(self.delete_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # Description
        self.description_text = wx.StaticText(self, label="")
        self.description_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        
        # Configuration grid
        config_sizer = wx.FlexGridSizer(0, 2, 5, 10)
        config_sizer.AddGrowableCol(1, 1)
        
        # Command
        config_sizer.Add(wx.StaticText(self, label="Command:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.command_text = wx.TextCtrl(self, style=wx.TE_READONLY)
        config_sizer.Add(self.command_text, 1, wx.EXPAND)
        
        # API Key (if required)
        self.api_key_label = wx.StaticText(self, label="API Key:")
        self.api_key_text = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.api_key_text.SetHint("Enter your API key here...")
        config_sizer.Add(self.api_key_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_sizer.Add(self.api_key_text, 1, wx.EXPAND)
        
        # Client ID (for some APIs)
        self.client_id_label = wx.StaticText(self, label="Client ID:")
        self.client_id_text = wx.TextCtrl(self)
        self.client_id_text.SetHint("Enter client ID if required...")
        config_sizer.Add(self.client_id_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_sizer.Add(self.client_id_text, 1, wx.EXPAND)
        
        # API URL (for custom endpoints)
        self.api_url_label = wx.StaticText(self, label="API URL:")
        self.api_url_text = wx.TextCtrl(self)
        self.api_url_text.SetHint("Custom API endpoint URL...")
        config_sizer.Add(self.api_url_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_sizer.Add(self.api_url_text, 1, wx.EXPAND)
        
        # Client Secret (for V4 APIs like Digi-Key)
        self.client_secret_label = wx.StaticText(self, label="Client Secret:")
        self.client_secret_text = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.client_secret_text.SetHint("Enter client secret if required...")
        config_sizer.Add(self.client_secret_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_sizer.Add(self.client_secret_text, 1, wx.EXPAND)
        
        # Sandbox mode checkbox
        self.sandbox_label = wx.StaticText(self, label="Sandbox Mode:")
        self.sandbox_checkbox = wx.CheckBox(self, label="Use sandbox/testing endpoint")
        config_sizer.Add(self.sandbox_label, 0, wx.ALIGN_CENTER_VERTICAL)
        config_sizer.Add(self.sandbox_checkbox, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # Test button
        test_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.test_btn = wx.Button(self, label="🧪 Test Connection")
        self.test_status = wx.StaticText(self, label="")
        test_sizer.Add(self.test_btn, 0, wx.RIGHT, 10)
        test_sizer.Add(self.test_status, 1, wx.ALIGN_CENTER_VERTICAL)
        
        # Layout
        main_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.description_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(config_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(test_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Events
        self.enabled_cb.Bind(wx.EVT_CHECKBOX, self.on_enabled_change)
        self.test_btn.Bind(wx.EVT_BUTTON, self.on_test_connection)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        
        # Update visibility based on server type
        self.update_field_visibility()
        
    def load_config(self):
        """Load configuration values"""
        self.enabled_cb.SetValue(self.server_config.get('enabled', False))
        self.description_text.SetLabel(self.server_config.get('description', ''))
        
        # Command
        command = self.server_config.get('command', [])
        if isinstance(command, list):
            self.command_text.SetValue(' '.join(command))
        else:
            self.command_text.SetValue(str(command))
        
        # API credentials (load from environment or config)
        if self.server_name == 'digikey_api':
            api_key = os.getenv('DIGIKEY_API_KEY', '')
            client_id = os.getenv('DIGIKEY_CLIENT_ID', '')
            client_secret = os.getenv('DIGIKEY_CLIENT_SECRET', '')
            use_sandbox = os.getenv('DIGIKEY_USE_SANDBOX', 'true')
            self.api_key_text.SetValue(api_key)
            self.client_id_text.SetValue(client_id)
            if hasattr(self, 'client_secret_text'):
                self.client_secret_text.SetValue(client_secret)
            if hasattr(self, 'sandbox_checkbox'):
                self.sandbox_checkbox.SetValue(use_sandbox.lower() == 'true')
            self.api_url_text.SetValue('https://sandbox-api.digikey.com/products/v4' if use_sandbox.lower() == 'true' else 'https://api.digikey.com/products/v4')
        elif self.server_name == 'mouser_api':
            api_key = os.getenv('MOUSER_API_KEY', '')
            self.api_key_text.SetValue(api_key)
            self.api_url_text.SetValue('https://api.mouser.com/api/v1')
        
        self.update_field_visibility()
        
    def update_field_visibility(self):
        """Update field visibility based on server type"""
        requires_api_key = self.server_config.get('requires_api_key', False)
        
        # Show/hide API fields based on server type
        if self.server_name in ['component_database', 'kicad_tools']:
            # Local servers don't need API keys
            self.api_key_label.Hide()
            self.api_key_text.Hide()
            self.client_id_label.Hide()
            self.client_id_text.Hide()
            self.api_url_label.Hide()
            self.api_url_text.Hide()
        elif self.server_name == 'digikey_api':
            # Digi-Key needs API key and client ID
            self.api_key_label.Show()
            self.api_key_text.Show()
            self.client_id_label.Show()
            self.client_id_text.Show()
            self.api_url_label.Show()
            self.api_url_text.Show()
        else:
            # Other APIs might need just API key
            self.api_key_label.Show()
            self.api_key_text.Show()
            self.client_id_label.Hide()
            self.client_id_text.Hide()
            self.api_url_label.Show()
            self.api_url_text.Show()
        
        self.Layout()
        
    def on_enabled_change(self, event):
        """Handle enable/disable change"""
        enabled = self.enabled_cb.GetValue()
        self.server_config['enabled'] = enabled
        
        # Enable/disable all controls
        for child in self.GetChildren():
            if child != self.enabled_cb and child != self.delete_btn:
                child.Enable(enabled)
                
    def on_test_connection(self, event):
        """Test the server connection"""
        self.test_status.SetLabel("🔄 Testing...")
        wx.CallAfter(self._test_connection_async)
        
    def _test_connection_async(self):
        """Test connection in background"""
        try:
            # Import test function
            import sys
            import subprocess
            import tempfile
            import time
            
            # Create test message
            test_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "config-test", "version": "1.0.0"}
                }
            }
            
            # Get command
            command = self.server_config.get('command', [])
            if isinstance(command, str):
                command = command.split()
            
            # Start server process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            # Send test message
            process.stdin.write(json.dumps(test_message) + '\n')
            process.stdin.flush()
            
            # Wait for response (with timeout)
            import select
            ready, _, _ = select.select([process.stdout], [], [], 5.0)  # 5 second timeout
            
            if ready:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if 'result' in response:
                        server_name = response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
                        self.test_status.SetLabel(f"✅ Connected: {server_name}")
                        self.test_status.SetForegroundColour(wx.Colour(0, 128, 0))
                    else:
                        self.test_status.SetLabel("❌ Server error")
                        self.test_status.SetForegroundColour(wx.Colour(255, 0, 0))
                else:
                    self.test_status.SetLabel("❌ No response")
                    self.test_status.SetForegroundColour(wx.Colour(255, 0, 0))
            else:
                self.test_status.SetLabel("❌ Timeout")
                self.test_status.SetForegroundColour(wx.Colour(255, 0, 0))
                
            process.terminate()
            
        except Exception as e:
            self.test_status.SetLabel(f"❌ Error: {str(e)}")
            self.test_status.SetForegroundColour(wx.Colour(255, 0, 0))
            
    def on_delete(self, event):
        """Handle delete server"""
        dlg = wx.MessageDialog(
            self,
            f"Are you sure you want to delete the '{self.server_name}' server configuration?",
            "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            # Notify parent to remove this panel
            event = wx.PyCommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
            event.SetEventObject(self)
            event.server_name = self.server_name
            wx.PostEvent(self.GetParent(), event)
            
        dlg.Destroy()
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        config = self.server_config.copy()
        config['enabled'] = self.enabled_cb.GetValue()
        
        # Save API credentials to environment variables
        if self.api_key_text.IsShown() and self.api_key_text.GetValue():
            if self.server_name == 'digikey_api':
                os.environ['DIGIKEY_API_KEY'] = self.api_key_text.GetValue()
                os.environ['DIGIKEY_CLIENT_ID'] = self.client_id_text.GetValue()
                if hasattr(self, 'client_secret_text') and self.client_secret_text.GetValue():
                    os.environ['DIGIKEY_CLIENT_SECRET'] = self.client_secret_text.GetValue()
                if hasattr(self, 'sandbox_checkbox'):
                    os.environ['DIGIKEY_USE_SANDBOX'] = 'true' if self.sandbox_checkbox.GetValue() else 'false'
            elif self.server_name == 'mouser_api':
                os.environ['MOUSER_API_KEY'] = self.api_key_text.GetValue()
        
        return config


class AddServerDialog(wx.Dialog):
    """Dialog for adding a new MCP server"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Add MCP Server", size=(400, 300))
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instructions
        instruction_text = wx.StaticText(panel, label="Add a new MCP server configuration:")
        instruction_text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Server template selection
        template_sizer = wx.StaticBoxSizer(wx.VERTICAL, panel, "Server Template")
        
        self.template_choice = wx.Choice(panel, choices=[
            "Custom Server",
            "Digi-Key API Server", 
            "Mouser API Server",
            "Local Component Database",
            "External Tool Server"
        ])
        self.template_choice.SetSelection(0)
        
        template_desc = wx.StaticText(panel, label="Select a template or create a custom server")
        template_desc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        
        template_sizer.Add(self.template_choice, 0, wx.EXPAND | wx.ALL, 5)
        template_sizer.Add(template_desc, 0, wx.EXPAND | wx.ALL, 5)
        
        # Server details
        details_sizer = wx.StaticBoxSizer(wx.VERTICAL, panel, "Server Details")
        
        form_sizer = wx.FlexGridSizer(0, 2, 5, 10)
        form_sizer.AddGrowableCol(1, 1)
        
        # Server name
        form_sizer.Add(wx.StaticText(panel, label="Server Name:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.name_text = wx.TextCtrl(panel)
        self.name_text.SetHint("e.g., my_custom_server")
        form_sizer.Add(self.name_text, 1, wx.EXPAND)
        
        # Description
        form_sizer.Add(wx.StaticText(panel, label="Description:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.desc_text = wx.TextCtrl(panel)
        self.desc_text.SetHint("Brief description of the server")
        form_sizer.Add(self.desc_text, 1, wx.EXPAND)
        
        # Command
        form_sizer.Add(wx.StaticText(panel, label="Command:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.command_text = wx.TextCtrl(panel)
        self.command_text.SetHint("python3 -m my_server")
        form_sizer.Add(self.command_text, 1, wx.EXPAND)
        
        details_sizer.Add(form_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        add_btn = wx.Button(panel, wx.ID_OK, "Add Server")
        add_btn.SetDefault()
        
        button_sizer.Add(cancel_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(add_btn, 0)
        
        # Layout
        main_sizer.Add(instruction_text, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(template_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(details_sizer, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
        
        # Events
        self.template_choice.Bind(wx.EVT_CHOICE, self.on_template_change)
        add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Load default template
        self.on_template_change(None)
        
    def on_template_change(self, event):
        """Handle template selection change"""
        selection = self.template_choice.GetSelection()
        
        if selection == 1:  # Digi-Key API Server
            self.name_text.SetValue("digikey_api_custom")
            self.desc_text.SetValue("Custom Digi-Key API integration")
            self.command_text.SetValue("python3 -m mcp_servers.digikey")
        elif selection == 2:  # Mouser API Server
            self.name_text.SetValue("mouser_api")
            self.desc_text.SetValue("Mouser Electronics API integration")
            self.command_text.SetValue("python3 -m mcp_servers.mouser")
        elif selection == 3:  # Local Component Database
            self.name_text.SetValue("local_database")
            self.desc_text.SetValue("Local component database")
            self.command_text.SetValue("python3 -m mcp_servers.local_db")
        elif selection == 4:  # External Tool Server
            self.name_text.SetValue("external_tool")
            self.desc_text.SetValue("External tool integration")
            self.command_text.SetValue("python3 -m mcp_servers.external")
        else:  # Custom Server
            self.name_text.SetValue("")
            self.desc_text.SetValue("")
            self.command_text.SetValue("")
    
    def get_server_config(self) -> tuple:
        """Get the server configuration"""
        name = self.name_text.GetValue().strip()
        if not name:
            return None, None
            
        config = {
            "command": self.command_text.GetValue().strip().split(),
            "description": self.desc_text.GetValue().strip(),
            "enabled": False,  # Start disabled
            "requires_api_key": "api" in name.lower()
        }
        
        return name, config
    
    def on_add(self, event):
        """Handle add button click"""
        name, config = self.get_server_config()
        if name and config:
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox("Please provide a server name and command!", "Missing Information", wx.OK | wx.ICON_WARNING)
    
    def on_cancel(self, event):
        """Handle cancel button click"""
        self.EndModal(wx.ID_CANCEL)
    
    def on_close(self, event):
        """Handle window close (X button)"""
        self.EndModal(wx.ID_CANCEL)


class ConfigurationDialog(wx.Dialog):
    """Main configuration dialog for KIC-AI Assistant"""
    
    def __init__(self, parent):
        super().__init__(parent, title="KIC-AI Configuration", size=(700, 600))
        
        self.config_file = os.path.join(os.path.dirname(__file__), 'mcp_config.json')
        self.server_panels = {}
        
        self.init_ui()
        self.load_configuration()
        
    def init_ui(self):
        """Initialize the UI"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header_text = wx.StaticText(panel, label="KIC-AI Assistant Configuration")
        header_text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Notebook for different config sections
        self.notebook = wx.Notebook(panel)
        
        # MCP Servers tab
        self.mcp_panel = wx.ScrolledWindow(self.notebook)
        self.mcp_panel.SetScrollRate(5, 5)
        self.mcp_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add server button
        add_server_btn = wx.Button(self.mcp_panel, label="➕ Add MCP Server")
        add_server_btn.Bind(wx.EVT_BUTTON, self.on_add_server)
        
        self.mcp_sizer.Add(add_server_btn, 0, wx.EXPAND | wx.ALL, 10)
        self.mcp_panel.SetSizer(self.mcp_sizer)
        
        self.notebook.AddPage(self.mcp_panel, "MCP Servers")
        
        # AI Settings tab
        ai_panel = wx.Panel(self.notebook)
        ai_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # AI Enhancement settings
        ai_group = wx.StaticBoxSizer(wx.VERTICAL, ai_panel, "AI Enhancement Settings")
        
        self.enable_suggestions_cb = wx.CheckBox(ai_panel, label="Enable component suggestions")
        self.enable_pricing_cb = wx.CheckBox(ai_panel, label="Enable pricing lookup")
        self.enable_auto_mod_cb = wx.CheckBox(ai_panel, label="Enable automated modifications (Advanced)")
        self.safety_mode_cb = wx.CheckBox(ai_panel, label="Safety mode (Recommended)")
        
        ai_group.Add(self.enable_suggestions_cb, 0, wx.EXPAND | wx.ALL, 5)
        ai_group.Add(self.enable_pricing_cb, 0, wx.EXPAND | wx.ALL, 5)
        ai_group.Add(self.enable_auto_mod_cb, 0, wx.EXPAND | wx.ALL, 5)
        ai_group.Add(self.safety_mode_cb, 0, wx.EXPAND | wx.ALL, 5)
        
        ai_sizer.Add(ai_group, 0, wx.EXPAND | wx.ALL, 10)
        ai_panel.SetSizer(ai_sizer)
        
        self.notebook.AddPage(ai_panel, "AI Settings")
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        save_btn = wx.Button(panel, wx.ID_OK, "Save Configuration")
        save_btn.SetDefault()
        
        button_sizer.Add(cancel_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(save_btn, 0)
        
        # Layout
        main_sizer.Add(header_text, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
        
        # Events
        self.Bind(wx.EVT_BUTTON, self.on_server_delete, id=wx.ID_ANY)
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    def load_configuration(self):
        """Load existing configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                # Default configuration
                config = {
                    "mcp_servers": {
                        "component_database": {
                            "command": ["python3", "-m", "mcp_servers.component_db"],
                            "description": "Component database with pricing and availability",
                            "enabled": True
                        },
                        "digikey_api": {
                            "command": ["python3", "-m", "mcp_servers.digikey"],
                            "description": "Digi-Key API integration for real-time data",
                            "enabled": False,
                            "requires_api_key": True
                        },
                        "kicad_tools": {
                            "command": ["python3", "-m", "mcp_servers.kicad_tools"],
                            "description": "KiCad design manipulation tools",
                            "enabled": True
                        }
                    },
                    "ai_enhancement": {
                        "enable_component_suggestions": True,
                        "enable_pricing_lookup": True,
                        "enable_automated_modifications": False,
                        "safety_mode": True
                    }
                }
                
            # Load MCP servers
            for server_name, server_config in config.get('mcp_servers', {}).items():
                self.add_server_panel(server_name, server_config)
                
            # Load AI settings
            ai_settings = config.get('ai_enhancement', {})
            self.enable_suggestions_cb.SetValue(ai_settings.get('enable_component_suggestions', True))
            self.enable_pricing_cb.SetValue(ai_settings.get('enable_pricing_lookup', True))
            self.enable_auto_mod_cb.SetValue(ai_settings.get('enable_automated_modifications', False))
            self.safety_mode_cb.SetValue(ai_settings.get('safety_mode', True))
            
        except Exception as e:
            wx.MessageBox(f"Error loading configuration: {e}", "Configuration Error", wx.OK | wx.ICON_ERROR)
            
    def add_server_panel(self, server_name: str, server_config: Dict[str, Any]):
        """Add a server configuration panel"""
        panel = MCPServerConfigPanel(self.mcp_panel, server_name, server_config)
        self.server_panels[server_name] = panel
        self.mcp_sizer.Insert(self.mcp_sizer.GetItemCount() - 1, panel, 0, wx.EXPAND | wx.ALL, 5)
        self.mcp_panel.Layout()
        self.mcp_panel.FitInside()
        
    def on_add_server(self, event):
        """Handle add server button"""
        dlg = AddServerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            server_name, server_config = dlg.get_server_config()
            if server_name and server_config:
                if server_name not in self.server_panels:
                    self.add_server_panel(server_name, server_config)
                else:
                    wx.MessageBox("Server name already exists!", "Duplicate Name", wx.OK | wx.ICON_WARNING)
        dlg.Destroy()
        
    def on_server_delete(self, event):
        """Handle server deletion"""
        if hasattr(event, 'server_name'):
            server_name = event.server_name
            if server_name in self.server_panels:
                panel = self.server_panels[server_name]
                self.mcp_sizer.Detach(panel)
                panel.Destroy()
                del self.server_panels[server_name]
                self.mcp_panel.Layout()
                self.mcp_panel.FitInside()
                
    def save_configuration(self):
        """Save the current configuration"""
        try:
            config = {
                "mcp_servers": {},
                "ai_enhancement": {
                    "enable_component_suggestions": self.enable_suggestions_cb.GetValue(),
                    "enable_pricing_lookup": self.enable_pricing_cb.GetValue(),
                    "enable_automated_modifications": self.enable_auto_mod_cb.GetValue(),
                    "safety_mode": self.safety_mode_cb.GetValue()
                }
            }
            
            # Get server configurations
            for server_name, panel in self.server_panels.items():
                config["mcp_servers"][server_name] = panel.get_config()
                
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            return True
            
        except Exception as e:
            wx.MessageBox(f"Error saving configuration: {e}", "Save Error", wx.OK | wx.ICON_ERROR)
            return False
    
    def on_save(self, event):
        """Handle save button click"""
        if self.save_configuration():
            self.EndModal(wx.ID_OK)
        # If save fails, dialog stays open
    
    def on_cancel(self, event):
        """Handle cancel button click"""
        self.EndModal(wx.ID_CANCEL)
    
    def on_close(self, event):
        """Handle window close (X button)"""
        self.EndModal(wx.ID_CANCEL)


def show_configuration_dialog(parent=None):
    """Show the configuration dialog"""
    dlg = ConfigurationDialog(parent)
    result = dlg.ShowModal()
    
    if result == wx.ID_OK:
        success = dlg.save_configuration()
        if success:
            wx.MessageBox("Configuration saved successfully!\nRestart the plugin to apply changes.", 
                         "Configuration Saved", wx.OK | wx.ICON_INFORMATION)
    
    dlg.Destroy()
    return result == wx.ID_OK


if __name__ == "__main__":
    app = wx.App()
    show_configuration_dialog()
    app.MainLoop()
