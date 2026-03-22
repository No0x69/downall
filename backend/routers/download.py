import os
import urllib.parse
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from utils.ytdlp_helper import download_stream
from utils.sanitize import sanitize_url
from utils.platform_detect import is_valid_url
from utils.cache import is_rate_limited

router = APIRouter()


@router.get("/download")
async def download_media(url: str, format_id: str, request: Request, type: str = "video"):
    client_ip = request.client.host if request.client else "unknown"

    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    url = sanitize_url(url)
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL.")

    # Sanitize format_id
    import re
    if not re.match(r"^[\w\+\-\/\.\[\]\=]+$", format_id):
        raise HTTPException(status_code=400, detail="Invalid format ID.")

    # ALWAYS force stable extensions to ignore cached frontend requests
    is_audio = type == "audio"
    ext = "mp3" if is_audio else "mp4"
    media_type = "audio/mpeg" if is_audio else "video/mp4"

    try:
        # Get generator, size, and filename from the helper
        gen, size, fname = download_stream(url, format_id, download_type=type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        print(f"CRITICAL DOWNLOAD ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred during download preparation.")

    headers = {
        "Content-Disposition": f'attachment; filename="download.{ext}"',
        "Content-Length": str(size),
        "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
    }

    return StreamingResponse(
        gen,
        media_type=media_type,
        headers=headers,
    )
