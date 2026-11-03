"""End-to-end MCP Protocol Handshake and Tool Execution Test."""

import json
import subprocess
import sys
from pathlib import Path


def test_mcp_server_protocol():
    python_exe = Path("D:/setup/antigravity-skillforge/.venv/Scripts/python.exe")
    proc = subprocess.Popen(
        [str(python_exe), "-m", "skillforge.mcp_server.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    def send_rpc(msg: dict):
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()

    def read_rpc():
        line = proc.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    try:
        # 1. Initialize
        send_rpc({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "AntigravityTestClient", "version": "2.6.0"}
            }
        })

        init_resp = read_rpc()
        assert init_resp is not None, "Failed to receive initialize response"
        assert "result" in init_resp, f"Initialize error: {init_resp.get('error')}"
        server_info = init_resp["result"].get("serverInfo", {})
        print(f"[PASS] MCP Handshake: Connected to {server_info.get('name')} v{server_info.get('version')}")

        # Send initialized notification
        send_rpc({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

        # 2. List tools
        send_rpc({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })

        tools_resp = read_rpc()
        assert tools_resp is not None, "Failed to receive tools/list response"
        tools = tools_resp["result"].get("tools", [])
        tool_names = [t["name"] for t in tools]
        print(f"[PASS] Tools Registered ({len(tool_names)}): {', '.join(tool_names)}")
        assert "recommend_skills" in tool_names
        assert "load_skill" in tool_names
        assert "skillforge_status" in tool_names

        # 3. Call recommend_skills tool
        send_rpc({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "recommend_skills",
                "arguments": {
                    "task": "Develop an Android mobile app with Jetpack Compose",
                    "project_path": "D:/setup",
                    "max_skills": 2
                }
            }
        })

        call_resp = read_rpc()
        assert call_resp is not None, "Failed to receive recommend_skills response"
        assert not call_resp["result"].get("isError"), f"Tool error: {call_resp['result']}"
        res_content = call_resp["result"]["content"][0]["text"]
        parsed_res = json.loads(res_content)
        print(f"[PASS] Tool Execution (recommend_skills): {parsed_res['selected_count']} skill(s) selected")
        print(f"       Primary skill: {parsed_res['recommendations'][0]['skill_name']}")

        # 4. Call load_skill tool
        primary_skill = parsed_res['recommendations'][0]['skill_name']
        send_rpc({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "load_skill",
                "arguments": {
                    "skill_name_or_id": primary_skill
                }
            }
        })

        load_resp = read_rpc()
        assert load_resp is not None, "Failed to receive load_skill response"
        load_content = load_resp["result"]["content"][0]["text"]
        parsed_load = json.loads(load_content)
        print(f"[PASS] Tool Execution (load_skill): Loaded {parsed_load['skill_name']} ({len(parsed_load['content'])} characters)")

        print("\nAll end-to-end MCP protocol checks passed!")

    finally:
        proc.terminate()
        proc.wait(timeout=2)


if __name__ == "__main__":
    test_mcp_server_protocol()
