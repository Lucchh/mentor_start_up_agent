"""
Main entrypoint for the Mentor MCP server.
Exposes CrewAI mentor/student agents as MCP tools.
"""

from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import os, sys, traceback

# --- Load .env using an absolute path so it works regardless of CWD ---
ROOT = Path(__file__).resolve().parents[1]  # .../Assignment_1
load_dotenv(ROOT / ".env")

# --- Logging helper (stderr only, safe for MCP) ---
def _elog(msg: str) -> None:
    try:
        sys.stderr.write(msg.rstrip() + "\n")
    except Exception:
        pass

# Model controls
DEFAULT_MODEL = os.getenv("MENTOR_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = os.getenv("MENTOR_MODEL_FALLBACK", "gpt-4o")

# MCP server
mcp = FastMCP("mentor-mcp")

# ======================================================
#   SHARED IMPLEMENTATIONS (used by both MCP + NANDA)
# ======================================================

def _explain_topic_impl(topic: str) -> str:
    """Shared implementation of topic explanation."""
    from crewai import Agent, Task, Crew, Process

    def crew_agent_logic(topic: str, model: str) -> str:
        student = Agent(
            role="Harvard Data Science Student",
            goal="Summarize technical concepts clearly and accurately",
            backstory="You are Luc, a Harvard Data Science student...",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        mentor = Agent(
            role="Content Mentor",
            goal="Rewrite technical explanations in simple, approachable language",
            backstory="Approachable mentor who avoids jargon.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        research_task = Task(
            description=f"Research the topic: {topic}",
            expected_output="Definition, key concepts, how it works, example applications",
            agent=student,
        )

        writing_task = Task(
            description=f"Rewrite the findings on {topic} for beginners.",
            expected_output=f"A peer-friendly explanation of {topic}",
            agent=mentor,
        )

        crew = Crew(
            agents=[student, mentor],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=False,
        )
        return str(crew.kickoff())

    try:
        return crew_agent_logic(topic, DEFAULT_MODEL)
    except Exception as e:
        _elog(f"[explain_topic] Error: {e}\n{traceback.format_exc()}")
        if FALLBACK_MODEL and FALLBACK_MODEL != DEFAULT_MODEL:
            try:
                return crew_agent_logic(topic, FALLBACK_MODEL)
            except Exception as e2:
                _elog(f"[explain_topic] Fallback error: {e2}\n{traceback.format_exc()}")
        return "Sorry, explanation tool failed. Check API key or model."


def _startup_brief_impl(idea_prompt: str) -> str:
    """Shared implementation of startup brief."""
    from crewai import Agent, Task, Crew, Process

    def run_startup_brief(prompt: str, model: str) -> str:
        # ---------- Agents ----------
        analyst = Agent(
            role="Market Analyst",
            goal="Define ICP, JTBD, pains, competitors, why-now, market size.",
            backstory="Seasoned operator, focuses ideas until inevitable.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        techlead = Agent(
            role="Technical Lead",
            goal="Design simplest feasible MVP, estimate costs/latency.",
            backstory="Startup engineer who ships fast, de-risks early.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        pm = Agent(
            role="Product Manager",
            goal="Turn insights into a crisp MVP spec and 2-week plan.",
            backstory="Zero-to-one PM, testable user stories, fast learning.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        growth = Agent(
            role="Growth Strategist",
            goal="Craft day-0 and day-30 GTM with channels & experiments.",
            backstory="Growth hacker validating fast, small experiments.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        counsel = Agent(
            role="Risk & Privacy Counsel",
            goal="Flag risks and propose lightweight mitigations.",
            backstory="Pragmatic advisor for privacy, IP, compliance.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        pitch = Agent(
            role="Pitch Writer",
            goal="Synthesize into a one-page brief & tight 30s pitch.",
            backstory="Clear communicator, makes ideas understandable.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        # ---------- Tasks ----------
        analysis = Task(
            description=f"Pick ONE strongest direction from prompt: {prompt}. Output chosen direction, ICP, JTBD, pains, competitors, why now, market size, riskiest assumption.",
            expected_output="Concise opportunity analysis with Chosen Direction + ICP + JTBD + Pains + Competitors + Why Now + Market Size + Riskiest Assumption.",
            agent=analyst,
        )

        tech = Task(
            description="Design simplest MVP system with costs/latency & privacy/security notes.",
            expected_output="MVP architecture, components, costs, latency, risks, privacy notes.",
            agent=techlead,
        )

        product = Task(
            description="Translate analysis + architecture into 2-week MVP build plan with user stories.",
            expected_output="MVP spec with stories, schema, milestones, metrics.",
            agent=pm,
        )

        gtm = Task(
            description="Day-0 & day-30 GTM plan: 3 channels, 2 experiments each, tagline, pricing, outreach.",
            expected_output="GTM plan with channels, experiments, tagline, pricing, outreach message.",
            agent=growth,
        )

        risk = Task(
            description="Identify legal/ethical/privacy/IP concerns & mitigations.",
            expected_output="Risks & mitigations across privacy, security, IP, safety.",
            agent=counsel,
        )

        final_pitch = Task(
            description="Synthesize everything into one-page brief + 30s spoken pitch + tagline + names.",
            expected_output="One-page venture brief, 30s pitch, tagline, 3 name options.",
            agent=pitch,
        )

        crew = Crew(
            agents=[analyst, techlead, pm, growth, counsel, pitch],
            tasks=[analysis, tech, product, gtm, risk, final_pitch],
            process=Process.sequential,
            verbose=False,
        )
        return str(crew.kickoff())

    try:
        return run_startup_brief(idea_prompt, DEFAULT_MODEL)
    except Exception as e:
        _elog(f"[startup_brief] Error: {e}\n{traceback.format_exc()}")
        if FALLBACK_MODEL and FALLBACK_MODEL != DEFAULT_MODEL:
            try:
                return run_startup_brief(idea_prompt, FALLBACK_MODEL)
            except Exception as e2:
                _elog(f"[startup_brief] Fallback error: {e2}\n{traceback.format_exc()}")
        return "Sorry, startup brief tool failed. Check API key or model."


# ======================================================
#   MCP TOOLS (for Claude Desktop)
# ======================================================

@mcp.tool()
def ping() -> str:
    """Health check for MCP."""
    return "ok"

@mcp.tool()
def explain_topic(topic: str) -> str:
    """Explain topic (MCP version)."""
    return _explain_topic_impl(topic)

@mcp.tool()
def startup_brief(idea_prompt: str) -> str:
    """Startup brief (MCP version)."""
    return _startup_brief_impl(idea_prompt)


# ======================================================
#   PLAIN WRAPPERS (for NANDA / Flask adapter)
# ======================================================

def explain_topic_plain(topic: str) -> str:
    return _explain_topic_impl(topic)

def startup_brief_plain(idea_prompt: str) -> str:
    return _startup_brief_impl(idea_prompt)


# ======================================================
#   MAIN ENTRYPOINT
# ======================================================

def main() -> None:
    """Entrypoint for running the Mentor MCP server."""
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
