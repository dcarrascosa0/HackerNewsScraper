import httpx
from bs4 import BeautifulSoup


async def fetch_page_html(page_number: int) -> str:
    """
    Fetch and return the raw HTML for Hacker News page `p=<page_number>`.
    Raises ValueError if page_number is not a positive integer.
    """
    if not isinstance(page_number, int) or page_number < 1:
        raise ValueError("page_number must be an integer ≥ 1")

    url = f"https://news.ycombinator.com/news?p={page_number}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def parse_items_from_html(html: str) -> list[dict]:
    """
    Parse exactly 30 front‐page items from the given HTML.
    Each item is a dict with keys: { title, url, points, sent_by, published, comments }.
    """
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict] = []

    for element in soup.select(".athing"):
        # Extract title and raw href
        title_tag = element.select_one(".titleline > a")
        title = title_tag.get_text(strip=True)
        href = title_tag.get("href") or ""
        url_full = (
            f"https://news.ycombinator.com/{href}"
            if href.startswith("item?id=")
            else href
        )

        # The sibling element contains subtext (points, user, age, comments)
        subtext = element.find_next_sibling().select_one(".subtext")

        # Points
        score_tag = subtext.select_one(".score")
        points = int(score_tag.get_text().replace(" points", "")) if score_tag else 0

        # Username who submitted
        user_tag = subtext.select_one(".hnuser")
        sent_by = user_tag.get_text(strip=True) if user_tag else ""

        # Age (published)
        age_tag = subtext.select_one(".age")
        published = age_tag.get_text(strip=True) if age_tag else ""

        # Comments count
        comments = 0
        comment_links = subtext.find_all("a")
        if comment_links:
            last_link_text = comment_links[-1].get_text()
            if "comment" in last_link_text:
                num_str = last_link_text.split("\u00A0")[0]  # e.g. "24 comments" → "24"
                comments = int(num_str) if num_str.isdigit() else 0

        items.append({
            "title": title,
            "url": url_full,
            "points": points,
            "sent_by": sent_by,
            "published": published,
            "comments": comments
        })

    # If Hacker News layout changes and we don’t get exactly 30 items, warn but still return what we got
    if len(items) != 30:
        print(f"Warning: expected 30 items from HTML, but parsed {len(items)}")

    return items


async def fetch_page(page_number: int) -> list[dict]:
    """
    Public interface: fetch raw HTML and parse into 30 news items.
    Returns a list of dicts, each with { title, url, points, sent_by, published, comments }.
    """
    html = await fetch_page_html(page_number)
    return parse_items_from_html(html)
