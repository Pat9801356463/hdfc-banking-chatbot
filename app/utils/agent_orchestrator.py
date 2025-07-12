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
    """
    print(f"\n[Agent Pipeline] Starting agent chain for query: '{query}'")
    
   from utils.cache_manager import is_public_query
    if is_public_query(query):
        tools = plan_tools_for_query(query)
    else:
        tools = ["none"]  # Force RAG for internal/private banking queries

    print(f"[Planner] Toolchain: {tools}")

    # Special case: No tools required — use RAG directly
    if tools == ["none"]:
        print("[Planner] No tools required — using RAG.")
        rag_context = load_documents_for_use_case(use_case)
        if "⚠️" in rag_context or not rag_context.strip():
            return "⚠️ No relevant documents found for your query."
        return generate_final_answer(query, rag_context, user_name=user_name)

    # Prepare variables
    search_results = None
    html_content = None
    scraped = None
    context = None
    top_link = None
    schema_validated = False

    try:
        for tool in tools:
            if tool == "search":
                search_results = search_web(query)
                if not search_results or search_results[0][1] == "":
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
                schema_validated = validate_schema_against_usecase(use_case, scraped)
                if not schema_validated:
                    print("⚠️ Schema mismatch — falling back to RAG.")
                else:
                    print("[Validator] Schema validated ✅")

        # If scraping worked and schema is validated → generate final answer
        if scraped and schema_validated:
            final_response = generate_final_answer(query, scraped, user_name=user_name)
            source = extract_metadata_type(scraped)

            # Cache the result
            GlobalCache.set(
                query=query,
                response=final_response,
                source=source,
                use_case=use_case,
                validated=True
            )
            return final_response

        # If agent toolchain fails or schema not validated → fallback to RAG
        print("[Fallback] Falling back to RAG document context.")
        rag_context = load_documents_for_use_case(use_case)
        if "⚠️" in rag_context or not rag_context.strip():
            return "⚠️ No retrievable RAG content for this use case."
        return generate_final_answer(query, rag_context, user_name=user_name)

    except Exception as e:
        return f"❌ Agent pipeline crashed: {e}"
