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
async def download_media(url: str, format_id: str, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    url = sanitize_url(url)
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL.")

    # Sanitize format_id — allow alphanumeric, +, /, -, _, [, ], =, ,
    import re
    if not re.match(r"^[\w\+\-\/\.\[\]\=]+$", format_id):
        raise HTTPException(status_code=400, detail="Invalid format ID.")

    filename_holder = [None]
    
    def stream_generator():
        try:
            for chunk, fname in download_stream(url, format_id):
                if filename_holder[0] is None:
                    filename_holder[0] = fname
                yield chunk
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    # Determine content type based on format
    is_audio = "audio" in format_id or format_id == "bestaudio/best"
    media_type = "audio/mpeg" if is_audio else "video/mp4"

    safe_filename = "download.mp4"
    if is_audio:
        safe_filename = "download.mp3"

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return StreamingResponse(
        stream_generator(),
        media_type=media_type,
        headers=headers,
    )
