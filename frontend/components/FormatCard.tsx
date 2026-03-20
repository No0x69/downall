"use client";

import { VideoFormat, AudioFormat } from "@/lib/store";

interface Props {
  format: VideoFormat | AudioFormat;
  selected: boolean;
  onSelect: () => void;
  best?: boolean;
}

function formatBytes(bytes: number | null) {
  if (!bytes) return "Unknown size";
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(1) + " " + ["B", "KB", "MB", "GB"][i];
}

export default function FormatCard({ format, selected, onSelect, best }: Props) {
  const isVideo = format.type === "video";
  const label = isVideo ? format.label : format.label;

  return (
    <button
      className={`format-card ${selected ? "format-card--selected" : ""} ${best ? "format-card--best" : ""}`}
      onClick={onSelect}
      type="button"
    >
      <div className="format-card__content">
        <span className="format-card__label">{label}</span>
        {best && <span className="format-card__badge">Best</span>}
        <div className="format-card__details">
          <span>{format.ext.toUpperCase()}</span>
          <span>•</span>
          <span>{formatBytes(format.filesize)}</span>
        </div>
        {isVideo && !format.has_audio && (
          <span className="format-card__muted" title="Video only, no sound">
            🔇 No Audio
          </span>
        )}
      </div>
      <div className="format-card__radio">
        {selected && <div className="format-card__radio-inner" />}
      </div>
    </button>
  );
}
