# Ollama Setup

LocalCodeAgent uses Ollama for local model inference. The Python package is installed through `requirements.txt`; Ollama itself must be installed as a system application.

## 1. Install Ollama

Install Ollama for macOS or Linux from:

```text
https://ollama.com/download
```

Install the desktop application for macOS, or follow the Linux installation instructions. Then verify the command is available:

```bash
ollama --version
```

## 2. Explore the model catalog

Browse the official model catalog here:

```text
https://ollama.com/library
```

Choose a model based on your needs and hardware:

- Coding and tool use: choose a strong coding or general-purpose model.
- Faster responses on a laptop: choose a smaller model such as a 3B-8B model.
- Better reasoning and larger projects: choose a larger model if your computer has enough RAM.
- Local storage: check the model size on its catalog page before downloading.
- Tool calling: confirm the model supports tool or function calling when that capability is listed.

The project currently uses `qwen3.5:9b`. You can keep it or choose another model from the catalog.

## 3. Install Python dependencies

From the project directory, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
bash requirements.txt
```

## 4. Pull the selected model

Use the model's exact name from its catalog page. For the current default:

```bash
ollama pull qwen3.5:9b
```

For another model, replace the name, for example:

```bash
ollama pull llama3.2
```

```python
MODEL = "llama3.2"
```

The model name in [agent/config.py](agent/config.py) must match the model you pulled.

After downloading the model, open [agent/config.py](agent/config.py) and write the exact same model name here:

```python
MODEL = "qwen3.5:9b"
```

For example, if you downloaded `llama3.2`, change it to:

```python
MODEL = "llama3.2"
```

The name must match exactly, including its tag if the catalog lists one, such as `:9b`.

Check downloaded models with:

```bash
ollama list
```

## 5. Start and connect to Ollama

Ollama normally runs its local service automatically after installation. If it is not running, start it in another terminal:

```bash
ollama serve
```

The default Ollama API address is:

```text
http://localhost:11434
```

The `ollama` Python client used by this project connects to that address automatically. No API key is required for local use.

Test the Ollama connection and selected model:

```bash
ollama run qwen3.5:9b "Reply with: Ollama connection is working."
```

If the service is unavailable, start it in another terminal:

```bash
ollama serve
```

## Run the project

With Ollama running and the virtual environment active:

```bash
.venv/bin/python main.py
```

Type a request at the `>` prompt. Type `exit` or `quit` to stop.

## Complete copy-paste setup

This installs the Python dependencies, starts Ollama if needed, downloads the configured model, and launches the agent:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
bash requirements.txt
ollama pull qwen3.5:9b
python main.py
```

If `ollama pull` or `ollama serve` is not found, install Ollama first using the official download page above, then rerun the commands.
