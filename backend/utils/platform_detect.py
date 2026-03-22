from __future__ import annotations
import re

PATTERNS = {
    "youtube": [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=",
        r"(?:https?://)?(?:www\.)?youtu\.be/",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/",
    ],
    "instagram": [
        r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|tv)/",
    ],
    "facebook": [
        r"(?:https?://)?(?:www\.)?facebook\.com/.+/videos/",
        r"(?:https?://)?(?:www\.)?fb\.watch/",
        r"(?:https?://)?(?:www\.)?facebook\.com/watch",
        r"(?:https?://)?(?:www\.)?facebook\.com/reel/",
        r"(?:https?://)?(?:www\.)?facebook\.com/share/v/",
        r"(?:https?://)?(?:www\.)?facebook\.com/share/r/",
        r"(?:https?://)?m\.facebook\.com/",
    ],
    "tiktok": [
        r"(?:https?://)?(?:www\.)?tiktok\.com/@[^/]+/video/",
        r"(?:https?://)?vm\.tiktok\.com/",
        r"(?:https?://)?vt\.tiktok\.com/",
        r"(?:https?://)?m\.tiktok\.com/",
    ],
}


def detect_platform(url: str) -> str | None:
    for platform, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return None


def is_valid_url(url: str) -> bool:
    return bool(re.match(r"https?://", url.strip()))
