"use client";

import { useState, useRef, useCallback } from "react";
import { detectPlatform, isValidUrl, Platform } from "@/lib/platformDetect";
import { useStore } from "@/lib/store";
import { fetchMediaInfo } from "@/lib/api";
import PlatformBadge from "./PlatformBadge";

export default function UrlInput() {
  const {
    inputUrl, setInputUrl,
    detectedPlatform, setDetectedPlatform,
    openModal, setMediaInfo, setLoading, setError,
    loading,
  } = useStore();

  const [inputError, setInputError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = useCallback((val: string) => {
    setInputUrl(val);
    setInputError(null);
    if (val.trim()) {
      const p = detectPlatform(val);
      setDetectedPlatform(p);
    } else {
      setDetectedPlatform(null);
    }
  }, [setInputUrl, setDetectedPlatform]);

  const handlePaste = useCallback((e: React.ClipboardEvent<HTMLInputElement>) => {
    const text = e.clipboardData.getData("text");
    setTimeout(() => handleChange(text), 10);
  }, [handleChange]);

  const handleDownload = useCallback(async () => {
    const url = inputUrl.trim();
    if (!url) {
      setInputError("Please paste a video URL first.");
      inputRef.current?.focus();
      return;
    }
    if (!isValidUrl(url)) {
      setInputError("URL must start with http:// or https://");
      return;
    }
    if (!detectedPlatform) {
      setInputError("Unsupported platform. Try a YouTube, Instagram, Facebook, or TikTok link.");
      return;
    }

    setError(null);
    setLoading(true);
    openModal();

    try {
      const info = await fetchMediaInfo(url);
      setMediaInfo(info);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [inputUrl, detectedPlatform, setError, setLoading, openModal, setMediaInfo]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleDownload();
  };

  const handleClear = () => {
    setInputUrl("");
    setDetectedPlatform(null);
    setInputError(null);
    inputRef.current?.focus();
  };

  return (
    <div className="url-input-container">
      <div className={`url-input-wrapper ${inputError ? "url-input-wrapper--error" : ""}`}>
        {detectedPlatform && (
          <div className="url-input__badge-wrapper">
            <PlatformBadge platform={detectedPlatform} size="sm" />
          </div>
        )}
        <input
          ref={inputRef}
          type="url"
          className="url-input__field"
          placeholder="Paste a YouTube, Instagram, Facebook, or TikTok URL..."
          value={inputUrl}
          onChange={(e) => handleChange(e.target.value)}
          onPaste={handlePaste}
          onKeyDown={handleKeyDown}
          disabled={loading}
          autoFocus
        />
        {inputUrl && (
          <button
            className="url-input__clear"
            onClick={handleClear}
            aria-label="Clear input"
            type="button"
          >
            ✕
          </button>
        )}
        <button
          className="url-input__btn"
          onClick={handleDownload}
          disabled={loading || !inputUrl.trim()}
          type="button"
        >
          {loading ? (
            <span className="spinner" />
          ) : (
            <>
              <span>⬇</span>
              <span>Download</span>
            </>
          )}
        </button>
      </div>
      {inputError && (
        <p className="url-input__error" role="alert">
          ⚠️ {inputError}
        </p>
      )}
      <p className="url-input__hint">
        Supports YouTube, Instagram, Facebook, TikTok · Free · No sign-up
      </p>
    </div>
  );
}
