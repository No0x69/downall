export type Platform = "youtube" | "instagram" | "facebook" | "tiktok";

const PATTERNS: Record<Platform, RegExp[]> = {
  youtube: [
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=/i,
    /(?:https?:\/\/)?(?:www\.)?youtu\.be\//i,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\//i,
  ],
  instagram: [
    /(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:p|reel|tv)\//i,
  ],
  facebook: [
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/.+\/videos\//i,
    /(?:https?:\/\/)?(?:www\.)?fb\.watch\//i,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/watch/i,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/reel\//i,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/share\/v\//i,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/share\/r\//i,
    /(?:https?:\/\/)?m\.facebook\.com\//i,
  ],
  tiktok: [
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@[^/]+\/video\//i,
    /(?:https?:\/\/)?vm\.tiktok\.com\//i,
    /(?:https?:\/\/)?vt\.tiktok\.com\//i,
    /(?:https?:\/\/)?m\.tiktok\.com\//i,
  ],
};

export function detectPlatform(url: string): Platform | null {
  for (const [platform, patterns] of Object.entries(PATTERNS) as [Platform, RegExp[]][]) {
    if (patterns.some((p) => p.test(url))) {
      return platform;
    }
  }
  return null;
}

export function isValidUrl(url: string): boolean {
  return /^https?:\/\//i.test(url.trim());
}
