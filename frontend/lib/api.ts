import { MediaInfo } from "./store";

const API_BASE = "/api";

export async function fetchMediaInfo(url: string): Promise<MediaInfo> {
  const res = await fetch(
    `${API_BASE}/info?url=${encodeURIComponent(url)}`,
    { signal: AbortSignal.timeout(60_000) }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Failed to fetch media info");
  }
  return res.json();
}

export function getDownloadUrl(url: string, formatId: string, type: "video" | "audio" = "video"): string {
  return `${API_BASE}/download?url=${encodeURIComponent(url)}&format_id=${encodeURIComponent(formatId)}&type=${type}`;
}
