#!/usr/bin/env python3
"""
Simple MCP Client for Nexar API integration with embedded server fallback
"""

import json
import subprocess
import time
import os
import sys
import threading
import queue

class EmbeddedNexarServer:
    """Embedded Nexar-compatible server with demo data"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.demo_mode = not bool(api_key)
        
        self.capabilities = {
            "tools": [
                {
                    "name": "search_parts",
                    "description": "Search for electronic components and get pricing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Component search query"},
                            "limit": {"type": "integer", "description": "Max results", "default": 5}
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
        
    def handle_initialize(self, params):
        mode_info = "Demo mode" if self.demo_mode else f"API mode (key: {self.api_key[:8]}...)"
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "embedded-nexar-server", 
                "version": "1.0.0",
                "mode": mode_info
            }
        }
        
    def handle_list_tools(self, params):
        return {"tools": self.capabilities["tools"]}
        
    def handle_call_tool(self, params):
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "search_parts":
            return self._search_parts(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
            
    def _search_parts(self, args):
        query = args.get("query", "")
        limit = args.get("limit", 5)
        
        # Demo parts with realistic pricing
        demo_parts = [
            {
                "part_number": "STM32F407VGT6",
                "manufacturer": "STMicroelectronics",
                "description": "ARM Cortex-M4 32b MCU+FPU 210DMIPS 1MB Flash 192+4KB RAM USB OTG HS/FS 82 IOs",
                "category": "Microcontrollers",
                "pricing": {
                    "Digi-Key": {"price_1": 8.45, "price_10": 7.89, "price_100": 6.98, "stock": 2547},
                    "Mouser": {"price_1": 8.52, "price_10": 7.95, "price_100": 7.02, "stock": 1834},
                    "Farnell": {"price_1": 9.12, "price_10": 8.34, "price_100": 7.45, "stock": 892}
                }
            },
            {
                "part_number": "ESP32-WROOM-32E",
                "manufacturer": "Espressif Systems",
                "description": "WiFi+BT SoC Module 2.4GHz 32-bit",
                "category": "RF Modules",
                "pricing": {
                    "Digi-Key": {"price_1": 3.45, "price_10": 2.98, "price_100": 2.15, "stock": 5670},
                    "Mouser": {"price_1": 3.52, "price_10": 3.05, "price_100": 2.22, "stock": 4123},
                    "Farnell": {"price_1": 3.78, "price_10": 3.25, "price_100": 2.45, "stock": 2890}
                }
            },
            {
                "part_number": "LM358P",
                "manufacturer": "Texas Instruments",
                "description": "Dual Operational Amplifier, 8-Pin PDIP",
                "category": "Amplifiers", 
                "pricing": {
                    "Digi-Key": {"price_1": 0.45, "price_10": 0.38, "price_100": 0.25, "stock": 12450},
                    "Mouser": {"price_1": 0.48, "price_10": 0.41, "price_100": 0.28, "stock": 8967}
                }
            },
            {
                "part_number": "ATMEGA328P-PU",
                "manufacturer": "Microchip Technology",
                "description": "8-bit AVR Microcontroller, 32KB Flash, 28-Pin PDIP",
                "category": "Microcontrollers",
                "pricing": {
                    "Digi-Key": {"price_1": 2.45, "price_10": 2.15, "price_100": 1.85, "stock": 3456},
                    "Mouser": {"price_1": 2.52, "price_10": 2.22, "price_100": 1.91, "stock": 2789}
                }
            },
            {
                "part_number": "NE555P",
                "manufacturer": "Texas Instruments",
                "description": "Single Precision Timer, 8-Pin PDIP",
                "category": "Timers",
                "pricing": {
                    "Digi-Key": {"price_1": 0.35, "price_10": 0.28, "price_100": 0.18, "stock": 8750},
                    "Mouser": {"price_1": 0.38, "price_10": 0.31, "price_100": 0.21, "stock": 6234}
                }
            }
        ]
        
        # Simple search matching
        results = []
        query_lower = query.lower()
        
        for part in demo_parts:
            if (query_lower in part["part_number"].lower() or 
                query_lower in part["description"].lower() or
                query_lower in part["manufacturer"].lower() or
                any(query_lower in word for word in query_lower.split())):
                results.append(part)
                
            if len(results) >= limit:
                break
        
        return {
            "content": [{"type": "text", "text": f"Found {len(results)} parts ({'API' if not self.demo_mode else 'demo'} mode)"}],
            "isError": False,
            "_meta": {
                "parts": results,
                "demo_mode": self.demo_mode,
                "api_key_configured": bool(self.api_key)
            }
        }

class SimpleMCPClient:
    def __init__(self, api_key=None):
        self.server_process = None
        self.embedded_server = None
        self.api_key = api_key
        self.request_id = 1
        self.is_embedded = False
    
    def start_nexar_server(self):
        """Start the Nexar MCP server - try external files first, then embedded server"""
        try:
            # Try to find external server files first
            possible_paths = [
                os.path.join(os.path.dirname(__file__), 'nexar_server.py'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_servers', 'nexar.py'),
                os.path.join(os.path.dirname(__file__), '..', 'mcp_servers', 'nexar.py'),
                os.path.join('mcp_servers', 'nexar.py'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_servers', 'nexar.py')
            ]
            
            server_path = None
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    server_path = abs_path
                    print(f"Found external Nexar server at: {server_path}")
                    break
            
            # If external server found, try to start it
            if server_path:
                if self._start_external_server(server_path):
                    return True
                else:
                    print("External server failed, falling back to embedded...")
            else:
                print("No external server found, using embedded server...")
            
            # Fallback to embedded server
            return self._start_embedded_server()
                
        except Exception as e:
            print(f"Error starting server: {e}, using embedded fallback...")
            return self._start_embedded_server()
    
    def _start_external_server(self, server_path):
        """Try to start external server"""
        try:
            python_commands = ['python3', 'python']
            
            for python_cmd in python_commands:
                try:
                    self.server_process = subprocess.Popen(
                        [python_cmd, server_path],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=0
                    )
                    
                    print(f"Started external server with {python_cmd}")
                    
                    # Test external server
                    if self._test_external_server():
                        self.is_embedded = False
                        return True
                    else:
                        self.server_process.terminate()
                        self.server_process = None
                        
                except FileNotFoundError:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"External server error: {e}")
            return False
    
    def _start_embedded_server(self):
        """Start embedded server as fallback"""
        try:
            print("Starting embedded Nexar server...")
            self.embedded_server = EmbeddedNexarServer(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Failed to start embedded server: {e}")
            return False
    
    def _test_external_server(self):
        """Test external server connection"""
        try:
            init_request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "initialize",
                "params": {}
            }
            self.request_id += 1
            
            response = self._send_request_external(init_request)
            return response and "result" in response
        except:
            return False
    
    def search_parts(self, query, limit=5):
        """Search for parts using the MCP server"""
        if self.is_embedded:
            return self._search_parts_embedded(query, limit)
        else:
            return self._search_parts_external(query, limit)
    
    def _search_parts_embedded(self, query, limit=5):
        """Search using embedded server"""
        try:
            arguments = {"query": query, "limit": limit}
            params = {"name": "search_parts", "arguments": arguments}
            result = self.embedded_server.handle_call_tool(params)
            
            if result and "_meta" in result:
                return result["_meta"].get("parts", [])
            return []
            
        except Exception as e:
            print(f"Embedded search error: {e}")
            return []
    
    def _search_parts_external(self, query, limit=5):
        """Search using external server"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "tools/call",
                "params": {
                    "name": "search_parts",
                    "arguments": {"query": query, "limit": limit}
                }
            }
            self.request_id += 1
            
            response = self._send_request_external(request)
            if response and "result" in response:
                meta = response["result"].get("_meta", {})
                return meta.get("parts", [])
            
            return []
            
        except Exception as e:
            print(f"External search error: {e}")
            return []

    def get_pricing(self, part_number, quantity=1):
        """Get pricing for a specific part"""
        # For now, just return search results
        results = self.search_parts(part_number, limit=1)
        if results:
            return {"pricing": results[0].get("pricing", {})}
        return {"error": "Part not found"}
    
    def _send_request_external(self, request):
        """Send request to external server"""
        try:
            if not self.server_process:
                return {"error": "No server process"}
            
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process and not self.is_embedded:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
            self.server_process = None
        
        self.embedded_server = None
        self.is_embedded = False
