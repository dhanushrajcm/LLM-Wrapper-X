from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
import time

# Replace this with your actual Groq API key
GROQ_API_KEY = "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"

# Initialize Groq client with the API key
client = Groq(api_key=GROQ_API_KEY)

# Retry decorator
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=1.0, max_tokens=1024):
    try:
        # Send a request to Groq API using the llama-3.1-8b-instant model
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}],  
            temperature=temperature,  
            max_completion_tokens=max_tokens,  
            top_p=1,  
            stream=True,  
            stop=None,  
        )

        response_content = ""
        # Process the streamed response from the model
        for chunk in completion:
            # Append the chunk content to the response
            response_content += chunk.choices[0].delta.content or ""
            # Print each chunk as it arrives (you can remove this if not needed)
            print(chunk.choices[0].delta.content or "", end="")

        return response_content
    except Exception as e:
        print(f"Error during API call: {e}")
        raise

# Example usage
if __name__ == "__main__":
    prompt = "What can you tell me about the latest advancements in AI?"
    try:
        response = LLM_QnA_agent(prompt)
        print("\n\nFull Response:")
        print(response)
    except RetryError as e:
        print(f"Failed after multiple attempts: {e}")