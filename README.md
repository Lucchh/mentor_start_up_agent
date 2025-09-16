# Luc's AI Agent - CrewAI Digital Twin

A CrewAI-powered system that simulates Luc's learning process through collaborative AI agents. One agent researches technical topics (like a Harvard Data Science student), while another rewrites the findings into beginner-friendly explanations.

## 🚀 Features

- **Dual-Agent System**: Research agent + Content mentor agent
- **Interactive Topic Selection**: Choose any technical topic to explore
- **Automatic File Generation**: Creates markdown explanations automatically
- **Sequential Processing**: Agents work together in a structured workflow
- **Beginner-Friendly Output**: Complex topics explained in simple terms
- **Environment Configuration**: Uses `.env` files for secure API key management

## 📁 Project Structure

```
AI Agent/
├── Assignment_1/
│   ├── main.py                 # Main CrewAI orchestration script
│   ├── requirements.txt        # Python dependencies
│   ├── .gitignore             # Git ignore patterns
│   ├── simclr_explained.md    # Example output file
│   ├── ai_agent_explained.md  # Example output file
└── README.md                  
```

## 🛠️ Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (or other LLM provider API key)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd "/Users/lucchen/Desktop/AI Agent"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd Assignment_1
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   
   Create a `.env` file in the Assignment_1 directory:
   ```bash
   cd Assignment_1
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   Or set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 🎯 Usage

### Basic Usage

1. **Run the main script:**
   ```bash
   python main.py
   ```

2. **Enter a topic when prompted:**
   - Type any technical topic (e.g., "Machine Learning", "Neural Networks", "SimCLR")
   - Press Enter to use the default topic "SimCLR"

3. **Watch the agents work:**
   - The research agent will analyze your topic
   - The mentor agent will rewrite it in simple terms
   - Output will be saved to `simclr_explained.md`

### Example Session

```bash
$ python main.py
🚀 Starting Luc's CrewAI Digital Twin
==================================================
Enter a topic you'd like Luc's agent to explain (default: SimCLR): Machine Learning

🎯 Executing crew...

[Agent logs will appear here...]

✅ Crew execution completed!
==================================================
```

### Output

The system generates a markdown file with:
- Clear definitions
- Key concepts explained simply
- How things work (step-by-step)
- Real-world examples
- Why it's important

## 🔧 Configuration

### Customizing Agents

You can modify the agents in `main.py`:

- **Research Agent**: Change the role, goal, or backstory
- **Mentor Agent**: Adjust the simplification approach
- **LLM Settings**: Specify different models or temperature settings

Example customization:
```python
def create_student_agent():
    return Agent(
        role="Harvard Data Science Student",
        goal="Summarize technical concepts clearly and accurately",
        backstory="""You are Luc, a Harvard Data Science student...""",
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o-mini",  # Specify model
        temperature=0.2     # Control randomness
    )
```

### Adding Tools

The mentor agent uses `FileWriterTool()` to save output. You can add more tools:

```python
from crewai_tools import WebSearchTool, SerperDevTool

tools = [FileWriterTool(), WebSearchTool(), SerperDevTool()]
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'crewai'"**
   - Make sure you're in the virtual environment
   - Run `pip install -r requirements.txt`

2. **API Key Error**
   - Verify your API key is set correctly in `.env` file
   - Check that you have sufficient API credits
   - Ensure the `.env` file is in the Assignment_1 directory

3. **File Not Created**
   - Ensure you have write permissions in the directory
   - Check that the FileWriterTool is properly configured
   - Verify the output filename in the task description

4. **Import Errors**
   - Make sure all dependencies are installed
   - Check that you're running from the correct directory

### Performance Tips

- Use `gpt-4o-mini` for faster, cheaper runs
- Set `temperature=0.2` for more consistent outputs
- Add specific output length requirements in task descriptions
- Use virtual environments to avoid dependency conflicts

## 📚 Dependencies

- `crewai`: Multi-agent orchestration framework
- `crewai-tools`: Additional tools for agents
- `python-dotenv`: Environment variable management
- `openai`: LLM API client (or your preferred provider)

## 🎓 How It Works

1. **Research Agent**: Acts as a Harvard Data Science student, researching and summarizing technical topics
2. **Mentor Agent**: Takes the research and rewrites it in beginner-friendly language
3. **Sequential Process**: Agents work one after another, with the mentor building on the research
4. **File Output**: The mentor agent saves the final explanation to a markdown file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the MIT AI Studio - CrewAI Tech Track.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your API keys and dependencies
3. Ensure you're running from the correct directory
4. Check the CrewAI documentation for advanced configuration

## 📝 Example Output

The system generates explanations like the included `simclr_explained.md`, which demonstrates how complex AI concepts are broken down into simple, understandable explanations with real-world examples and clear structure.

---

**Happy Learning with Luc's AI Agents! 🚀✨**
