"""Golden dataset: fixed cases with known-good expectations. Any prompt,
model, or agent-logic change is regression-tested against this set before
it can ship.
"""
GOLDEN_CASES = [
    {
        "case_id": "refund_policy_1",
        "query": "What is your refund policy?",
        "expected_tool": "kb_lookup",
        "reference_output": "Refunds are issued within 14 days of purchase, minus a 5% processing fee.",
    },
    {
        "case_id": "shipping_time_1",
        "query": "How long does shipping time take?",
        "expected_tool": "kb_lookup",
        "reference_output": "Standard shipping takes 3-5 business days within the continental US.",
    },
    {
        "case_id": "password_reset_1",
        "query": "I need help with a password reset",
        "expected_tool": "kb_lookup",
        "reference_output": "Users can reset their password from the account settings page via emailed link.",
    },
    {
        "case_id": "unknown_query_1",
        "query": "Can you tell me about your loyalty rewards program?",
        "expected_tool": "kb_lookup",
        "reference_output": "I don't have information on that; escalating to a human agent.",
    },
]
