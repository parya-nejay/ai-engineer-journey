"""
Eval dataset for the Maple AI RAG system.

Each entry has:
- question: the user's question
- expected_facts: list of facts the correct answer MUST contain
- expected_refusal: True if the system should refuse (info not in docs)
- difficulty: easy / medium / hard (for analysis)
"""

EVAL_DATASET = [
    # ---- Easy: single direct fact ----
    {
        "id": "Q1",
        "question": "How much does the Professional tier cost per month?",
        "expected_facts": ["299", "Canadian dollars"],
        "expected_refusal": False,
        "difficulty": "easy",
    },
    {
        "id": "Q2",
        "question": "Who is the CEO of Maple AI?",
        "expected_facts": ["Sarah Chen"],
        "expected_refusal": False,
        "difficulty": "easy",
    },

    # ---- Medium: multiple facts or requires synthesis ----
    {
        "id": "Q3",
        "question": "What are the three office locations?",
        "expected_facts": ["Toronto", "Montreal", "Vancouver"],
        "expected_refusal": False,
        "difficulty": "medium",
    },
    {
        "id": "Q4",
        "question": "What are the support hours for non-Enterprise customers?",
        "expected_facts": ["Monday", "Friday", "8 AM", "8 PM", "Eastern"],
        "expected_refusal": False,
        "difficulty": "medium",
    },

    # ---- Hard: specific detail that might be missed by retrieval ----
    {
        "id": "Q5",
        "question": "What is the street address of the Toronto headquarters?",
        "expected_facts": ["220 King Street West", "14th floor"],
        "expected_refusal": False,
        "difficulty": "hard",
    },
    {
        "id": "Q6",
        "question": "How long does it take to process a refund?",
        "expected_facts": ["5 to 7 business days"],
        "expected_refusal": False,
        "difficulty": "medium",
    },

    # ---- Refusal test: info NOT in docs ----
    {
        "id": "Q7",
        "question": "What is Maple AI's stock price?",
        "expected_facts": [],
        "expected_refusal": True,
        "difficulty": "easy",
    },
]
