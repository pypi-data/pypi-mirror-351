# PraisonAITest

A minimal and simple testing framework for Large Language Models (LLMs) using LiteLLM.

## Installation

```bash
pip install PraisonAITest
```

For development installation:

```bash
pip install -e ./
```

## Usage

```python
from praisonaitest import Test

# Example with string validation
test1 = Test(model="openai/gpt-4o-mini", instruction="What is the capital of France?", validate="Paris")
result = test1.run()

print(f"Test result: {'Passed' if result['passed'] else 'Failed'}")
print(f"Response: {result['response']}")
print(f"Latency: {result['latency']:.2f} seconds")
print(f"Token usage: {result['token_usage']}")

# Example with a validation function
def validate_france_response(response):
    """Custom validator that checks if response mentions Paris and France"""
    return "Paris" in response and "France" in response

# Create a test with function validation
test2 = Test(
    model="openai/gpt-4o-mini", 
    instruction="Tell me about the capital of France", 
    validate=validate_france_response
)
result2 = test2.run()
```

## Environment Variables

Create a `.env` file with your API keys:

```
# LiteLLM API Key (Required)
LITELLM_API_KEY=your_api_key_here

# Default OpenAI API Key (Optional, if using OpenAI models directly)
OPENAI_API_KEY=your_openai_api_key_here
```

## License

This project is licensed under the MIT License.
