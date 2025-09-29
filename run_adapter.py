# run_adapter.py
from dotenv import load_dotenv
from nanda_adapter import NANDA
import os

# Load env variables
load_dotenv()

from mentor_mcp.main import explain_topic, startup_brief

def improvement_fn(message: str) -> str:
    if message.lower().startswith("startup:"):
        return startup_brief(message[len("startup:"):].strip())
    else:
        return explain_topic(message)

def main():
    # Here we don’t need Anthropic key
    openai_key = os.getenv("OPENAI_API_KEY")
    domain = os.getenv("DOMAIN_NAME")

    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    nanda = NANDA(improvement_fn)
    # Pass openai_key to start_server_api so adapter has it
    nanda.start_server_api(openai_key, domain)

if __name__ == "__main__":
    main()
