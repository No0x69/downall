export interface DownloadEntry {
  id: string;
  url: string;
  platform: string;
  title: string;
  format: string;
  timestamp: number;
}

const KEY = "vdl_history";
const MAX = 20;

export function getHistory(): DownloadEntry[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function addHistory(entry: Omit<DownloadEntry, "id" | "timestamp">) {
  try {
    const history = getHistory();
    // crypto.randomUUID is only available in Secure Contexts (HTTPS)
    const id = typeof crypto !== 'undefined' && crypto.randomUUID 
      ? crypto.randomUUID() 
      : Math.random().toString(36).substring(2, 15);

    const newEntry: DownloadEntry = {
      ...entry,
      id,
      timestamp: Date.now(),
    };
    const updated = [newEntry, ...history].slice(0, MAX);
    localStorage.setItem(KEY, JSON.stringify(updated));
    return updated;
  } catch (err) {
    console.error("Failed to add to history:", err);
    return [];
  }
}

export function clearHistory() {
  localStorage.removeItem(KEY);
}
