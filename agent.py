"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────
"""
def run_agent(query: str, wardrobe: dict) -> dict:
  
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    TODO — implement this function using the planning loop you designed in planning.md:

        Step 1: Initialize the session with _new_session().

        Step 2: Parse the user's query to extract a description, size, and
                max_price. You can use regex, string splitting, or ask the LLM
                to parse it — document your choice in planning.md.
                Store the result in session["parsed"].

        Step 3: Call search_listings() with the parsed parameters.
                Store results in session["search_results"].
                If no results: set session["error"] to a helpful message and
                return the session early. Do NOT proceed to suggest_outfit
                with empty input.

        Step 4: Select the item to use (e.g., the top result).
                Store it in session["selected_item"].

        Step 5: Call suggest_outfit() with the selected item and wardrobe.
                Store the result in session["outfit_suggestion"].

        Step 6: Call create_fit_card() with the outfit suggestion and selected item.
                Store the result in session["fit_card"].

        Step 7: Return the session.

    Before writing code, complete the Planning Loop and State Management sections
    of planning.md — your implementation should match what you described there.

    # TODO: implement the planning loop
    session = _new_session(query, wardrobe)
    session["error"] = "Planning loop not yet implemented."
    return session
"""
def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.
    """
    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse the query using the LLM
    parse_prompt = f"""Extract search parameters from this clothing query.
Respond ONLY with valid JSON, no extra text.

Query: "{query}"

Return this exact format:
{{
  "description": "keywords describing the item",
  "size": "size string or null",
  "max_price": number or null
}}

Examples:
- "vintage graphic tee under $30 size M" → {{"description": "vintage graphic tee", "size": "M", "max_price": 30.0}}
- "black denim jacket" → {{"description": "black denim jacket", "size": null, "max_price": null}}
"""

    try:
        parse_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": parse_prompt}],
            temperature=0.0,
        )
        raw = parse_response.choices[0].message.content.strip()
        parsed = json.loads(raw)
    except Exception:
        parsed = {"description": query, "size": None, "max_price": None}

    session["parsed"] = parsed

    # Step 3: Search listings
    results = search_listings(
        description=parsed.get("description", query),
        size=parsed.get("size"),
        max_price=parsed.get("max_price"),
    )
    session["search_results"] = results

    if not results:
        session["error"] = (
            "No listings matched your search. Try describing a different item "
            "or loosening your size or price filters!"
        )
        return session

    # Step 4: Select top result
    selected_item = results[0]
    session["selected_item"] = selected_item

    # Step 5: Check wardrobe completeness, init if needed
    if "items" not in wardrobe or wardrobe["items"] is None:
        wardrobe["items"] = []

    has_tops = any(i.get("category", "").lower() == "tops" for i in wardrobe["items"])
    has_bottoms = any(i.get("category", "").lower() == "bottoms" for i in wardrobe["items"])

    if not has_tops or not has_bottoms:
        # Wardrobe is empty or incomplete — add selected item and use what we have
        if selected_item not in wardrobe["items"]:
            wardrobe["items"].append(selected_item)

    # Step 6: suggest_outfit
    outfit_suggestion = suggest_outfit(
        new_item=selected_item,
        wardrobe=wardrobe,
    )
    session["outfit_suggestion"] = outfit_suggestion

    # Step 7: create_fit_card
    if not outfit_suggestion or not selected_item:
        session["error"] = (
            "Something went wrong building your outfit. "
            "Try adding more items to your wardrobe and searching again!"
        )
        return session

    fit_card = create_fit_card(
        outfit=outfit_suggestion,
        new_item=selected_item,
    )
    session["fit_card"] = fit_card

    return session
# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
