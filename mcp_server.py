"""MCP server for Token Cost Forecaster & Context Budgeter."""
import sys
import json
from client import TokenCostForecaster

def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "forecast_and_budget",
                    "description": "Forecast model invocation cost and check against hard organizational budget limits",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt_text": {"type": "string"},
                            "expected_completion_tokens": {"type": "integer", "default": 500},
                            "accumulated_spend_usd": {"type": "number"},
                            "hard_budget_cap_usd": {"type": "number"},
                            "pricing": {"type": "object"}
                        },
                        "required": ["prompt_text", "accumulated_spend_usd", "hard_budget_cap_usd"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "forecast_and_budget":
            out = TokenCostForecaster.forecast_and_budget(
                args.get("prompt_text", ""),
                int(args.get("expected_completion_tokens", 500)),
                float(args.get("accumulated_spend_usd", 0.0)),
                float(args.get("hard_budget_cap_usd", 10.0)),
                args.get("pricing")
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
    return {"error": "Unsupported method or tool"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
