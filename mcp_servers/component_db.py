#!/usr/bin/env python3
"""
Simple MCP Server for component database functionality
This demonstrates how to create an MCP server for KiCad integration
"""

import json
import sys
import asyncio
from typing import Dict, List, Any

class ComponentDatabaseServer:
    """Simple component database MCP server"""
    
    def __init__(self):
        self.component_db = {
            # Sample component database
            "R1": {
                "type": "resistor",
                "value": "10k",
                "package": "0805",
                "price": 0.02,
                "stock": 5000,
                "alternatives": ["R1206-10K", "R0603-10K"]
            },
            "C1": {
                "type": "capacitor", 
                "value": "100nF",
                "package": "0805",
                "price": 0.05,
                "stock": 2000,
                "alternatives": ["C1206-100N", "C0603-100N"]
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "component-database",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "search_components",
                            "description": "Search for components by type and specifications",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "specs": {"type": "object"}
                                }
                            }
                        },
                        {
                            "name": "get_pricing",
                            "description": "Get pricing for component part numbers",
                            "inputSchema": {
                                "type": "object", 
                                "properties": {
                                    "part_numbers": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        {
                            "name": "check_availability",
                            "description": "Check stock availability for components",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "part_numbers": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "search_components":
                component_type = arguments.get("type", "")
                specs = arguments.get("specs", {})
                
                # Search through component database
                results = []
                for part_id, component in self.component_db.items():
                    # Filter by type if specified
                    if component_type and component.get("type", "").lower() != component_type.lower():
                        continue
                    
                    # Filter by specs if specified
                    match = True
                    for spec_key, spec_value in specs.items():
                        if spec_key in component:
                            if str(component[spec_key]).lower() != str(spec_value).lower():
                                match = False
                                break
                    
                    if match:
                        results.append({
                            "part_id": part_id,
                            "type": component.get("type"),
                            "value": component.get("value"),
                            "package": component.get("package"),
                            "price": component.get("price"),
                            "stock": component.get("stock"),
                            "alternatives": component.get("alternatives", [])
                        })
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "components": results,
                        "total_found": len(results)
                    }
                }
            
            elif tool_name == "get_pricing":
                part_numbers = arguments.get("part_numbers", [])
                pricing = {}
                for part in part_numbers:
                    if part in self.component_db:
                        pricing[part] = {
                            "unit_price": self.component_db[part]["price"],
                            "stock": self.component_db[part]["stock"]
                        }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"pricing": pricing}
                }
            
            elif tool_name == "check_availability":
                part_numbers = arguments.get("part_numbers", [])
                availability = {}
                for part in part_numbers:
                    if part in self.component_db:
                        availability[part] = self.component_db[part]["stock"]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"availability": availability}
                }
        
        # Default error response
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"}
        }

async def main():
    """Main MCP server loop"""
    server = ComponentDatabaseServer()
    
    # Read from stdin, write to stdout (MCP protocol)
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
