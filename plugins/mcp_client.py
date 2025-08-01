# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) Client for KIC-AI Plugin
Enables communication with MCP servers for extended functionality
"""

import json
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional

class MCPClient:
    """MCP Client for communicating with MCP servers"""
    
    def __init__(self):
        self.servers = {}
        self.available_tools = {}
        
    def connect_server(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Connect to an MCP server"""
        try:
            # Start MCP server process
            process = subprocess.Popen(
                server_config['command'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            self.servers[server_name] = {
                'process': process,
                'config': server_config
            }
            
            # Initialize server
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "KIC-AI",
                        "version": "1.4.5"
                    }
                }
            }
            
            self._send_message(server_name, init_message)
            response = self._receive_message(server_name)
            
            if response and 'result' in response:
                # Get available tools
                self._load_server_tools(server_name)
                return True
                
        except Exception as e:
            print(f"Failed to connect to MCP server {server_name}: {e}")
            
        return False
    
    def _send_message(self, server_name: str, message: Dict[str, Any]):
        """Send JSON-RPC message to MCP server"""
        if server_name in self.servers:
            process = self.servers[server_name]['process']
            json_message = json.dumps(message) + '\n'
            process.stdin.write(json_message)
            process.stdin.flush()
    
    def _receive_message(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC message from MCP server"""
        if server_name in self.servers:
            process = self.servers[server_name]['process']
            try:
                line = process.stdout.readline()
                if line:
                    try:
                        response = json.loads(line.strip())
                        return response
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error from {server_name}: {e}")
                        print(f"Raw response: {line}")
                        return None
                else:
                    print(f"Empty response from {server_name}")
                    return None
            except Exception as e:
                print(f"Error reading from {server_name}: {e}")
                return None
        return None
    
    def _load_server_tools(self, server_name: str):
        """Load available tools from MCP server"""
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        self._send_message(server_name, tools_message)
        response = self._receive_message(server_name)
        
        if response and 'result' in response:
            tools = response['result'].get('tools', [])
            for tool in tools:
                tool_name = tool['name']
                self.available_tools[tool_name] = {
                    'server': server_name,
                    'schema': tool
                }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool via MCP"""
        if tool_name not in self.available_tools:
            return {"error": f"Tool {tool_name} not available"}
        
        server_name = self.available_tools[tool_name]['server']
        
        tool_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            self._send_message(server_name, tool_message)
            response = self._receive_message(server_name)
            
            if response:
                return response
            else:
                return {"error": f"No response from server {server_name}"}
                
        except Exception as e:
            return {"error": f"Tool call failed: {str(e)}"}
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.available_tools.keys())
    
    def disconnect_all(self):
        """Disconnect all MCP servers"""
        for server_name, server_info in self.servers.items():
            try:
                server_info['process'].terminate()
            except:
                pass
        self.servers.clear()
        self.available_tools.clear()


class KiCadMCPTools:
    """KiCad-specific MCP tool implementations"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        
    def search_components(self, component_type: str, specifications: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for components using MCP component database"""
        try:
            result = self.mcp_client.call_tool("search_components", {
                "type": component_type,
                "specs": specifications
            })
            
            if result and 'result' in result:
                return result['result'].get('components', [])
                
        except Exception as e:
            print(f"Component search error: {e}")
            
        return []
    
    def get_component_pricing(self, part_numbers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get component pricing via MCP"""
        try:
            result = self.mcp_client.call_tool("get_pricing", {
                "part_numbers": part_numbers
            })
            
            if result and 'result' in result:
                return result['result'].get('pricing', {})
                
        except Exception as e:
            print(f"Pricing lookup error: {e}")
            
        return {}
    
    def check_component_availability(self, part_numbers: List[str]) -> Dict[str, int]:
        """Check component availability via MCP"""
        try:
            result = self.mcp_client.call_tool("check_availability", {
                "part_numbers": part_numbers
            })
            
            if result and 'result' in result:
                return result['result'].get('availability', {})
                
        except Exception as e:
            print(f"Availability check error: {e}")
            
        return {}
    
    def suggest_alternatives(self, component_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get component alternatives via MCP"""
        try:
            result = self.mcp_client.call_tool("suggest_alternatives", component_specs)
            
            if result and 'result' in result:
                return result['result'].get('alternatives', [])
                
        except Exception as e:
            print(f"Alternative search error: {e}")
            
        return []
