# VirtueRed

VirtueRed is a comprehensive package for the VirtueAI Redteaming system, providing both a CLI tool and a Model Server.

## Installation

```bash
pip install virtuered
```

## Components

### 1. Model Server

The Model Server allows you to serve your custom models for use with the VirtueRed system.

#### Usage

```python
from virtuered.client import ModelServer

# Start the model server
server = ModelServer(
    port=4299                   # Optional, defaults to 4299
)
server.start()
```

#### Local Model Setup

1. Create a models directory:
```
models/
├── model1.py
└── model2.py
```

2. Create a new Python file in the ```./models``` folder with a descriptive name for your model, e.g., ```model1.py```. Create a function called ```chat``` in ```model1.py```, the chat function will takes a list of chat messages and returns the response from the language model. For example, if we want to create a chat function with LLAMA-3-8b from huggingface:

```python
import os
from transformers import pipeline, LlamaTokenizer, LlamaForCausalLM

# Step 1: Load the LLaMA model and tokenizer
model_name = "meta-llama/Meta-Llama-3-8B"  # Replace with the actual model name on Hugging Face Hub
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Initialize the Hugging Face pipeline with the model and tokenizer
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Don't change the name of the function or the function signature
def chat(chats):
    """
    This function takes a list of chat messages and returns the response from the language model.
    
    Parameters:
    chats (list): A list of dictionaries. Each dictionary contains a "prompt" and optionally an "answer".
                  The last item in the list should have a "prompt" without an "answer".
    
    Returns:
    str: The response from the language model.
    
    Example of `chats` list with few-shot prompts:
    [
        {"prompt": "Hello, how are you?", "answer": "I'm an AI, so I don't have feelings, but thanks for asking!"},
        {"prompt": "What is the capital of France?", "answer": "The capital of France is Paris."},
        {"prompt": "Can you tell me a joke?"}
    ]
    
    Another example of `chats` list with one-shot prompt:
    [
        {"prompt": "What is the weather like today?"}
    ]
    """
    
    # Step 2: Prepare the chat history as a single string
    chat_history = []
    for c in chats:
        # Add the user prompt and assistant's answer to the chat history
        chat_history.append({"role": "user", "content": c["prompt"]})
        if "answer" in c.keys():
            chat_history.append({"role": "assistant", "content": c["answer"]})
        else:
            # If there is no answer, it means this is the prompt we need a response for
            break
    
    # Step 3: Generate the model's response
    response = chatbot(chat_history, max_length=1000, num_return_sequences=1)
    
    # Step 4: Extract and return the generated text
    generated_text = response[0]['generated_text']
    assistant_response = generated_text.split("Assistant:")[-1].strip()
    
    return assistant_response 
```



### 2. CLI Tool

The CLI tool provides a command-line interface for managing VirtueRed operations.

#### CLI Commands

```bash
# View all available commands
virtuered --help

# Configure a custom server address instead of the default http://localhost:4401(persistent)
virtuered config http://localhost:4403
virtuered show-config

# List all runs
virtuered list

# List all custom models
virtuered models

# Monitor ongoing scans
virtuered monitor

# Initialize a new scan
virtuered scan                # Uses default scan_config.json
virtuered scan myconfig.json  # Uses custom config file

# Get summary of a run
virtuered summary my_scan
virtuered summary 1

# Pause/Resume a scan
virtuered pause my_scan
virtuered resume 1

# Generate report
virtuered report my_scan

# Delete a run
virtuered delete 1

# For temporary custom server URL:
virtuered --server http://localhost:4403 list
```

#### Available Commands

- `--help`: View all available commands
- `config`: Set persistent default server URL
- `show-config`: View current configuration
- `list`: Show all runs
- `models`: Show all custom models
- `scan`: Initialize a new scan using configuration file
- `monitor`: Monitor ongoing scans
- `summary`: Get detailed summary of a run
- `report`: Generate PDF report
- `pause`: Pause a running scan
- `resume`: Resume a paused scan
- `delete`: Delete a run

#### Scan Configuration

Create a JSON configuration file (`scan_config.json` or custom name) before initiating a scan:

```json
{
    "name": "my_scan",
    "model": "together_template",
    "datasets": [
        {
            "name": "EU Artificial Intelligence Act",
            "subcategories": [
                "Criminal justice/Predictive policing",
                "Persons (including murder)"
            ]
        },
        {
            "name": "White House AI Executive Order"
        }
    ],
    "extra_args": {
        "modelname": "model name",
        "apikey": "your-api-key"
    }
}
```

**Configuration Fields:**
- Required:
  - `name`: Unique scan identifier (alphanumeric and underscores only)
  - `model`: Model specification (local or cloud-hosted template)
  - `datasets`: Array of at least one dataset object with `name` field
- Optional:
  - `subcategories`: Array of specific subcategories to evaluate within each dataset
  - `extra_args`: Additional parameters for cloud-based models (credentials, settings)







## Architecture

The package consists of two main components:
1. **Model Server**: Serves your custom models, making them accessible to the VirtueRed system
2. **CLI Tool**: Provides command-line interface for managing VirtueRed operations

The typical setup involves:
1. Running the Model Server to serve your custom models
2. Running the VirtueRed Docker container, configured to connect to your Model Server
3. Using the CLI tool to manage and monitor operations

## Notes

- The Model Server must be running and accessible to the Docker container
- For local setup, use `http://127.0.0.1:4299` as client address
- For remote setup, use `http://<server-ip>:4299` as client address
- Ensure your models directory is properly structured with required model files

## Support

If you need further assistance, please contact our support team at contact@virtueai.com