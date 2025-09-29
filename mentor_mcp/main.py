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

# IMPORTANT: Do NOT print to stdout anywhere in this file.
# Use stderr for diagnostics (safe for MCP transport).
def _elog(msg: str) -> None:
    try:
        sys.stderr.write(msg.rstrip() + "\n")
    except Exception:
        pass

# Model controls (override in .env if you like)
DEFAULT_MODEL = os.getenv("MENTOR_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = os.getenv("MENTOR_MODEL_FALLBACK", "gpt-4o")

# Create MCP server
mcp = FastMCP("mentor-mcp")


@mcp.tool()
def ping() -> str:
    """
    Health check. Useful to verify that the MCP handshake works.
    """
    return "ok"


@mcp.tool()
def explain_topic(topic: str) -> str:
    """
    Explain a technical topic in beginner-friendly language.

    Arguments:
        topic (str): The technical concept to explain.
    """
    # Lazy-import heavy deps to make startup fast & avoid handshake timeouts
    from crewai import Agent, Task, Crew, Process

    def crew_agent_logic(topic: str, model: str) -> str:
        """Run the CrewAI mentor pipeline on a given topic."""
        # --- Student agent ---
        student = Agent(
            role="Harvard Data Science Student",
            goal="Summarize technical concepts clearly and accurately",
            backstory=(
                "You are Luc, a Harvard Data Science student. "
                "You are curious, diligent, and skilled in ML, causal inference, "
                "and anomaly detection. You focus on clarity and depth."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        # --- Mentor agent ---
        mentor = Agent(
            role="Content Mentor",
            goal="Rewrite technical explanations into simple, approachable language",
            backstory="You are Luc's approachable mentor who explains concepts without jargon.",
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        # --- Tasks ---
        research_task = Task(
            description=(
                f"Research the topic: {topic}. Provide a structured summary of "
                f"what it is, how it works, and why it is important."
            ),
            expected_output=(
                "A clear, well-structured research summary with:\n"
                "- Definition\n- Key concepts\n- How it works\n- Example applications"
            ),
            agent=student,
        )

        writing_task = Task(
            description=(
                f"Take the research findings on {topic} and rewrite them in simple, "
                f"beginner-friendly language. Return as plain text."
            ),
            expected_output=f"A peer-friendly explanation of {topic} as plain text",
            agent=mentor,
        )

        # --- Run CrewAI pipeline ---
        crew = Crew(
            agents=[student, mentor],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=False,
        )
        result = crew.kickoff()
        return str(result)

    # Try with DEFAULT_MODEL; fall back if provider/model mismatch
    try:
        return crew_agent_logic(topic, DEFAULT_MODEL)
    except Exception as e:
        _elog(f"[explain_topic] Error with model {DEFAULT_MODEL}: {e}\n{traceback.format_exc()}")
        if FALLBACK_MODEL and FALLBACK_MODEL != DEFAULT_MODEL:
            try:
                return crew_agent_logic(topic, FALLBACK_MODEL)
            except Exception as e2:
                _elog(f"[explain_topic] Fallback {FALLBACK_MODEL} also failed: {e2}\n{traceback.format_exc()}")
        return (
            "Sorry, the explanation tool failed to run. "
            "Check your API key, model access, and network, then try again."
        )


@mcp.tool()
def startup_brief(idea_prompt: str) -> str:
    """
    Generate a focused, one-page startup brief from a seed prompt or problem statement.
    Returns ONE strongest direction (not a list) with crisp MVP & GTM.

    Arguments:
        idea_prompt (str): The domain, problem, or spark
                           (e.g., 'AI copilot for hospital prior auth').
    """
    # Lazy-import heavy deps to make startup fast & avoid handshake timeouts
    from crewai import Agent, Task, Crew, Process

    def run_startup_brief(prompt: str, model: str) -> str:
        """
        Orchestrates a small venture-creation crew. Produces ONE strongest idea,
        not a list, with a crisp MVP and GTM you can execute immediately.
        Aim for ~600–900 words (tight, no fluff).
        """
        # ---------- Agents ----------
        analyst = Agent(
            role="Market Analyst",
            goal="Choose one sharp opportunity and define ICP, JTBD, pains, alternatives, and why-now.",
            backstory=(
                "Seasoned operator who focuses ideas until they become inevitable. "
                "You make pragmatic assumptions explicit and avoid hand-wavy market talk."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        techlead = Agent(
            role="Technical Lead",
            goal="Design the simplest feasible architecture and estimate costs/latency for an MVP.",
            backstory=(
                "Startup engineer who ships fast and de-risks. "
                "Prefer boring, proven tools and minimal scope to reach user value quickly."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        pm = Agent(
            role="Product Manager",
            goal="Turn insights into a crisp MVP spec with acceptance criteria and a 2-week build plan.",
            backstory=(
                "Zero-to-one PM. Writes user stories that are testable, small, and measurable. "
                "Obsessed with learning velocity over feature breadth."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        growth = Agent(
            role="Growth Strategist",
            goal="Craft day-0 and day-30 GTM: channels, experiments, messaging, and early pricing.",
            backstory=(
                "Hands-on growth hacker who validates fast. "
                "Designs small, falsifiable experiments with clear success criteria."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        counsel = Agent(
            role="Risk & Privacy Counsel",
            goal="Flag legal/ethical/compliance risks and propose lightweight mitigations appropriate for an MVP.",
            backstory=(
                "Pragmatic advisor who keeps early products safe without blocking learning. "
                "Focus on privacy, data usage, IP, and model/AI safety concerns."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        pitch = Agent(
            role="Pitch Writer",
            goal="Synthesize into a one-page brief and compelling 30-second pitch ready to share.",
            backstory=(
                "Clear communicator who makes technical ideas instantly understandable. "
                "Removes fluff and makes next steps obvious."
            ),
            model=model,
            verbose=False,
            allow_delegation=False,
        )

        # ---------- Tasks ----------
        analysis = Task(
            description=(
                "From the seed prompt below, consider adjacent opportunities but PICK ONE strongest direction. "
                "Define:\n"
                f"- Seed prompt: {prompt}\n"
                "- Ideal Customer Profile (ICP) and buyer vs. user\n"
                "- Jobs-To-Be-Done & top pains (ranked)\n"
                "- Current alternatives and 3–5 notable competitors\n"
                "- Why now (enablers, regulations, platform shifts)\n"
                "- Market sizing guesstimates (TAM/SAM/SOM) with explicit assumptions\n"
                "- Key uncertainties & the single riskiest assumption to test first\n"
                "Output MUST select exactly one 'Chosen Direction' to pursue."
            ),
            expected_output=(
                "Concise brief sections: Chosen Direction, ICP, JTBD, Pains, Alternatives, "
                "Competitors, Why Now, Market Size (TAM/SAM/SOM with assumptions), "
                "Riskiest Assumption."
            ),
            agent=analyst,
        )

        tech = Task(
            description=(
                "Design the simplest feasible MVP system for the Chosen Direction. "
                "Prefer boring, hosted services. Estimate unit costs and p50 latency per key action."
            ),
            expected_output=(
                "Architecture Outline (text), Core Components, Data sources, "
                "Model selection (if any), Build risks & unknowns, "
                "Per-request cost and p50 latency estimates, "
                "Notes on privacy/security for MVP."
            ),
            agent=techlead,
        )

        product = Task(
            description=(
                "Translate analysis + architecture into an MVP that can be built in ~2 weeks. "
                "Include small, testable user stories with acceptance criteria and telemetry."
            ),
            expected_output=(
                "MVP Spec with:\n"
                "- User stories (3–7) each with acceptance criteria\n"
                "- Simple schema or data model (if applicable)\n"
                "- 2-week plan with day-by-day milestones\n"
                "- Instrumentation (events + properties)\n"
                "- Success metrics: 1 North Star + 3 leading indicators"
            ),
            agent=pm,
        )

        gtm = Task(
            description=(
                "Create day-0 and day-30 GTM. Small, falsifiable experiments. "
                "Propose initial pricing/packaging and messaging for the ICP."
            ),
            expected_output=(
                "GTM Plan:\n"
                "- Channels (3) with 2 experiments each (setup, target, success criteria)\n"
                "- Positioning & 10-word tagline draft\n"
                "- Initial pricing/packaging assumptions\n"
                "- First-user outreach email and a tweet-length pitch"
            ),
            agent=growth,
        )

        risk = Task(
            description=(
                "Identify legal/ethical/privacy concerns, IP/trademark pitfalls, data handling risks, "
                "and propose practical mitigations suitable for an MVP."
            ),
            expected_output=(
                "Risks & Mitigations:\n"
                "- Privacy/data usage\n"
                "- Security access scope\n"
                "- IP/trademark naming notes\n"
                "- Model/AI safety concerns\n"
                "- Red flags & unknowns"
            ),
            agent=counsel,
        )

        final_pitch = Task(
            description=(
                "Synthesize all prior outputs into a single one-page venture brief and a tight pitch. "
                "Do NOT produce a list of ideas; commit to the chosen direction."
            ),
            expected_output=(
                "One-Page Venture Brief:\n"
                "1) TL;DR (one sentence)\n"
                "2) Problem → Solution\n"
                "3) ICP & Why Now\n"
                "4) Differentiation vs. Alternatives\n"
                "5) MVP Spec (bullet summary)\n"
                "6) Architecture (summary + cost/latency)\n"
                "7) GTM (channels + first experiments)\n"
                "8) Risks & Mitigations\n"
                "9) Metrics (NSM + 3 leading indicators)\n"
                "10) Next 3 steps (weekend build)\n\n"
                "Also include:\n"
                "- 30-second spoken pitch\n"
                "- 10-word tagline\n"
                "- 3 product name options"
            ),
            agent=pitch,
        )

        # ---------- Run Crew ----------
        crew = Crew(
            agents=[analyst, techlead, pm, growth, counsel, pitch],
            tasks=[analysis, tech, product, gtm, risk, final_pitch],
            process=Process.sequential,
            verbose=False,
        )
        result = crew.kickoff()
        return str(result)

    try:
        return run_startup_brief(idea_prompt, DEFAULT_MODEL)
    except Exception as e:
        _elog(f"[startup_brief] Error with model {DEFAULT_MODEL}: {e}\n{traceback.format_exc()}")
        if FALLBACK_MODEL and FALLBACK_MODEL != DEFAULT_MODEL:
            try:
                return run_startup_brief(idea_prompt, FALLBACK_MODEL)
            except Exception as e2:
                _elog(f"[startup_brief] Fallback {FALLBACK_MODEL} also failed: {e2}\n{traceback.format_exc()}")
        return (
            "Sorry, the startup brief tool failed to run. "
            "Check your API key, model access, and network, then try again."
        )


def main() -> None:
    """Entrypoint for running the Mentor MCP server."""
    # Choose transport by env var:
    # - local desktop host: MCP_TRANSPORT=stdio
    # - cloud (for NANDA): MCP_TRANSPORT=sse  (HTTP(S) SSE endpoint)
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        # SSE/HTTP server (what NANDA expects: an HTTP URL)
        mcp.run(transport="sse", host=host, port=port)
    else:
        # local stdio for Claude/ChatGPT desktop
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

