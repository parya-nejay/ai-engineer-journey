from anthropic import Anthropic # from anthropic import Anthropic
from dotenv import load_dotenv  # from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv() # load_dotenv()

# Create the client (auto-reads ANTHROPIC_API_KEY from environment)
client = Anthropic() # client = Anthropic()

# Make a request to Claude
response = client.messages.create(  # response = client.messages.create(
    model="claude-haiku-4-5-20251001",  #     model="Claude-haiku-4-5-20251001",
    max_tokens=1024,
    system="You are a sarcastic developer who makes jokes about programming languages."
    messages=[                           
        {"role": "user", "content": "Hello, Claude! Tell me one interesting fact about Python programming language in two sentences."}
    ] 
)

# Extract and print the response
print("=== Claude's response ===")
print(response.content[0].text)

# Show token usage (so we can track costs)
print("\n=== Token usage ===")
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
