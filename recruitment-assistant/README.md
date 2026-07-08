# Recruitment Assistant

A CrewAI multi-agent recruitment assistant that automates candidate sourcing, evaluation, outreach strategy, and recruiter reporting.

## Overview

The Recruitment Assistant is an open-source, multi-agent system built on CrewAI that reduces time-to-fill by 50% while maintaining transparency and compliance. It uses four specialized agents working in sequence:

1. **Job Candidate Researcher** - Finds potential candidates via web search
2. **Candidate Matcher and Scorer** - Scores and ranks candidates against requirements
3. **Candidate Outreach Strategist** - Develops engagement strategies and templates
4. **Candidate Reporting Specialist** - Compiles recruiter-ready final reports

## Features

- **Multi-Agent Workflow**: Four specialized agents collaborating autonomously
- **YAML Configuration**: Easily customize agents and tasks via YAML files
- **CLI Interface**: Simple command-line interface for job description input
- **Report Generation**: Generates comprehensive markdown reports
- **Extensible**: Add custom tools and agents easily

## Prerequisites

- **Python**: 3.10 or higher (3.10, 3.11, 3.12, 3.13 supported)
- **uv**: Package manager (install from [astral.sh/uv](https://astral.sh/uv))
- **API Keys**:
  - LLM API key (for GLM-5.2 or other OpenAI-compatible models)
  - Serper.dev API key (for web search functionality)

## Quick Start (< 15 minutes)

### 1. Clone and Navigate

```bash
cd recruitment-assistant
```

### 2. Install Dependencies

```bash
# Install uv if not already installed
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install project dependencies
uv sync
```

### 3. Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=your_api_key_here
# SERPER_API_KEY=your_serper_api_key_here
```

### 4. Verify Installation

```bash
# Run the recruitment assistant
uv run recruitment

# Or run tests
uv run pytest
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | API key for LLM provider (OpenAI-compatible) |
| `SERPER_API_KEY` | Yes | - | Serper.dev API key |
| `LLM_MODEL` | No | `glm-5.2` | LLM model identifier |
| `LLM_BASE_URL` | No | `https://api.iamhc.cn` | Custom LLM endpoint (GLM, Ollama, LM Studio, etc.) |

*Required for any OpenAI-compatible provider

### Agent Configuration

Edit `src/recruitment/config/agents.yaml` to customize agent roles, goals, and backstories:

```yaml
researcher:
  role: "Job Candidate Researcher"
  goal: "Find potential candidates for the job"
  backstory: "You are adept at finding the right candidates..."
```

### Task Configuration

Edit `src/recruitment/config/tasks.yaml` to customize task descriptions and expected outputs:

```yaml
research_candidates_task:
  description: "Conduct thorough research to find potential candidates..."
  expected_output: "A list of 10 potential candidates..."
```

## Usage

### Basic Usage

```bash
# Run the recruitment assistant
uv run recruitment

# Follow the prompts to enter job description
```

### Example Workflow

1. Run the assistant
2. Enter job title
3. Enter job description (minimum 100 characters)
4. Enter key responsibilities (minimum 3)
5. Enter required qualifications (minimum 3)
6. Confirm and run workflow
7. View generated report

### Using Alternative LLMs

The system uses an OpenAI-compatible API by default. To use a different provider:

1. Set `LLM_BASE_URL` in your `.env` file:
   ```
   # For GLM-5.2 (default)
   LLM_BASE_URL=https://api.iamhc.cn
   
   # For Ollama (local)
   LLM_BASE_URL=http://localhost:11434/v1
   
   # For LM Studio (local)
   LLM_BASE_URL=http://localhost:1234/v1
   ```

2. Set the model name:
   ```
   # For GLM-5.2
   LLM_MODEL=glm-5.2

   # For Ollama
   LLM_MODEL=ollama/llama3
   ```

## Development

### Project Structure

```
recruitment-assistant/
├── src/recruitment/
│   ├── __init__.py
│   ├── main.py                 # Entry point and CLI
│   ├── crew.py                 # Crew assembly and orchestration
│   ├── config/
│   │   ├── agents.yaml         # Agent definitions
│   │   └── tasks.yaml          # Task definitions
│   └── tools/
│       ├── __init__.py
│       └── custom_tools.py     # Custom tool implementations
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_basic.py
```

### Code Quality

```bash
# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/

# Format code
uv run ruff format src/
```

## Troubleshooting

### Common Issues

**Missing API Keys**
```
Error: Missing required environment variables: OPENAI_API_KEY, SERPER_API_KEY
```
Solution: Copy `.env.example` to `.env` and add your API keys (the `OPENAI_API_KEY` variable accepts any OpenAI-compatible provider key).

**Import Errors**
```
ModuleNotFoundError: No module named 'recruitment'
```
Solution: Run `uv sync` to install dependencies.

**Version Compatibility**
```
Error: Python version not supported
```
Solution: Ensure you're using Python 3.10-3.13.

### Getting Help

1. Check this README
2. Review the [CrewAI documentation](https://docs.crewai.com)
3. Open an issue on GitHub

## Roadmap

- **v0.1.0**: MVP with CLI interface (current)
- **v0.2.0**: Web chat UI (Next.js + assistant-ui)
- **v0.3.0**: ATS integration (Greenhouse, Lever)
- **v0.4.0**: Multi-role hiring support
- **v0.5.0**: Analytics dashboard
- **v1.0.0**: Production-ready with auth, multi-tenancy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [CrewAI](https://github.com/crewAIInc/crewAI)
- Part of the [AAMAD Framework](https://github.com/aamad)
- Inspired by real-world recruitment challenges