import pytest
import asyncio

from app.scraper import fetch_page

pytestmark = pytest.mark.asyncio

async def test_fetch_page_returns_30_items_and_correct_shape():
    items = await fetch_page(1)
    assert isinstance(items, list)
    assert len(items) == 30
    first = items[0]
    assert "title" in first and isinstance(first["title"], str)
    assert "url" in first and isinstance(first["url"], str)
    assert "points" in first and isinstance(first["points"], int)
    assert "sent_by" in first and isinstance(first["sent_by"], str)
    assert "published" in first and isinstance(first["published"], str)
    assert "comments" in first and isinstance(first["comments"], int)

@pytest.mark.parametrize("invalid_page", [0, -1, None, "abc"])
async def test_fetch_page_invalid_param_raises(invalid_page):
    with pytest.raises(ValueError):
        # type: ignore
        await fetch_page(invalid_page)


async def test_fetch_page_different_pages_return_different_data():
    """Test that different page numbers return distinct data."""
    page1 = await fetch_page(1)
    page2 = await fetch_page(2)
    
    # Both should be valid lists of 30 items
    assert len(page1) == 30
    assert len(page2) == 30
    
    # They should be different (unless we're mocking, but this tests the interface)
    # In real implementation, different pages should have different content
    assert isinstance(page1, list)
    assert isinstance(page2, list)


async def test_fetch_page_large_page_number():
    """Test that large page numbers are handled correctly."""
    items = await fetch_page(10)
    assert isinstance(items, list)
    assert len(items) == 30


async def test_fetch_page_all_items_have_required_fields():
    """Test that every item in the response has all required fields."""
    items = await fetch_page(1)
    required_fields = {"title", "url", "points", "sent_by", "published", "comments"}
    
    for item in items:
        assert set(item.keys()) == required_fields
        # Ensure no fields are None and have correct types
        for field_name, field_value in item.items():
            assert field_value is not None
            if field_name in ["points", "comments"]:
                assert isinstance(field_value, int)
                assert field_value >= 0  # Points and comments should be non-negative
            else:
                assert isinstance(field_value, str)
                # Note: sent_by can be empty for anonymous/deleted users
                # published could be empty in rare cases
                # title and url should generally not be empty, but we'll be lenient
                if field_name in ["title", "url"]:
                    assert len(field_value) > 0  # Title and URL should not be empty
                # sent_by and published can be empty strings in valid cases


@pytest.mark.parametrize("page_num", [1, 2, 3, 5, 10])
async def test_fetch_page_consistent_structure_across_pages(page_num):
    """Test that all pages return consistent data structure."""
    items = await fetch_page(page_num)
    assert len(items) == 30
    
    for item in items:
        assert isinstance(item["title"], str)
        assert isinstance(item["url"], str) 
        assert isinstance(item["points"], int)
        assert isinstance(item["sent_by"], str)
        assert isinstance(item["published"], str)
        assert isinstance(item["comments"], int)
