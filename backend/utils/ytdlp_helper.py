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
    # Using specific clients help bypass current YouTube blocks.
    # 'android_vr' and 'web_embedded' currently expose the most DASH formats.
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        "--no-warnings",
        "--extractor-args", "youtube:player-client=android_vr,web_embedded",
        url,
    ]
    result = subprocess.run(
        cmd,
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
    # We add more robust extractor args to try and bypass throttling/SABR issues
    # Using 'tv' and 'android' clients often helps without requiring PO tokens
    info = _run_ytdlp_json(url)

    title = info.get("title", "Unknown Title")
    duration = _format_duration(info.get("duration"))
    thumbnail = info.get("thumbnail", "")
    uploader = info.get("uploader") or info.get("channel", "")
    platform = info.get("extractor_key", "").lower()

    raw_formats = info.get("formats", [])

    video_formats = []
    audio_formats = []
    seen_heights = set()

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

        # Video formats
        elif vcodec != "none" and height:
            if height in seen_heights:
                continue
                
            has_audio = acodec != "none" and acodec != "none"
            final_fmt = fmt_id
            
            # If video has no audio (DASH/HLS), merge it with best audio!
            if not has_audio:
                final_fmt = f"{fmt_id}+bestaudio[ext=m4a]/bestaudio/best"
                has_audio = True

            label = f"{height}p"
            if height >= 2160:
                label = f"4K {height}p"
            elif height >= 1440:
                label = f"2K {height}p"
            elif height >= 1080:
                label = f"1080p HD"
            elif height >= 720:
                label = f"720p"

            # Determine codec labels for user visibility
            codec_label = ""
            if "avc1" in vcodec or "h264" in vcodec:
                codec_label = " (H.264)" # Highly compatible with Mac/iOS
            elif "vp09" in vcodec or "vp9" in vcodec:
                codec_label = " (VP9)"
            elif "av01" in vcodec or "av1" in vcodec:
                codec_label = " (AV1)"
            
            # Update the label with more info
            full_label = f"{label}{codec_label}"

            video_formats.append({
                "format_id": final_fmt,
                "type": "video",
                "label": full_label,
                "height": height,
                "ext": ext if ext != "none" else "mp4",
                "filesize": filesize,
                "has_audio": has_audio,
                "vcodec": vcodec,
                "acodec": acodec,
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


def download_stream(url: str, format_id: str, download_type: str = "video"):
    """
    Downloads a video from a URL in the specified format and return a generator, size, and filename.
    """
    temp_dir = tempfile.mkdtemp()
    temp_dir_path = Path(temp_dir)
    out_template = str(temp_dir_path / "%(title)s.%(ext)s")
    
    # Build yt-dlp command
    cmd = [
        "yt-dlp",
        "--newline",
        "--no-playlist",
        "--socket-timeout", "30",
        "--extractor-args", "youtube:player-client=android_vr,web_embedded",
        "-f", format_id,
        "--merge-output-format", "mp4",
        "--ffmpeg-location", imageio_ffmpeg.get_ffmpeg_exe(),
        "-o", out_template,
    ]

    if download_type == "audio":
        cmd += ["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]

    cmd.append(url)
    
    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=600)
        
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace")
            print(f"Error: {stderr}")
            shutil.rmtree(temp_dir)
            raise ValueError(f"Download failed: {stderr[:500]}")

        # Find the output file
        files = list(temp_dir_path.iterdir())
        if not files:
            shutil.rmtree(temp_dir)
            raise ValueError("No output file was created.")

        # Pick largest file
        out_file = max(files, key=lambda f: f.stat().st_size)
        filename = out_file.name
        filesize = out_file.stat().st_size

        def generator():
            try:
                with open(out_file, "rb") as f:
                    while chunk := f.read(1024 * 64):
                        yield chunk
            finally:
                # Cleanup temp directory when generator is exhausted OR closed
                shutil.rmtree(temp_dir)

        return generator(), filesize, filename
    except Exception as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e
