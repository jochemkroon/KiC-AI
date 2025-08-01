#!/usr/bin/env python3
"""
Nexar API MCP Server
Provides component search and pricing via Model Context Protocol (MCP)
"""

import json
import sys
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NexarServer:
    """MCP Server for Nexar API integration"""
    
    def __init__(self):
        self.capabilities = {
            "tools": [
                {
                    "name": "search_parts",
                    "description": "Search for electronic components and get pricing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Component search query (part number, description, etc.)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_pricing",
                    "description": "Get detailed pricing for a specific part",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string", 
                                "description": "Exact part number to get pricing for"
                            }
                        },
                        "required": ["part_number"]
                    }
                }
            ]
        }
        
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "nexar-server",
                "version": "1.0.0"
            }
        }
        
    def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tools request"""
        return {"tools": self.capabilities["tools"]}
        
    def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "search_parts":
            return self._search_parts(arguments)
        elif tool_name == "get_pricing":
            return self._get_pricing(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
            
    def _search_parts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for parts - demo implementation with realistic data"""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        
        logger.info(f"Searching for parts: {query} (limit: {limit})")
        
        # Demo data with realistic component information
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
                "part_number": "STM32F4DISCOVERY",
                "manufacturer": "STMicroelectronics", 
                "description": "Development board for STM32F407VG MCU",
                "category": "Development Boards",
                "pricing": {
                    "Digi-Key": {"price_1": 23.50, "price_10": 22.15, "price_100": 19.85, "stock": 456},
                    "Mouser": {"price_1": 24.12, "price_10": 22.78, "price_100": 20.34, "stock": 234}
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
                    "Mouser": {"price_1": 0.48, "price_10": 0.41, "price_100": 0.28, "stock": 8967},
                    "Farnell": {"price_1": 0.52, "price_10": 0.44, "price_100": 0.31, "stock": 6789}
                }
            },
            {
                "part_number": "ATMEGA328P-PU",
                "manufacturer": "Microchip Technology",
                "description": "8-bit AVR Microcontroller, 32KB Flash, 28-Pin PDIP",
                "category": "Microcontrollers",
                "pricing": {
                    "Digi-Key": {"price_1": 2.45, "price_10": 2.15, "price_100": 1.85, "stock": 3456},
                    "Mouser": {"price_1": 2.52, "price_10": 2.22, "price_100": 1.91, "stock": 2789},
                    "Farnell": {"price_1": 2.67, "price_10": 2.35, "price_100": 2.05, "stock": 1567}
                }
            }
        ]
        
        # Simple search matching
        results = []
        query_lower = query.lower()
        
        for part in demo_parts:
            if (query_lower in part["part_number"].lower() or 
                query_lower in part["description"].lower() or
                query_lower in part["manufacturer"].lower()):
                results.append(part)
                
            if len(results) >= limit:
                break
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(results)} parts matching '{query}'"
                }
            ],
            "isError": False,
            "_meta": {
                "parts": results
            }
        }
        
    def _get_pricing(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed pricing for a specific part"""
        part_number = args.get("part_number", "")
        
        logger.info(f"Getting pricing for part: {part_number}")
        
        # This would normally call the real Nexar API
        # For demo, return sample pricing
        return {
            "content": [
                {
                    "type": "text", 
                    "text": f"Pricing for {part_number} (demo data)"
                }
            ],
            "isError": False,
            "_meta": {
                "pricing": {
                    "Digi-Key": {"price_1": 5.99, "price_10": 5.49, "stock": 1000},
                    "Mouser": {"price_1": 6.15, "price_10": 5.65, "stock": 750}
                }
            }
        }
        
    def run(self):
        """Main server loop - reads JSON-RPC requests from stdin"""
        logger.info("Nexar MCP Server starting...")
        
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    request = json.loads(line)
                    logger.debug(f"Received request: {request}")
                    
                    # Handle different MCP methods
                    method = request.get("method")
                    params = request.get("params", {})
                    request_id = request.get("id")
                    
                    if method == "initialize":
                        result = self.handle_initialize(params)
                    elif method == "tools/list":
                        result = self.handle_list_tools(params)
                    elif method == "tools/call":
                        result = self.handle_call_tool(params)
                    else:
                        raise ValueError(f"Unknown method: {method}")
                    
                    # Send response
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                    
                    response_json = json.dumps(response)
                    print(response_json)
                    sys.stdout.flush()
                    logger.debug(f"Sent response: {response_json}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
                except Exception as e:
                    logger.error(f"Request processing error: {e}")
                    error_response = {
                        "jsonrpc": "2.0", 
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {"code": -32603, "message": str(e)}
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception as e:
            logger.error(f"Server error: {e}")

if __name__ == "__main__":
    server = NexarServer()
    server.run()
