#!/usr/bin/env python3
"""
MIT AI Studio - Crew AI Tech Track
Digital Twin Example: Luc's AI Agents
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileWriterTool
from dotenv import load_dotenv
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
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_').lower()
    filename = f"{safe_topic}_explained.md"
    
    return Agent(
        role="Content Mentor",
        goal="Rewrite technical explanations into simple, approachable language",
        backstory="""You are Luc's approachable mentor persona.
        You explain concepts without jargon so peers can quickly understand.""",
        verbose=True,
        allow_delegation=False,
        tools=[FileWriterTool(file_path=filename)]  # Dynamic filename
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
    # Create a safe filename from the topic
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_').lower()
    filename = f"{safe_topic}_explained.md"
    
    return Task(
        description=f"Take the research findings on {topic} and rewrite them \
        in simple, beginner-friendly language. Use the FileWriterTool to save \
        the result to '{filename}'.",
        expected_output=f"A markdown file with a peer-friendly explanation saved as {filename}",
        agent=agent
    )

# --- Main Crew Orchestration ---

def main():
    print("🚀 Starting Luc's CrewAI Digital Twin")
    print("=" * 50)

    topic = input("Enter a topic you'd like Luc's agent to explain (default: SimCLR): ")
    if not topic.strip():
        topic = "SimCLR"
        print(f"Using default topic: {topic}")

    # Create agents
    student = create_student_agent()
    mentor = create_mentor_agent(topic)

    # Create tasks
    research_task = create_research_task(student, topic)
    writing_task = create_writing_task(mentor, topic)

    # Assemble crew
    crew = Crew(
        agents=[student, mentor],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True
    )

    # Run crew
    print("\n🎯 Executing crew...\n")
    result = crew.kickoff()

    print("\n✅ Crew execution completed!")
    print("=" * 50)
    print(result)

if __name__ == "__main__":
    main()