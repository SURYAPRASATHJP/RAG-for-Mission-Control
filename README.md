# Prerequisites

This code was written for python 3.14
Before running the script, ensure you have the following installed:

## Ollama
Download and install Ollama.

## Models
Pull the models used in the script:

```bash
ollama pull llama3.1:latest
ollama pull glm-4.7-flash:latest
ollama pull gemma4:latest
```

or pull your own and modify the `MODELS` list in the script accordingly

## Python Libraries

```bash
pip install -r requirements.txt
```

## Running the Script
Before running the script start the Ollama server

```bash
ollama serve
```