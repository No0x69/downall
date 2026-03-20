import asyncio
import subprocess
import json
import os
import tempfile
import shutil
from pathlib import Path
import imageio_ffmpeg


def _run_ytdlp_json(url: str) -> dict:
    """Extract info dict from yt-dlp (no download)."""
    result = subprocess.run(
        [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--no-warnings",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        err = result.stderr.strip()
        if "Private video" in err or "private" in err.lower():
            raise ValueError("This video is private or unavailable.")
        if "not available" in err.lower() or "unavailable" in err.lower():
            raise ValueError("This video is unavailable in your region or has been removed.")
        raise ValueError(f"yt-dlp error: {err[:300]}")
    return json.loads(result.stdout)


def _format_duration(seconds) -> str:
    if not seconds:
        return "Unknown"
    try:
        s = int(seconds)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"
    except Exception:
        return "Unknown"


def get_info(url: str) -> dict:
    """Return structured metadata + format list for a URL."""
    info = _run_ytdlp_json(url)

    title = info.get("title", "Unknown Title")
    duration = _format_duration(info.get("duration"))
    thumbnail = info.get("thumbnail", "")
    uploader = info.get("uploader") or info.get("channel", "")
    platform = info.get("extractor_key", "").lower()

    raw_formats = info.get("formats", [])

    VIDEO_HEIGHTS = [144, 240, 360, 480, 720, 1080, 1440, 2160]
    seen_heights = set()
    video_formats = []
    audio_formats = []

    for f in raw_formats:
        fmt_id = f.get("format_id", "")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        height = f.get("height")
        abr = f.get("abr")
        ext = f.get("ext", "mp4")
        filesize = f.get("filesize") or f.get("filesize_approx")
        tbr = f.get("tbr")

        # Pure audio formats
        if vcodec == "none" and acodec != "none" and abr:
            abr_rounded = round(abr / 32) * 32  # snap to 32/64/128/192/256/320
            abr_rounded = max(64, min(320, abr_rounded))
            audio_formats.append({
                "format_id": fmt_id,
                "type": "audio",
                "label": f"MP3 {abr_rounded}kbps",
                "abr": abr_rounded,
                "ext": "mp3",
                "filesize": filesize,
                "tbr": tbr,
            })

        # Video formats (may have audio merged or be video-only)
        elif vcodec != "none" and height and height in VIDEO_HEIGHTS and height not in seen_heights:
            has_audio = acodec != "none"
            final_fmt = fmt_id
            
            # If video has no audio (common for 1080p+), merge it with best audio!
            if not has_audio:
                final_fmt = f"{fmt_id}+bestaudio[ext=m4a]/bestaudio/best"
                has_audio = True

            label = f"{height}p"
            if height >= 2160:
                label = "4K 2160p"
            elif height >= 1440:
                label = "2K 1440p"
            elif height >= 1080:
                label = "HD 1080p"

            video_formats.append({
                "format_id": final_fmt,
                "type": "video",
                "label": label,
                "height": height,
                "ext": "mp4", # Merged files usually end up as mp4
                "has_audio": has_audio,
                "filesize": filesize,
                "tbr": tbr,
            })
            seen_heights.add(height)

    # Sort
    video_formats.sort(key=lambda x: x["height"], reverse=True)
    # Deduplicate audio by abr
    seen_abr = set()
    deduped_audio = []
    for a in sorted(audio_formats, key=lambda x: x["abr"], reverse=True):
        if a["abr"] not in seen_abr:
            deduped_audio.append(a)
            seen_abr.add(a["abr"])

    # Always include a "best audio" option
    if not deduped_audio:
        deduped_audio = [{
            "format_id": "bestaudio/best",
            "type": "audio",
            "label": "Best Audio",
            "abr": 0,
            "ext": "mp3",
            "filesize": None,
            "tbr": None,
        }]

    return {
        "title": title,
        "duration": duration,
        "thumbnail": thumbnail,
        "uploader": uploader,
        "platform": platform,
        "video_formats": video_formats,
        "audio_formats": deduped_audio,
    }


def download_stream(url: str, format_id: str):
    """Generator that yields file bytes for the given format."""
    tmpdir = tempfile.mkdtemp()
    out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
    try:
        # Build yt-dlp args
        if format_id in ("bestaudio/best",):
            fmt_arg = format_id
        else:
            fmt_arg = format_id

        # For audio formats, post-process to mp3
        cmd = [
            "yt-dlp",
            "--ffmpeg-location", imageio_ffmpeg.get_ffmpeg_exe(),
            "-f", fmt_arg,
            "--merge-output-format", "mp4",
            "--no-playlist",
            "-o", out_template,
        ]

        # if it's audio-only request, convert to mp3
        is_audio = format_id.startswith("bestaudio") or "audio" in format_id
        if is_audio:
            cmd += ["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]

        cmd.append(url)

        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode != 0:
            raise ValueError(f"Download failed: {result.stderr.decode()[:200]}")

        # Find the output file
        files = list(Path(tmpdir).iterdir())
        if not files:
            raise ValueError("No output file was created.")

        out_file = files[0]
        filename = out_file.name

        with open(out_file, "rb") as f:
            while chunk := f.read(1024 * 64):
                yield chunk, filename
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
