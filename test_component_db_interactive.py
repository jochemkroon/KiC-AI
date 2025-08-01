#!/usr/bin/env python3
"""
Interactive test for component_db MCP server
Shows you exactly how to communicate with the server
"""

import subprocess
import json
import sys
import time

def test_component_db_interactive():
    """Test component_db server interactively"""
    print("🧪 Interactive Component DB Test")
    print("=" * 40)
    
    # Start the server process
    print("Starting component_db server...")
    try:
        process = subprocess.Popen(
            ["python3", "-m", "mcp_servers.component_db"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        def send_request(request_dict):
            """Send a JSON-RPC request and get response"""
            request_json = json.dumps(request_dict) + "\n"
            print(f"\n📤 Sending: {request_json.strip()}")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            response = process.stdout.readline()
            if response:
                print(f"📥 Response: {response.strip()}")
                return json.loads(response.strip())
            else:
                print("❌ No response received")
                return None
        
        # Test 1: Initialize
        print("\n1️⃣ Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = send_request(init_request)
        
        if response and "result" in response:
            print("✅ Initialize successful!")
            server_info = response["result"]["serverInfo"]
            print(f"   Server: {server_info['name']} v{server_info['version']}")
        else:
            print("❌ Initialize failed!")
            return
        
        # Test 2: List tools
        print("\n2️⃣ Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        response = send_request(tools_request)
        
        if response and "result" in response:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Tools/list failed!")
            return
        
        # Test 3: Call a tool
        print("\n3️⃣ Testing tools/call - search_components...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3, 
            "method": "tools/call",
            "params": {
                "name": "search_components",
                "arguments": {
                    "type": "resistor",
                    "specs": {"value": "10k"}
                }
            }
        }
        response = send_request(call_request)
        
        if response and "result" in response:
            print("✅ Tool call successful!")
            print(f"   Result: {json.dumps(response['result'], indent=2)}")
        else:
            print("❌ Tool call failed!")
            if response and "error" in response:
                print(f"   Error: {response['error']}")
        
        # Test 4: Get pricing
        print("\n4️⃣ Testing tools/call - get_pricing...")
        pricing_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call", 
            "params": {
                "name": "get_pricing",
                "arguments": {
                    "part_numbers": ["R1", "C1"]
                }
            }
        }
        response = send_request(pricing_request)
        
        if response and "result" in response:
            print("✅ Pricing request successful!")
            print(f"   Result: {json.dumps(response['result'], indent=2)}")
        else:
            print("❌ Pricing request failed!")
            if response and "error" in response:
                print(f"   Error: {response['error']}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
    finally:
        # Clean up
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)
    
    print("\n💡 Manual test instructions:")
    print("To test manually, run:")
    print("python3 -m mcp_servers.component_db")
    print("\nThen send JSON-RPC requests like:")
    print('{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}')
    print("\n⚠️ Important: Each request must end with a newline!")

if __name__ == "__main__":
    test_component_db_interactive()
