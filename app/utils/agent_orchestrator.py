# utils/agent_orchestrator.py

from utils.planner_agent import plan_tools_for_query
from utils.searcher_agent import search_with_google
from utils.navigator_agent import navigate_and_capture
from utils.web_retriever import run_scraper
from utils.validator_agent import validate_schema_against_usecase, extract_metadata_type
from utils.response_generator import generate_final_answer
from utils.cache_manager import GlobalCache


def handle_query_with_agents(query, use_case, user_name="Customer"):
    """
    Full agent pipeline with tool chaining:
    Planner → Searcher → Navigator → Scraper → Validator → Cache
    """
    print("\n[Agent Pipeline] Starting agent chain for:", query)

    tools = plan_tools_for_query(query)
    print(f"[Planner] Toolchain decided: {tools}")

    search_results = None
    html_content = None
    scraped = None
    context = None
    top_link = None

    try:
        for tool in tools:
            if tool == "search":
                search_results = search_with_google(query)
                if not search_results:
                    return "⚠️ No relevant search results found."
                top_link = search_results[0]['link']
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
                return "🔗 Try our official page: [Link resolving not yet implemented in chain]"

            elif tool == "none":
                return "⚠️ No tools required. Try checking the RAG or cache pipeline."

        # Final generation if scraping & validation succeeded
        if scraped:
            final_response = generate_final_answer(query, scraped, user_name=user_name)
            source = extract_metadata_type(scraped)

            # Cache result
            GlobalCache.set(
                query=query,
                response=final_response,
                source=source,
                use_case=use_case,
                validated=True
            )
            return final_response

        return "⚠️ Something went wrong in the agent pipeline."

    except Exception as e:
        return f"❌ Agent chain crashed: {e}"
