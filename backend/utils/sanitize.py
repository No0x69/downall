import re
import html


def sanitize_url(url: str) -> str:
    """Strip whitespace and basic HTML entities from URL."""
    url = url.strip()
    url = html.unescape(url)
    # Allow only safe URL characters
    url = re.sub(r"[^\w\-._~:/?#\[\]@!$&'()*+,;=%]", "", url)
    return url
