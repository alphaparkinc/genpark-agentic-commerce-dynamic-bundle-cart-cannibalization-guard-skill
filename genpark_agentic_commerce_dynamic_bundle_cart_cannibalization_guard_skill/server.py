# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Dynamic Bundle Cart Cannibalization Guard Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "evaluate_bundle_profitability_and_cannibalization",
    "description": "Assess proposed bundle discount to prevent cannibalizing high-margin standalone purchases while maximizing Average Order Value (AOV).",
    "inputSchema": {
      "type": "object",
      "properties": {
        "primary_item_price_usd": {
          "type": "number"
        },
        "primary_item_margin_pct": {
          "type": "number"
        },
        "bundled_addon_price_usd": {
          "type": "number"
        },
        "bundled_addon_margin_pct": {
          "type": "number"
        },
        "proposed_bundle_discount_pct": {
          "type": "number"
        }
      },
      "required": [
        "primary_item_price_usd",
        "primary_item_margin_pct",
        "bundled_addon_price_usd",
        "bundled_addon_margin_pct",
        "proposed_bundle_discount_pct"
      ]
    }
  },
  {
    "name": "synthesize_personalized_bundle_offer",
    "description": "Generate multi-item bundle copy with tiered savings presentation and margin-protected promotional callout.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "bundle_title": {
          "type": "string"
        },
        "primary_item_name": {
          "type": "string"
        },
        "addon_item_name": {
          "type": "string"
        },
        "approved_discount_pct": {
          "type": "number"
        },
        "net_bundle_price_usd": {
          "type": "number"
        }
      },
      "required": [
        "bundle_title",
        "primary_item_name",
        "addon_item_name",
        "approved_discount_pct",
        "net_bundle_price_usd"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-agentic-commerce-dynamic-bundle-cart-cannibalization-guard-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-agentic-commerce-dynamic-bundle-cart-cannibalization-guard-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "evaluate_bundle_profitability_and_cannibalization",
            "arguments": {
                "primary_item_price_usd": 120.0,
                "primary_item_margin_pct": 55.0,
                "bundled_addon_price_usd": 40.0,
                "bundled_addon_margin_pct": 60.0,
                "proposed_bundle_discount_pct": 15.0
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: evaluate_bundle_profitability_and_cannibalization")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
