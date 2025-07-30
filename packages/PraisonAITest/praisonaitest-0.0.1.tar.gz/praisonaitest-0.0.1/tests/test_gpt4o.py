"""
Simple example demonstrating the PraisonAITest package
"""
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from praisonaitest import Test

# Example with the exact API format requested
test1 = Test(model="openai/gpt-4o-mini", instruction="What is the capital of France?", validate="Paris")
result = test1.run()

# Print the results
print(f"Test result: {'Passed' if result['passed'] else 'Failed'}")
print(f"Response: {result['response']}")
print(f"Latency: {result['latency']:.2f} seconds")
print(f"Token usage: {result['token_usage']}")

# Example with a validation function instead of a string
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

print("\nFunction validator test:")
print(f"Test result: {'Passed' if result2['passed'] else 'Failed'}")
print(f"Response: {result2['response']}")
