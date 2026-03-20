"use client";

import { useEffect, useState } from "react";
import { useStore, VideoFormat, AudioFormat } from "@/lib/store";
import { getDownloadUrl } from "@/lib/api";
import { addHistory } from "@/lib/downloadHistory";
import Image from "next/image";
import FormatCard from "./FormatCard";

export default function DownloadModal() {
  const { modalOpen, closeModal, mediaInfo, inputUrl } = useStore();
  const [activeTab, setActiveTab] = useState<"video" | "audio">("video");
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);

  useEffect(() => {
    if (modalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
      setSelectedFormat(null);
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [modalOpen]);

  useEffect(() => {
    // Auto-select best format when info loads
    if (mediaInfo) {
      if (activeTab === "video" && mediaInfo.video_formats.length > 0) {
        setSelectedFormat(mediaInfo.video_formats[0].format_id);
      } else if (activeTab === "audio" && mediaInfo.audio_formats.length > 0) {
        setSelectedFormat(mediaInfo.audio_formats[0].format_id);
      }
    }
  }, [mediaInfo, activeTab]);

  if (!modalOpen) return null;

  const handleDownload = () => {
    if (!selectedFormat || !mediaInfo) return;

    // Add to history
    let formatLabel = "";
    if (activeTab === "video") {
      const fmt = mediaInfo.video_formats.find((f) => f.format_id === selectedFormat);
      formatLabel = fmt ? `Video • ${fmt.label}` : "Video";
    } else {
      const fmt = mediaInfo.audio_formats.find((f) => f.format_id === selectedFormat);
      formatLabel = fmt ? `Audio • ${fmt.label}` : "Audio";
    }

    addHistory({
      url: inputUrl,
      platform: mediaInfo.platform,
      title: mediaInfo.title,
      format: formatLabel,
    });

    // Trigger download using the proxy route
    const downloadUrl = getDownloadUrl(inputUrl, selectedFormat);
    
    // Assign to location to invoke browser's native file download handler reliably
    window.location.assign(downloadUrl);

    closeModal();
  };

  return (
    <div className="modal-overlay" onClick={closeModal} role="dialog" aria-modal="true">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={closeModal} aria-label="Close modal">
          ✕
        </button>

        {mediaInfo ? (
          <>
            <div className="modal-header">
              {mediaInfo.thumbnail && (
                <div className="modal-thumb">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={mediaInfo.thumbnail} alt="Thumbnail" />
                  <span className="modal-duration">{mediaInfo.duration}</span>
                </div>
              )}
              <div className="modal-meta">
                <h2 className="modal-title" title={mediaInfo.title}>
                  {mediaInfo.title}
                </h2>
                <p className="modal-uploader">{mediaInfo.uploader}</p>
              </div>
            </div>

            <div className="modal-tabs">
              <button
                className={`tab ${activeTab === "video" ? "tab--active" : ""}`}
                onClick={() => setActiveTab("video")}
              >
                Video ({mediaInfo.video_formats.length})
              </button>
              <button
                className={`tab ${activeTab === "audio" ? "tab--active" : ""}`}
                onClick={() => setActiveTab("audio")}
              >
                Audio ({mediaInfo.audio_formats.length})
              </button>
            </div>

            <div className="modal-formats">
              {activeTab === "video" ? (
                mediaInfo.video_formats.length > 0 ? (
                  mediaInfo.video_formats.map((fmt, idx) => (
                    <FormatCard
                      key={fmt.format_id}
                      format={fmt}
                      selected={selectedFormat === fmt.format_id}
                      onSelect={() => setSelectedFormat(fmt.format_id)}
                      best={idx === 0}
                    />
                  ))
                ) : (
                  <p className="empty-formats">No video formats available.</p>
                )
              ) : mediaInfo.audio_formats.length > 0 ? (
                mediaInfo.audio_formats.map((fmt, idx) => (
                  <FormatCard
                    key={fmt.format_id}
                    format={fmt}
                    selected={selectedFormat === fmt.format_id}
                    onSelect={() => setSelectedFormat(fmt.format_id)}
                    best={idx === 0}
                  />
                ))
              ) : (
                <p className="empty-formats">No audio formats available.</p>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn-download"
                onClick={handleDownload}
                disabled={!selectedFormat}
              >
                Download Now
              </button>
            </div>
          </>
        ) : (
          <div className="modal-loading">
            <div className="spinner-large" />
            <p>Gathering download formats...</p>
          </div>
        )}
      </div>
    </div>
  );
}
