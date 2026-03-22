import sys
import os
sys.path.append(os.path.abspath('backend'))

from utils.ytdlp_helper import download_stream
import json

try:
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    # Format 137 is 1080p video only on Youtube
    format_id = "137+bestaudio[ext=m4a]/bestaudio/best" 
    print(f"Testing merged download for {url} format {format_id}...")
    
    count = 0
    for chunk, filename in download_stream(url, format_id):
        if count == 0:
            print(f"Started receiving: {filename}")
        count += len(chunk)
        if count > 5 * 1024 * 1024: # 5MB
            print(f"Received {count} bytes, stopping test.")
            break
            
    print("Download test successful!")
    
except Exception as e:
    print("Error:", e)
