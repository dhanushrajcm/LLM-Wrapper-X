from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
import os

# Ensure the API key is set, either via environment variable or direct initialization
# os.environ["GROQ_API_KEY"] = "your_api_key_here"  # Uncomment and set if using an environment variable

# Initialize Groq client
GROQ_API_KEY = "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"  # Set your API key here
client = Groq(api_key=GROQ_API_KEY)

# Retry decorator from tenacity
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=1.0, max_tokens=1024):
    """
    Function to interact with Groq API using the Mixtral-8x7b-32768 model for chat completions.
    This function streams the response from the API and includes retry logic.
    """
    try:
        # Create the chat completion request using the Groq client
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Use the Mixtral-8x7b-32768 model
            messages=[{"role": "user", "content": prompt}],  # Send the user's prompt
            temperature=temperature,  # Set the temperature for randomness
            max_completion_tokens=max_tokens,  # Max number of tokens in the response
            top_p=1,  # Set top_p for nucleus sampling
            stream=True,  # Stream the response
            stop=None,  # No specific stop sequence
        )

        # Collect the streamed response chunks and print them
        response_content = ""
        for chunk in completion:
            # Extract and print the content from each chunk
            response_content += chunk.choices[0].delta.content or ""
            print(chunk.choices[0].delta.content or "", end="")  # Print incrementally

        # Optionally, return the entire response content after streaming
        return response_content

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error during API call: {e}")
        raise  # Re-raise the exception to trigger retry mechanism

# Example usage
if __name__ == "__main__":
    prompt = "What are the latest trends in AI research?"
    temperature = 1.0  # Adjust for more randomness or creativity
    max_tokens = 1024  # Adjust the maximum response length

    try:
        # Get the response from the Groq API
        response = LLM_QnA_agent(prompt, temperature, max_tokens)

        # Optionally, print the final response after streaming
        print("\n\nFull Response:")
        print(response)
    except RetryError as e:
        print(f"Failed after multiple attempts: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")