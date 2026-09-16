import html
import re
import urllib.parse
import urllib.request
from typing import List


def search_web(query: str, max_results: int = 5) -> str:
    """
    Perform a direct web search using a public search endpoint.

    This is intentionally lightweight and uses no paid API. It is designed to
    provide useful search results in environments where only a browser or raw
    HTTP access is available.
    """
    if not query or not query.strip():
        return "Error: empty search query."

    escaped = urllib.parse.quote(query.strip())
    url = f"https://duckduckgo.com/html/?q={escaped}"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response = urllib.request.urlopen(req, timeout=20)
        if hasattr(response, "read"):
            body = response.read().decode("utf-8", errors="replace")
        else:
            body = str(response)
    except Exception as exc:
        return f"Error searching web: {exc}"

    anchors = re.findall(
        r'<a rel="nofollow" class="result-link" href="(.*?)".*?>(.*?)</a>',
        body,
        re.DOTALL | re.IGNORECASE,
    )

    if not anchors:
        anchors = re.findall(
            r'<a class="result-link" href="(.*?)".*?>(.*?)</a>',
            body,
            re.DOTALL | re.IGNORECASE,
        )

    if not anchors:
        return "No web results found."

    results: List[str] = []
    seen = set()

    for href, text in anchors[:max_results]:
        href = html.unescape(href)
        text = re.sub(r"<.*?>", "", text)
        text = html.unescape(text).strip()

        if not href or not text:
            continue

        if href in seen:
            continue
        seen.add(href)

        results.append(f"{text}\n{href}")

        if len(results) >= max_results:
            break

    if not results:
        return "No web results found."

    return "\n\n".join(results)
