"use client";

import { useRef, useEffect, useState } from "react";
import { DownloadEntry, getHistory, clearHistory } from "@/lib/downloadHistory";
import PlatformBadge from "./PlatformBadge";
import { Platform } from "@/lib/platformDetect";

export default function DownloadHistory() {
  const [history, setHistory] = useState<DownloadEntry[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setHistory(getHistory());
    setMounted(true);
  }, []);

  if (!mounted || history.length === 0) return null;

  return (
    <div className="history">
      <div className="history__header">
        <h3>Recent Downloads</h3>
        <button onClick={() => { clearHistory(); window.location.reload(); }} className="history__clear">
          Clear
        </button>
      </div>
      <ul className="history__list">
        {history.map((entry: DownloadEntry) => (
          <li key={entry.id} className="history__item">
            <PlatformBadge platform={entry.platform as Platform} size="sm" />
            <div className="history__info">
              <span className="history__title" title={entry.title}>
                {entry.title}
              </span>
              <span className="history__meta">
                {entry.format} • {new Date(entry.timestamp).toLocaleDateString()}
              </span>
            </div>
            <a href={entry.url} className="history__download" aria-label="Download again">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
