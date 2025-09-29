# test_local.py
from mentor_mcp.main import crew_agent_logic

if __name__ == "__main__":
    result = crew_agent_logic("causal inference")
    print("Result:\n", result)
