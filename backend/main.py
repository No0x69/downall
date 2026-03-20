from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import info, download

app = FastAPI(
    title="Video Downloader API",
    description="Download videos and audio from YouTube, Instagram, Facebook, TikTok",
    version="1.0.0",
)

# CORS — allow Next.js frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register routers
app.include_router(info.router, prefix="/api")
app.include_router(download.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
