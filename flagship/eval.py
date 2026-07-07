from eval_dataset import eval_cases
from query import answer
passed_count = 0
for case in eval_cases:
    question = case["question"]
    result = answer(question)
    refused = "I don't have that information" in result
    expected_refusal = case["expected_refusal"]

    if expected_refusal:
        passed = refused
        print(f"Q: {question}")
        print(f"expected refusal, got refusal? {refused} -> {'PASS' if passed else 'FAIL'}")
        if passed: passed_count += 1
        print("---")
    else:
        if refused:
            passed = False
            print(f"Q: {question}")
            print(f"should answer but refused -> FAIL")
            if passed: passed_count += 1
            print("---")
        else:
            expected_facts = case["expected_facts"]
            found = [f for f in expected_facts if f.lower() in result.lower()]
            passed = len(found) >= len(expected_facts) / 2
            print(f"Q: {question}")
            print(f"found {len(found)}/{len(expected_facts)} facts -> {'PASS' if passed else 'FAIL'}")
            if passed: passed_count += 1
            print("---")
            
print(f"\nSCORE: {passed_count}/{len(eval_cases)}")