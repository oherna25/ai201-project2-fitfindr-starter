"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────
""""
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
  
    # Replace this with your implementation
    return []
  """

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform
    """
    print("search_listings")
    listings = load_listings()

    # Step 1: Filter by max_price and size
    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.lower() not in listing["size"].lower():
            continue
        filtered.append(listing)

    # Step 2: Score by keyword overlap with description
    keywords = set(description.lower().split())

    def score(listing):
        searchable = " ".join([
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("category") or "",
            listing.get("brand") or "",
            " ".join(listing.get("style_tags") or []),
            " ".join(listing.get("colors") or []),
        ]).lower()
        return sum(1 for kw in keywords if kw in searchable)

    scored = [(score(listing), listing) for listing in filtered]

    # Step 3: Drop zero-score listings, sort best first
    results = [listing for s, listing in sorted(scored, key=lambda x: x[0], reverse=True) if s > 0]

    return results


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────
"""
def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
  
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    
    # Replace this with your implementation
    return 
"""
def suggest_outfit(
    new_item: dict,
    wardrobe: dict,
) -> str:
    """
    Suggest wardrobe items that pair well with new_item.
    """
    print("suggest_outfit")
    # Ensure wardrobe has an items list
    if "items" not in wardrobe or wardrobe["items"] is None:
        wardrobe["items"] = []

    # Filter out the new item from wardrobe candidates
    wardrobe_others = [
        i for i in wardrobe["items"]
        if i.get("id") != new_item.get("id")
        and i.get("name") != new_item.get("title")
        and i.get("name") != new_item.get("name")
    ]

    # Empty wardrobe or only contains the new item
    if len(wardrobe_others) == 0:
        if new_item not in wardrobe["items"]:
            wardrobe["items"].append(new_item)
        return {
            "new_item": new_item,
            "pairings": [],
            "wardrobe": wardrobe,
            "message": (
                "Your wardrobe doesn't have enough items to suggest an outfit yet. "
                "Keep adding more pieces so I can put together a complete look!"
            ),
        }

    # Score only other wardrobe items
    new_tags = set(t.lower() for t in new_item.get("style_tags", []))
    new_colors = set(c.lower() for c in new_item.get("colors", []))
    new_category = new_item.get("category", "").lower()

    def pairing_score(item):
        item_tags = set(t.lower() for t in item.get("style_tags", []))
        item_colors = set(c.lower() for c in item.get("colors", []))
        item_category = item.get("category", "").lower()
        tag_overlap = len(new_tags & item_tags)
        color_overlap = len(new_colors & item_colors)
        category_penalty = -2 if item_category == new_category else 0
        return tag_overlap + color_overlap + category_penalty

    scored = sorted(wardrobe_others, key=pairing_score, reverse=True)
    pairings = [item for item in scored if pairing_score(item) > 0]

    if pairings:
        message = (
            f"Here are some pieces from your wardrobe that would go well with "
            f"'{new_item.get('title') or new_item.get('name')}'!"
        )
    else:
        message = (
            f"Nothing in your wardrobe is a strong match for "
            f"'{new_item.get('title') or new_item.get('name')}' yet. "
            "Try adding more items to get better outfit suggestions!"
        )
    ##print("pairings[0]:", pairings[0])  
    return {
        "new_item": new_item,
        "pairings": pairings,
        "wardrobe": wardrobe,
        "message": message,
    }

# ── Tool 3: create_fit_card ───────────────────────────────────────────────────
"""
def create_fit_card(outfit: str, new_item: dict) -> str:
    
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.

    # Replace this with your implementation
    return ""
"""

def create_fit_card(outfit: dict, new_item: dict) -> str:
    print("create_fit_card")
    try:
        # Guard: check for incomplete data
        if not outfit or not isinstance(outfit, dict):
            return (
                "I don't have enough outfit info yet. "
                "Keep chatting and adding items so I can put together a full look!"
            )

        client = _get_groq_client()
        pairings = outfit.get("pairings", [])

        if not new_item or not new_item.get("title"):
            return (
                "I don't have enough info to build a fit card yet. "
                "Keep chatting and add more items so I can put together a full look!"
            )

        # Build a readable summary of the outfit pairings
        if pairings:
            pairing_lines = "\n".join(
                f"- {item['title']} ({item.get('category', 'item')})"
                for item in pairings
                if isinstance(item, dict) and item.get("title")
            )
            outfit_summary = f"Paired with:\n{pairing_lines}" if pairing_lines else "No wardrobe pairings yet — this is a standalone piece."
        else:
            outfit_summary = "No wardrobe pairings yet — this is a standalone piece."

        # Build the prompt
        item_title = new_item.get("title", "this piece")
        item_price = new_item.get("price", "?")
        item_platform = new_item.get("platform", "a thrift platform")
        item_style_tags = ", ".join(new_item.get("style_tags") or [])
        item_colors = ", ".join(new_item.get("colors") or [])

        prompt = f"""You are writing a casual, authentic OOTD (outfit of the day) caption for Instagram or TikTok. 
It should sound like a real person excited about a thrift find — not a product listing.

The thrifted item:
- Name: {item_title}
- Price: ${item_price}
- Found on: {item_platform}
- Style vibes: {item_style_tags}
- Colors: {item_colors}

Outfit:
{outfit_summary}

Write a 2–4 sentence caption that:
- Feels casual and specific, not generic
- Mentions the item name, price, and platform naturally (once each)
- Captures the overall outfit vibe
- Sounds fresh and different each time

Caption:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )

        caption = response.choices[0].message.content.strip()

        if not caption:
            return (
                "I wasn't able to generate a caption right now. "
                "Keep chatting and adding items — I'll put together your fit card once we have more to work with!"
            )

        return caption

    except Exception as e:
        return (
            f"Something went wrong building your fit card: {e}. "
            "Try searching for another item!"
        )