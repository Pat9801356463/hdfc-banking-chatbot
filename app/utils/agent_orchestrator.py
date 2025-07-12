# utils/agent_orchestrator.py

from utils.planner_agent import plan_next_action
from utils.searcher_agent import search_with_google
from utils.navigator_agent import navigate_and_capture
from utils.web_retriever import run_scraper
from utils.validator_agent import validate_schema_against_usecase, extract_metadata_type
from utils.response_generator import generate_final_answer
from utils.cache_manager import GlobalCache


def handle_query_with_agents(query, use_case, user_name="Customer"):
    """
    Full agent pipeline orchestration:
    Planner -> Searcher -> Navigator -> Scraper -> Validator -> Cache + Response
    """
    print("\n[Agent Pipeline] Starting pipeline for query:", query)

    # Step 1: Planner decides next best action (optional refinement)
    refined_query = plan_next_action(query, use_case)
    print("[Planner] Refined Query:", refined_query)

    # Step 2: Searcher queries Google or search engine
    search_results = search_with_google(refined_query)
    if not search_results:
        return "⚠️ No relevant search results found. Please rephrase your query."

    print("[Searcher] Found search results.")

    # Step 3: Navigator opens top search result and extracts HTML
    top_link = search_results[0]['link']
    html_content = navigate_and_capture(top_link)
    if not html_content:
        return "⚠️ Failed to open or capture content from the top result."

    print("[Navigator] Captured HTML from:", top_link)

    # Step 4: Scraper extracts data
    scraped = run_scraper(html_content)
    if not scraped:
        return "⚠️ Unable to extract meaningful data from the page."

    print("[Scraper] Extracted data from HTML.")

    # Step 5: Validator checks schema & use-case alignment
    if validate_schema_against_usecase(use_case, scraped):
        print("[Validator] Schema validated ✅")
        
        # Step 6: Generate final response
        final_response = generate_final_answer(query, scraped, user_name=user_name)

        # Step 7: Extract metadata tag (e.g., HDFC/RBI)
        source = extract_metadata_type(scraped)

        # Step 8: Cache it for future
        GlobalCache.set(
            query=query,
            response=final_response,
            source=source,
            use_case=use_case,
            validated=True
        )

        return final_response

    else:
        print("[Validator] ❌ Validation failed.")
        return "⚠️ Sorry, the retrieved data could not be validated for this use case. Please try rephrasing."
