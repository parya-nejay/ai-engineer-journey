from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

print("=== Asking Claude (streaming) ===\n")
with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {
            "role": "user", "content": "Tell me a 3-paragraph story about a Python developer who discovers AI engineering."}

    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n\n=== Done ===")
