import sys
import os
sys.path.append(os.path.abspath('backend'))

from utils.ytdlp_helper import _run_ytdlp_json
import json

try:
    info = _run_ytdlp_json("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    
    print("Raw video formats:")
    for f in info.get("formats", []):
        if f.get("vcodec", "none") != "none":
            print(f"Format: {f.get('format_id')}, Height: {f.get('height')}, Ext: {f.get('ext')}, Acodec: {f.get('acodec')}")
    
except Exception as e:
    print("Error:", e)
