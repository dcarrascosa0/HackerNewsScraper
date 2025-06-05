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
