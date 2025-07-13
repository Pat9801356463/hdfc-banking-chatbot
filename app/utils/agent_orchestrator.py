# utils/agent_orchestrator.py

from utils.planner_agent import plan_tools_for_query
from utils.searcher_agent import search_web
from utils.navigator_agent import navigate_and_capture
from utils.response_generator import generate_final_answer
from utils.validator_agent import validate_schema_against_usecase, extract_metadata_type
from utils.cache_manager import GlobalCache, is_public_query

# Optional import for scraper (may fail in some environments)
try:
    from utils.web_retriever import run_scraper
except ImportError:
    run_scraper = None


def classify_intent_and_usecase(query: str):
    """
    Temporary rule-based intent and use-case classifier.
    Replace with Cohere or Gemini if needed.
    """
    query = query.lower()
    if "repo" in query or "interest rate" in query or "rbi" in query:
        return "GetRates", "Banking Norms"
    if "headquarter" in query or "where is hdfc" in query:
        return "FindLocation", "Documentation & Process Query"
    if "credit card" in query:
        return "BrowseProduct", "Documentation & Process Query"
    if "loan" in query and "type" in query:
        return "BrowseProduct", "Loan Prepurchase Query"
    if "emi calculator" in query:
        return "ToolUse", "Loan Prepurchase Query"
    return "Generic", "Internal Account"


def orchestrate_agents(query, use_case=None, user_name="Customer"):
    """
    Full agent pipeline:
    Planner → Searcher → Navigator → Scraper → Validator → Cache + Response
    """
    print("\n[Agent Pipeline] Starting agent chain for:", query)

    # 1️⃣ Classify intent and use-case
    intent, predicted_use_case = classify_intent_and_usecase(query)
    use_case = use_case or predicted_use_case
    print(f"[Planner] Intent: {intent} | Use Case: {use_case}")

    # 2️⃣ Tool planning
    if is_public_query(intent, use_case):
        tools = plan_tools_for_query(query)
    else:
        tools = ["none"]
    print(f"[Planner] Toolchain decided: {tools}")

    search_results = None
    html_content = None
    scraped = None
    context = None
    top_link = None

    try:
        for tool in tools:
            if tool == "search":
                search_results = search_web(query)
                if not search_results or not search_results[0][1]:
                    return "⚠️ No relevant search results found."
                top_link = search_results[0][1]
                print(f"[Searcher] Top link: {top_link}")

            elif tool == "navigate":
                if not top_link:
                    return "⚠️ Cannot navigate: No link available."
                html_content = navigate_and_capture(top_link)
                if not html_content:
                    return "⚠️ Failed to capture page content."
                print("[Navigator] HTML captured.")

            elif tool == "scrape":
                if not html_content:
                    return "⚠️ No HTML to scrape."
                if not run_scraper:
                    return "❌ Scraper function not available in web_retriever."
                scraped = run_scraper(html_content)
                if not scraped:
                    return "⚠️ Scraping failed or returned empty data."
                print("[Scraper] Data extracted.")

            elif tool == "validate":
                if not scraped:
                    return "⚠️ Nothing to validate."
                if not validate_schema_against_usecase(use_case, scraped):
                    return "⚠️ Retrieved data didn't match expected format."
                print("[Validator] Schema validated ✅")

            elif tool == "link_resolver":
                return "🔗 Tool not implemented yet. Try using Gemini link resolver directly."

            elif tool == "none":
                print("ℹ️ Planner chose no tools — skipping agent pipeline.")
                return "NO_OP"

        # 3️⃣ Generate response from scraped data
        if scraped:
            final_response = generate_final_answer(query, scraped, user_name=user_name)
            source = extract_metadata_type(scraped)

            # 4️⃣ Cache it
            GlobalCache.set(
                query=query,
                response=final_response,
                source=source,
                use_case=use_case,
                validated=True
            )
            return final_response

        return "⚠️ Agent pipeline completed but no response could be generated."

    except Exception as e:
        return f"❌ Agent pipeline crashed: {e}"
