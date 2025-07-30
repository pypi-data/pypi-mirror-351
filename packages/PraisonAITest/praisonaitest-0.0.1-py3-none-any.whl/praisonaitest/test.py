"""
Core test module for PraisonAITest
"""
import time
from typing import Union, Callable, Dict, Any
from dotenv import load_dotenv

# Import litellm for multi-provider support
try:
    from litellm import completion
except ImportError:
    raise ImportError("litellm is required. Install it with 'pip install litellm'")

# Load environment variables for API keys
load_dotenv()

class Test:
    """
    Simple LLM test class that supports testing with string matches or custom validation functions.
    
    Example:
        from PraisonAITest import Test
        
        # Test with string validation
        test1 = Test(model="openai/gpt-4o-mini", instruction="What is the capital of France?", validate="Paris")
        result = test1.run()
        print(result)
        
        # Test with function validation
        def validator(response):
            return "Paris" in response and "France" in response
            
        test2 = Test(model="openai/gpt-4o-mini", instruction="What is the capital of France?", validate=validator)
        result = test2.run()
        print(result)
    """
    
    def __init__(
        self, 
        model: str,
        instruction: str,
        validate: Union[str, Callable[[str], bool]],
        max_tokens: int = 100,
        temperature: float = 0.7,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize a test for an LLM.
        
        Args:
            model: Model identifier (provider/model format, e.g., "openai/gpt-4o-mini")
            instruction: The prompt or instruction to send to the LLM
            validate: Either a string that should be in the response, or a function that takes 
                     the response text and returns True/False for validation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout: Maximum time in seconds to wait for a response
            **kwargs: Additional parameters to pass to the LLM
        """
        self.model = model
        self.instruction = instruction
        self.validate = validate
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.kwargs = kwargs
        
    def run(self) -> Dict[str, Any]:
        """
        Run the test and return the results.
        
        Returns:
            Dictionary containing test results with the following keys:
            - success: Whether the API call was successful
            - passed: Whether the response validation passed
            - response: The LLM's response text
            - latency: Time taken for the response
            - error: Any error message (if applicable)
        """
        start_time = time.time()
        
        try:
            # Prepare the model format that litellm expects
            model = self.model
            
            # Create the message format
            messages = [{"role": "user", "content": self.instruction}]
            
            # Call the LLM
            response = completion(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **self.kwargs
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Validate the response
            if callable(self.validate):
                # If validate is a function, call it with the response text
                passed = self.validate(response_text)
            else:
                # If validate is a string, check if it's in the response
                passed = self.validate in response_text
            
            return {
                "success": True,
                "passed": passed,
                "response": response_text,
                "latency": time.time() - start_time,
                "model": self.model,
                "token_usage": response.usage if hasattr(response, 'usage') else None,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "passed": False,
                "response": None,
                "latency": time.time() - start_time,
                "model": self.model,
                "error": str(e)
            }
            
    def __str__(self) -> str:
        """String representation of the test."""
        return f"Test(model='{self.model}', instruction='{self.instruction[:30]}...')"
