import { create } from "zustand";
import { Platform } from "./platformDetect";

export interface VideoFormat {
  format_id: string;
  type: "video";
  label: string;
  height: number;
  ext: string;
  has_audio: boolean;
  filesize: number | null;
  tbr: number | null;
  vcodec?: string;
  acodec?: string;
}

export interface AudioFormat {
  format_id: string;
  type: "audio";
  label: string;
  abr: number;
  ext: string;
  filesize: number | null;
  tbr: number | null;
}

export interface MediaInfo {
  title: string;
  duration: string;
  thumbnail: string;
  uploader: string;
  platform: string;
  video_formats: VideoFormat[];
  audio_formats: AudioFormat[];
}

interface AppState {
  inputUrl: string;
  detectedPlatform: Platform | null;
  modalOpen: boolean;
  mediaInfo: MediaInfo | null;
  loading: boolean;
  error: string | null;

  setInputUrl: (url: string) => void;
  setDetectedPlatform: (p: Platform | null) => void;
  openModal: () => void;
  closeModal: () => void;
  setMediaInfo: (info: MediaInfo | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (err: string | null) => void;
}

export const useStore = create<AppState>((set) => ({
  inputUrl: "",
  detectedPlatform: null,
  modalOpen: false,
  mediaInfo: null,
  loading: false,
  error: null,

  setInputUrl: (url) => set({ inputUrl: url }),
  setDetectedPlatform: (p) => set({ detectedPlatform: p }),
  openModal: () => set({ modalOpen: true }),
  closeModal: () => set({ modalOpen: false, mediaInfo: null, error: null }),
  setMediaInfo: (info) => set({ mediaInfo: info }),
  setLoading: (loading) => set({ loading }),
  setError: (err) => set({ error: err }),
}));
