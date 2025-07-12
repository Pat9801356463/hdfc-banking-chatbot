# utils/planner_agent.py

import os
import cohere
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Few-shot examples for classification
EXAMPLES = [
    {"query": "What is the latest RBI repo rate?", "tools": ["search", "scrape", "validate"]},
    {"query": "How to block my HDFC credit card?", "tools": ["link_resolver"]},
    {"query": "Download Form 16B", "tools": ["search", "scrape", "validate"]},
    {"query": "List some HDFC credit cards", "tools": ["search", "scrape", "validate"]},
    {"query": "Update address in HDFC account", "tools": ["search", "scrape", "validate"]},
    {"query": "Show me FD rates", "tools": ["search", "scrape"]},
    {"query": "Open an NPS account", "tools": ["search", "scrape"]},
    {"query": "Apply for personal loan EMI calculator", "tools": ["search", "scrape"]},
    {"query": "Mutual fund tax benefits for salaried", "tools": ["none"]},
    {"query": "KYC norms for NRIs", "tools": ["search", "scrape", "validate"]},
    {"query": "Where is HDFC headquarters", "tools": ["search", "scrape"]},
    {"query": "What are the features of HDFC website?", "tools": ["search", "navigate", "scrape"]},
]


def plan_tools_for_query(query: str) -> list:
    """
    Uses Cohere's Command-R+ model to classify query into a toolchain.
    """
    try:
        examples = [
            {
                "input": {"query": ex["query"]},
                "output": {"tools": ex["tools"]},
            }
            for ex in EXAMPLES
        ]

        response = co.rerank(  # Actually using Command-R+ with structured output
            model="command-r-plus",
            prompt_truncation="AUTO",
            task_type="classification",
            inputs=[{"query": query}],
            examples=examples,
            output_schema={"tools": list},
            return_prompt=False
        )

        tools = response["results"][0]["output"]["tools"]
        if isinstance(tools, list):
            print(f"[Planner] Tools chosen: {tools}")
            return tools
    except Exception as e:
        print(f"[Planner Error - Cohere] {e}")

    return ["none"]


def plan_next_action(query, intent=None, use_case=None):
    tools = plan_tools_for_query(query)
    return tools[0] if tools else "none"
