from utils.planner_agent import plan_tools_for_query
from utils.searcher_agent import search_web
from utils.navigator_agent import navigate_and_capture
from utils.web_retriever import run_scraper
from utils.validator_agent import validate_schema_against_usecase, extract_metadata_type
from utils.response_generator import generate_final_answer
from utils.cache_manager import GlobalCache
from utils.rag_engine import load_documents_for_use_case


def orchestrate_agents(query, use_case, user_name="Customer"):
    """
    Full agent pipeline:
    Planner → Searcher → Navigator → Scraper → Validator → Cache + Response
    Falls back to RAG only if toolchain is 'none'
    """
    print("\n[Agent Pipeline] Starting agent chain for:", query)

    tools = plan_tools_for_query(query)
    print(f"[Planner] Toolchain decided: {tools}")

    search_results = None
    html_content = None
    scraped = None
    top_link = None

    try:
        # Use full agent pipeline only if tools include real web tasks
        if any(tool in tools for tool in ["search", "navigate", "scrape", "validate"]):
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

            if scraped:
                final_response = generate_final_answer(query, scraped, user_name=user_name)
                source = extract_metadata_type(scraped)
                GlobalCache.set(query, final_response, source, use_case, validated=True)
                return final_response

            return "⚠️ No relevant information extracted. Try rephrasing your query."

        # If planner returns only "none" → fallback to RAG
        elif tools == ["none"]:
            print("[Fallback] Using RAG documents for this query.")
            rag_context = load_documents_for_use_case(use_case)
            if "⚠️" in rag_context or not rag_context.strip():
                return "⚠️ No relevant RAG documents found for this use case."

            final_response = generate_final_answer(query, rag_context, user_name=user_name)
            GlobalCache.set(query, final_response, "Docs", use_case, validated=False)
            return final_response

        # Toolchain is malformed or incomplete
        else:
            return "⚠️ No valid tools selected and no fallback triggered."

    except Exception as e:
        return f"❌ Agent pipeline crashed: {e}"
