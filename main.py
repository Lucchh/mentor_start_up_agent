#!/usr/bin/env python3
"""
MIT AI Studio - Crew AI Tech Track
Digital Twin Example: Luc's AI Agents
"""

import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from nanda_adapter import NANDA  
load_dotenv()

# --- Agent Definitions ---

def create_student_agent():
    return Agent(
        role="Harvard Data Science Student",
        goal="Summarize technical concepts clearly and accurately",
        backstory="""You are Luc, a Harvard Data Science student.
        You are curious, diligent, and skilled in ML, causal inference,
        and anomaly detection. You focus on clarity and depth.""",
        verbose=True,
        allow_delegation=False
    )

def create_mentor_agent(topic):
    return Agent(
        role="Content Mentor",
        goal="Rewrite technical explanations into simple, approachable language",
        backstory="""You are Luc's approachable mentor persona.
        You explain concepts without jargon so peers can quickly understand.""",
        verbose=True,
        allow_delegation=False
    )
# --- Task Definitions ---

def create_research_task(agent, topic):
    return Task(
        description=f"Research the topic: {topic}. Provide a structured summary \
        of what it is, how it works, and why it is important.",
        expected_output="""A clear, well-structured research summary with:
        - Definition
        - Key concepts
        - How it works
        - Example applications""",
        agent=agent
    )

def create_writing_task(agent, topic):
    return Task(
        description=f"Take the research findings on {topic} and rewrite them \
        in simple, beginner-friendly language. Return the explanation as plain text.",
        expected_output=f"A peer-friendly explanation of {topic} as plain text",
        agent=agent
    )

# --- Crew Logic wrapped for NANDA ---

def crew_agent_logic(message_text: str) -> str:
    """This function runs your CrewAI pipeline on a given topic."""
    topic = message_text.strip()
    if not topic:
        topic = "SimCLR"

    student = create_student_agent()
    mentor = create_mentor_agent(topic)

    research_task = create_research_task(student, topic)
    writing_task = create_writing_task(mentor, topic)

    crew = Crew(
        agents=[student, mentor],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()
    return str(result)

# --- NANDA Server Startup ---

if __name__ == "__main__":
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    domain = os.getenv("DOMAIN_NAME")

    # NANDA wraps your Crew logic
    nanda = NANDA(crew_agent_logic)
    nanda.start_server_api(anthropic_key, domain)