 # app/cache.py

_page_store: dict[int, list[dict]] = {}
_cached_pages: set[int] = set()

def get_missing_pages(pages: list[int]) -> list[int]:
    """
    Return subset of `pages` not yet in cache.
    """
    raise NotImplementedError("get_missing_pages not implemented")

def get_page(page_number: int) -> list[dict] | None:
    """
    Return cached items for page_number, or None.
    """
    raise NotImplementedError("get_page not implemented")

def store_page(page_number: int, items: list[dict]) -> None:
    """
    Store `items` under page_number and mark as cached.
    """
    raise NotImplementedError("store_page not implemented")

def clear_cache() -> None:
    """
    Clear entire in-memory cache.
    """
    raise NotImplementedError("clear_cache not implemented")

def get_cached_pages() -> list[int]:
    """
    Return sorted list of cached page numbers.
    """
    raise NotImplementedError("get_cached_pages not implemented")
