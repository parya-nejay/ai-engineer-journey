eval_cases = [
    {
        "question": "How often does my password expire?",
        "expected_facts": ["three months"],
        "expected_refusal": False,
    },
    {
        "question": "If I change my cloud PC password, does my VPN password change too?",
        "expected_facts": ["same password"],
        "expected_refusal": False,
    },
    {
        "question": "How do I change my password?",
        "expected_facts": ["Ctrl+Alt+Delete", "Change a password", "LAN"],
        "expected_refusal": False,
    },
    {
        "question": "How do I check when my VPN expires?",
        "expected_facts": ["its.example.com", "VPN Request", "expiration date"],
        "expected_refusal": False,
    },
    {
        "question": "Do we have guest WiFi?",
        "expected_facts": [],
        "expected_refusal": True,
    },
    {
        "question": "How do I set up a new printer?",
        "expected_facts": [],
        "expected_refusal": True,
    },
    {
        "question": "What is the CEO's email address?",
        "expected_facts": [],
        "expected_refusal": True,
    },
]