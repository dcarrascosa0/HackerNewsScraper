# app/cache.py

_page_store: dict[int, list[dict]] = {}
_cached_pages: set[int] = set()

def get_missing_pages(pages: list[int]) -> list[int]:
    """
    Return the subset of `pages` that are not yet cached.
    """
    return [p for p in pages if p not in _cached_pages]

def get_page(page_number: int) -> list[dict] | None:
    """
    Return cached items for `page_number`, or None if not cached.
    """
    return _page_store.get(page_number)

def store_page(page_number: int, items: list[dict]) -> None:
    """
    Store `items` under `page_number` and mark that page as cached.
    """
    _page_store[page_number] = items
    _cached_pages.add(page_number)

def clear_cache() -> None:
    """
    Clear the entire in‐memory cache (used in tests or on restart).
    """
    _page_store.clear()
    _cached_pages.clear()

def get_cached_pages() -> list[int]:
    """
    Return a sorted list of currently cached page numbers.
    """
    return sorted(_cached_pages)
