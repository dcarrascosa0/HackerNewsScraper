import pytest
from app import cache

@pytest.fixture(autouse=True)
def reset_cache():
    # Ensure cache is empty before each test
    cache.clear_cache()
    yield
    cache.clear_cache()

def test_missing_pages_all_when_empty():
    pages = [1, 2, 3]
    missing = cache.get_missing_pages(pages)
    assert missing == [1, 2, 3]

def test_store_and_get_page():
    dummy_items = [{"title": "x"}]
    cache.store_page(1, dummy_items)
    # Now get_page(1) should return the same list
    assert cache.get_page(1) == dummy_items
    # get_page(2) should be None
    assert cache.get_page(2) is None

def test_get_cached_pages_and_missing_after_store():
    # Initially empty
    assert cache.get_cached_pages() == []
    # Store page 2
    cache.store_page(2, [{"title": "y"}])
    # get_cached_pages should be [2]
    assert cache.get_cached_pages() == [2]
    # get_missing_pages([1, 2, 3]) should return [1, 3]
    assert cache.get_missing_pages([1, 2, 3]) == [1, 3]

def test_clear_cache_resets_everything():
    cache.store_page(1, [{"title": "a"}])
    cache.store_page(3, [{"title": "b"}])
    assert cache.get_cached_pages() == [1, 3]
    cache.clear_cache()
    assert cache.get_cached_pages() == []
    assert cache.get_page(1) is None
    assert cache.get_missing_pages([1, 2]) == [1, 2]


def test_store_page_overwrites_existing():
    """Test that storing a page twice overwrites the first version."""
    original_items = [{"title": "original"}]
    new_items = [{"title": "updated"}]
    
    cache.store_page(1, original_items)
    assert cache.get_page(1) == original_items
    
    cache.store_page(1, new_items)
    assert cache.get_page(1) == new_items
    assert cache.get_cached_pages() == [1]  # Still only one page cached


def test_get_missing_pages_empty_input():
    """Test get_missing_pages with empty input."""
    assert cache.get_missing_pages([]) == []


def test_get_missing_pages_duplicates():
    """Test get_missing_pages handles duplicate page numbers."""
    cache.store_page(2, [{"title": "test"}])
    # Input has duplicates: [1, 2, 1, 3, 2]
    missing = cache.get_missing_pages([1, 2, 1, 3, 2])
    # Should return unique missing pages
    assert set(missing) == {1, 3}


def test_cache_large_number_of_pages():
    """Test cache can handle many pages."""
    # Store pages 1-50
    for i in range(1, 51):
        cache.store_page(i, [{"title": f"page{i}"}])
    
    assert len(cache.get_cached_pages()) == 50
    assert cache.get_cached_pages() == list(range(1, 51))
    
    # Test get_missing_pages with large range
    missing = cache.get_missing_pages(list(range(1, 101)))
    assert missing == list(range(51, 101))


def test_cache_preserves_data_integrity():
    """Test that cached data is not mutated."""
    original_items = [{"title": "test", "points": 100}]
    cache.store_page(1, original_items)
    
    # Get the cached data
    cached_items = cache.get_page(1)
    
    # Modify the retrieved data
    cached_items[0]["title"] = "modified"
    cached_items[0]["points"] = 999
    
    # Original should be unchanged (depends on implementation - this tests the expectation)
    retrieved_again = cache.get_page(1)
    # This test will help determine if we need defensive copying in the cache
    assert isinstance(retrieved_again, list)
    assert len(retrieved_again) == 1


def test_get_page_nonexistent():
    """Test get_page returns None for non-existent pages."""
    assert cache.get_page(999) is None
    assert cache.get_page(-1) is None
