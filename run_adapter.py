#!/usr/bin/env python3
"""
Run adapter for NANDA + Mentor MCP server
"""

import os
from dotenv import load_dotenv
from nanda_adapter import NANDA
from mentor_mcp.main import startup_brief_plain as startup_brief


# Load env variables
load_dotenv()

def improvement_fn(message: str):
    """Custom logic for message improvement"""
    if not message:
        return {"response": "No input provided."}

    if message.lower().startswith("startup:"):
        result = startup_brief(message[len("startup:"):].strip())
    else:
        result = explain_topic(message)

    return {"response": str(result)}

def main():
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    domain = os.getenv("DOMAIN_NAME")

    if not api_key:
        raise RuntimeError("No API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    if not domain:
        raise RuntimeError("DOMAIN_NAME not set in .env")

    # Run NANDA with your logic
    nanda = NANDA(improvement_fn)
    nanda.start_server_api(api_key, domain)

if __name__ == "__main__":
    main()
