# LocalCodeAgent (VibeCoded)

> A local-first AI coding assistant powered by Ollama, built to inspect projects, work with files, run development commands, remember conversations, and help build polished interfaces.

**Tested on macOS only.**

## What It Does

LocalCodeAgent connects a local Ollama model to a practical development toolkit:

- Inspects the current project and understands its structure
- Reads, creates, and safely edits workspace files
- Runs development commands with approval and safety checks
- Searches project files with `ripgrep`
- Searches the public web without a paid search API
- Preserves conversation context and exact tool-call content
- Tracks task objectives and project snapshots across restarts
- Supports Git inspection and approved Git operations
- Applies design guidance to UI-heavy projects

## How It Works

```text
Your request
	|
	v
LocalCodeAgent + persistent context
	|
	+--> Ollama model
	|
	+--> File, command, Git, project, and web tools
	|
	v
Validated result in your workspace
```

The agent runs locally. Your prompts, project context, and memory are stored in the project workspace unless a tool explicitly accesses the public web.

## Requirements

- macOS
- Python 3.10 or newer
- Ollama
- A downloaded Ollama model
- Git, for Git-related features

## Quick Start

### 1. Install Ollama

Download Ollama from:

<https://ollama.com/download>

Verify the installation:

```bash
ollama --version
```

### 2. Install the project

From the repository root:

```bash
bash requirements.txt
```

This creates `.venv` and installs the Python dependency used by the agent.

### 3. Choose and download a model

Explore the official catalog:

<https://ollama.com/library>

For the current default model:

```bash
ollama pull qwen3.5:9b
```

Then open [agent/config.py](agent/config.py) and set the exact model name:

```python
MODEL = "qwen3.5:9b"
```

If you choose a different model, pull it first and update `MODEL` to match its exact name and tag.

### 4. Start the agent

Ollama normally runs its local service automatically. If needed, start it in a separate terminal:

```bash
ollama serve
```

Then run the agent:

```bash
.venv/bin/python main.py
```

Type `exit` or `quit` to stop.

## Example Requests

```text
Inspect this project and explain how it works.
```

```text
Create a responsive personal finance dashboard. Research suitable color palettes and accessibility guidance before implementing it.
```

```text
Run the tests and fix the failing code.
```

```text
What was the exact code you gave me earlier in this thread?
```

## Design-Aware UI Work

For UI projects, the agent can research public design references and apply guidance around:

- Visual hierarchy and whitespace
- 4px or 8px spacing systems
- Typography scales
- Color palette selection by product type
- Contrast, focus states, and keyboard accessibility
- Balanced composition inspired by proportional systems such as the golden ratio

The agent treats these principles as guidance rather than rigid rules, keeping usability and the product's purpose first.

## Project Structure

```text
.
├── agent/
│   ├── agent.py                 # Agent orchestration and tool loop
│   ├── config.py                # Ollama model configuration
│   ├── memory.py                # Persistent conversation and task memory
│   ├── workspace.py              # Workspace path safety
│   └── tools/                    # File, command, Git, project, and web tools
├── main.py                       # Interactive CLI entry point
├── requirements.txt              # Command-only Python setup script
├── model_downloading.md          # Ollama model setup guide
└── test_*.py                     # Regression tests
```

## Memory

The agent stores local state in `.agent_memory.json`, including:

- Recent conversation context
- Exact thread transcripts and tool-call arguments
- Older conversation summaries
- Current task memory
- The latest project snapshot

This file is generated locally and should be treated as private workspace data.

## Testing

Run the test suite from the project root:

```bash
python -m unittest -q
```

The project is currently tested on macOS only.

## Ollama Connection

The Python Ollama client connects to the local service at:

```text
http://localhost:11434
```

No API key is required for local use. For the full setup and model-selection process, see [model_downloading.md](model_downloading.md).

## Safety Notes

- File creation and edits require approval.
- Potentially risky commands are filtered or require approval.
- Git state-changing operations require explicit user intent.
- Workspace paths are restricted to the project directory.
- The web search tool retrieves public search results directly.

## Status

This is an actively evolving local coding assistant. It is currently tested on macOS only; Windows and Linux support may require platform-specific setup adjustments.
