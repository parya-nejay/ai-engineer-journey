import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()


# === Define the tools the agent has access to ===
TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Evaluates a basic math expression and returns the numeric result. "
            "Use when the user asks an arithmetic question (e.g., '2+2', '15 * 9 + 7'). "
            "Do NOT use for non-math questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression to evaluate, like '2 + 2' or '15 * 9 + 7'"
                }
            },
            "required": ["expression"]
        }
    }
]


# === The actual Python functions the tools call ===
def calculator(expression: str) -> str:
    """Evaluate a basic math expression and return the result as a string."""
    # SAFETY: whitelist allowed characters. In production, use a real expression parser.
    # NEVER pass raw user input to eval() without sandboxing.
    if not all(ch in "0123456789+-*/().% " for ch in expression):
        return "Error: expression contains unsupported characters"
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# Dispatch table: tool name → Python function that runs it
TOOL_FUNCTIONS = {
    "calculator": calculator,
}


print("Agent demo ready.")
print(f"Tools available: {[t['name'] for t in TOOLS]}")
print(f"Test: 2 + 2 = {calculator('2 + 2')}")


# === The agent loop ===
def run_agent(user_message: str) -> str:
    """Run the agent loop until Claude returns a final text answer."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",  # match the model you use in main.py
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        print(f"\n[Claude returned stop_reason: {response.stop_reason}]")

        # Case 1: Claude is done — return the final text answer
        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "(no text in response)"

        # Case 2: Claude wants to use a tool — execute it and loop
        if response.stop_reason == "tool_use":
            # Append Claude's response (the tool_use block) to the history
            messages.append({"role": "assistant", "content": response.content})

            # For each tool_use block, run the tool and collect the result
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Claude called: {block.name}({block.input})]")
                    tool_func = TOOL_FUNCTIONS[block.name]
                    result = tool_func(**block.input)
                    print(f"[Tool returned: {result}]")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Append the tool results as a user message — Claude reads this next turn
            messages.append({"role": "user", "content": tool_results})
            continue

        # Defensive: unknown stop_reason
        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")


# === Test the agent ===
print("\n" + "=" * 60)
print("Test 1: math question (should use calculator)")
print("=" * 60)
answer = run_agent("What is 15 * 9 + 7?")
print(f"\nFinal answer: {answer}")

print("\n" + "=" * 60)
print("Test 2: non-math question (should NOT use calculator)")
print("=" * 60)
answer = run_agent("What is the capital of France?")
print(f"\nFinal answer: {answer}")
