"""
tests/test_tools.py
pytest tests for search_listings, suggest_outfit, and create_fit_card.
No LLM calls — create_fit_card is tested by inspecting inputs/outputs only.
Assumes listings are already loaded via load_listings().
"""

import pytest
from tools import search_listings, suggest_outfit, create_fit_card


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_item():
    return {
        "id": "test-001",
        "title": "Vintage Graphic Tee",
        "description": "A cool retro graphic tee with faded print.",
        "category": "tops",
        "style_tags": ["vintage", "streetwear", "casual"],
        "size": "M",
        "condition": "Good",
        "price": 18.0,
        "colors": ["white", "black"],
        "brand": "Hanes",
        "platform": "Depop",
    }


@pytest.fixture
def another_item():
    return {
        "id": "test-002",
        "title": "Black Slim Jeans",
        "description": "Classic slim-fit black denim.",
        "category": "bottoms",
        "style_tags": ["casual", "streetwear"],
        "size": "30",
        "condition": "Like New",
        "price": 25.0,
        "colors": ["black"],
        "brand": "Levi's",
        "platform": "ThredUp",
    }


@pytest.fixture
def wardrobe_with_items(sample_item, another_item):
    return {"items": [sample_item, another_item]}


@pytest.fixture
def empty_wardrobe():
    return {"items": []}


@pytest.fixture
def null_wardrobe():
    return {}


# ---------------------------------------------------------------------------
# search_listings
# ---------------------------------------------------------------------------

class TestSearchListings:

    def test_returns_results_for_valid_query(self):
        results = search_listings("vintage graphic tee", size=None, max_price=50)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_returns_empty_list_no_match(self):
        """Failure mode: no listings match — must return [] not raise."""
        results = search_listings("designer ballgown", size="XXS", max_price=1)
        assert results == []

    def test_price_filter_respected(self):
        """All returned items must be at or below max_price."""
        results = search_listings("jacket", size=None, max_price=20)
        assert all(item["price"] <= 20 for item in results)

    def test_size_filter_case_insensitive(self):
        """Size matching should be case-insensitive and support partial match (e.g. S/M)."""
        results = search_listings("top", size="m", max_price=None)
        for item in results:
            assert "m" in item["size"].lower()

    def test_best_match_is_first(self):
        """The most relevant result should come first."""
        results = search_listings("vintage denim jacket", size=None, max_price=None)
        if len(results) >= 2:
            def keyword_hits(item, keywords):
                text = " ".join([
                    item.get("title", ""),
                    item.get("description", ""),
                    " ".join(item.get("style_tags") or []),
                ]).lower()
                return sum(1 for kw in keywords if kw in text)
            keywords = {"vintage", "denim", "jacket"}
            assert keyword_hits(results[0], keywords) >= keyword_hits(results[-1], keywords)

    def test_none_brand_does_not_crash(self):
        """Listings with brand=None must not raise TypeError."""
        results = search_listings("tee", size=None, max_price=None)
        assert isinstance(results, list)

    def test_combined_size_and_price_filter(self):
        results = search_listings("top", size="S", max_price=30)
        for item in results:
            assert item["price"] <= 30
            assert "s" in item["size"].lower()


# ---------------------------------------------------------------------------
# suggest_outfit
# ---------------------------------------------------------------------------

class TestSuggestOutfit:

    def test_empty_wardrobe_adds_item_and_prompts(self, sample_item, empty_wardrobe):
        """Failure mode: empty wardrobe — item is added and user is prompted."""
        result = suggest_outfit(sample_item, empty_wardrobe)
        assert result["pairings"] == []
        assert sample_item in result["wardrobe"]["items"]
        assert any(word in result["message"].lower() for word in ["wardrobe", "adding", "first", "empty"])

    def test_null_wardrobe_handled(self, sample_item, null_wardrobe):
        """Failure mode: wardrobe dict has no 'items' key — should not raise."""
        result = suggest_outfit(sample_item, null_wardrobe)
        assert "wardrobe" in result
        assert isinstance(result["pairings"], list)

    def test_returns_pairings_from_wardrobe(self, wardrobe_with_items):
        """Happy path: wardrobe has items — result contains expected keys."""
        new_item = {
            "id": "test-003",
            "title": "White Sneakers",
            "category": "shoes",
            "style_tags": ["casual", "streetwear"],
            "size": "10",
            "condition": "Good",
            "price": 22.0,
            "colors": ["white"],
            "brand": "Nike",
            "platform": "Depop",
        }
        result = suggest_outfit(new_item, wardrobe_with_items)
        assert isinstance(result["pairings"], list)
        assert result["new_item"] == new_item



    def test_result_contains_expected_keys(self, sample_item, wardrobe_with_items):
        result = suggest_outfit(sample_item, wardrobe_with_items)
        assert "new_item" in result
        assert "pairings" in result
        assert "wardrobe" in result
        assert "message" in result

    def test_wardrobe_returned_in_result(self, sample_item, wardrobe_with_items):
        """Wardrobe should always be returned so the agent can pass it along."""
        result = suggest_outfit(sample_item, wardrobe_with_items)
        assert result["wardrobe"] is not None


# ---------------------------------------------------------------------------
# create_fit_card
# ---------------------------------------------------------------------------

class TestCreateFitCard:

    def _make_outfit(self, pairings=None):
        return {
            "pairings": pairings or [],
            "message": "Here are some pieces that go well together!",
        }

    def test_missing_new_item_returns_error_string(self, another_item):
        """Failure mode: new_item is empty dict — must return error string, not raise."""
        outfit = self._make_outfit(pairings=[another_item])
        result = create_fit_card(outfit, {})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_pairings_returns_string(self, sample_item):
        """Outfit with no pairings should still return a string, not raise."""
        outfit = self._make_outfit(pairings=[])
        result = create_fit_card(outfit, sample_item)
        assert isinstance(result, str)

    def test_returns_string_not_none(self, sample_item, another_item):
        """Return type must always be str, never None."""
        outfit = self._make_outfit(pairings=[another_item])
        result = create_fit_card(outfit, sample_item)
        assert result is not None
        assert isinstance(result, str)

    def test_incomplete_outfit_returns_error_string(self, sample_item):
        """Failure mode: outfit dict is missing pairings key — must not raise."""
        result = create_fit_card({}, sample_item)
        assert isinstance(result, str)
        assert len(result) > 0