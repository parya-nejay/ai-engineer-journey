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
    },
    {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this when the user asks about weather, temperature, rain, snow, or whether to dress for cold or warm conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Toronto' or 'Vancouver'"
                }
            },
            "required": ["city"]
        }
    }
    ,
    {
        "name": "search_company_directory",
        "description": "Search the company employee directory by name. Returns the employee's email, title, and department. Use this when the user asks who someone is, what someone's role is, how to contact a coworker, or who works on what team.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The employee's full or partial name, e.g. 'Sarah' or 'Sarah Chen'"
                }
            },
            "required": ["name"]
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


def get_weather(city: str) -> str:
    """Fake weather lookup for demo purposes."""
    weather_data = {
        "toronto": "Cloudy, 8°C, 60% chance of rain",
        "vancouver": "Rainy, 12°C, windy",
        "montreal": "Sunny, 15°C",
    }
    return weather_data.get(
        city.lower(),
        f"No weather data available for {city}"
    )


def search_company_directory(name: str) -> str:
    """Fake company directory lookup for demo purposes."""
    
    directory = {
        "sarah chen": "Sarah Chen — Engineering Manager, sarah.chen@example.com, based in Vancouver",
        "david kim": "David Kim — Marketing Lead, david.kim@example.com, based in Toronto",
        "alex morgan": "Alex Morgan — Senior Software Engineer, alex.morgan@example.com, based in Montreal",
    }
    
    key = name.lower()
    if key in directory:
        return directory[key]
    # Partial match — e.g. Claude passes just "David"
    for full_name, info in directory.items():
        if key in full_name:
            return info
    return f"No employee found matching '{name}'"


# Dispatch table: tool name → Python function that runs it
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "search_company_directory": search_company_directory,
}


# print("Agent demo ready.")
# print(f"Tools available: {[t['name'] for t in TOOLS]}")
# print(f"Test: 2 + 2 = {calculator('2 + 2')}")


# # === The agent loop ===
# # new
def run_agent(user_message, tools, tool_functions):
    """Run the agent loop until Claude returns a final text answer."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",  # match the model you use in main.py
            max_tokens=1024,
            tools=tools,
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
                    tool_func = tool_functions[block.name]
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


# # === Test the agent ===
# print("\n" + "=" * 60)
# print("Test 1: math question (should use calculator)")
# print("=" * 60)
# answer = run_agent("What is 15 * 9 + 7?")
# print(f"\nFinal answer: {answer}")

# print("\n" + "=" * 60)
# print("Test 2: non-math question (should NOT use calculator)")
# print("=" * 60)
# answer = run_agent("What is the capital of France?")
# print(f"\nFinal answer: {answer}")

# print("="*60)
# print("Test 3: weather question (should use get_weather)")
# print("="*60)
# result = run_agent("What's the weather in Toronto?")
# print(f"Final answer: {result}")

# print("="*60)
# print("Test 4: directory question (should use search_company_directory)")
# print("="*60)
# result = run_agent("How do I contact David in marketing?")
# print(f"Final answer: {result}")

# print("="*60)
# print("Test 5: multi-tool question (should call TWO tools)")
# print("="*60)
# result = run_agent("What's the weather in Toronto and how do I contact David in marketing?")
# print(f"Final answer: {result}")
if __name__ == "__main__":
    print("Agent demo ready.")
    print(f"Tools available: {[t['name'] for t in TOOLS]}")
    print(f"Test: 2 + 2 = {calculator('2 + 2')}")

    print("\n" + "=" * 60)
    print("Test 1: math question (should use calculator)")
    print("=" * 60)
    answer = run_agent("What is 15 * 9 + 7?", TOOLS, TOOL_FUNCTIONS)
    print(f"\nFinal answer: {answer}")

    print("\n" + "=" * 60)
    print("Test 2: non-math question (should NOT use calculator)")
    print("=" * 60)
    answer = run_agent("What is the capital of France?", TOOLS, TOOL_FUNCTIONS)
    print(f"\nFinal answer: {answer}")

    print("=" * 60)
    print("Test 3: weather question (should use get_weather)")
    print("=" * 60)
    result = run_agent("What's the weather in Toronto?", TOOLS, TOOL_FUNCTIONS)
    print(f"Final answer: {result}")

    print("=" * 60)
    print("Test 4: directory question (should use search_company_directory)")
    print("=" * 60)
    result = run_agent("How do I contact David in marketing?", TOOLS, TOOL_FUNCTIONS)
    print(f"Final answer: {result}")
    
    print("=" * 60)
    print("Test 5: multi-tool question (should call TWO tools)")
    print("=" * 60)
    result = run_agent("What's the weather in Toronto and how do I contact David in marketing?", TOOLS, TOOL_FUNCTIONS)
    print(f"Final answer: {result}")

    print("=" * 60)
    print("Test 6: CHAINED tools (must call directory FIRST, then weather)")
    print("=" * 60)
    result = run_agent("What's the weather like in the city where David works?", TOOLS, TOOL_FUNCTIONS)
    print(f"Final answer: {result}")