from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from utils.ytdlp_helper import get_info
from utils.sanitize import sanitize_url
from utils.platform_detect import is_valid_url, detect_platform
from utils.cache import cache_get, cache_set, is_rate_limited

router = APIRouter()


@router.get("/info")
async def get_media_info(url: str, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    url = sanitize_url(url)

    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL. Please provide a valid link.")

    platform = detect_platform(url)
    if not platform:
        raise HTTPException(
            status_code=400,
            detail="Unsupported platform. We support YouTube, Instagram, Facebook, and TikTok.",
        )

    # Check cache
    cached = cache_get(url)
    if cached:
        return JSONResponse(content={"cached": True, **cached})

    try:
        info = get_info(url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch media info: {str(e)[:200]}")

    cache_set(url, info)
    return JSONResponse(content={"cached": False, **info})
