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
        "expected_facts": ["LAN", "IP"],
        "expected_refusal": False,
    },
    {
        "question": "What is the CEO's email address?",
        "expected_facts": [],
        "expected_refusal": True,
    },
    {
        "question": "Can I request to remove the upload restriction on my local PC?",
        "expected_facts": ["IP address"],
        "expected_refusal": False,
    },
    {
        "question": "Where do I go to request removing a file upload restriction?",
        "expected_facts": ["Security Portal"],
        "expected_refusal": False,
    },
]