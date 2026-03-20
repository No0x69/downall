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
  const history = getHistory();
  const newEntry: DownloadEntry = {
    ...entry,
    id: crypto.randomUUID(),
    timestamp: Date.now(),
  };
  const updated = [newEntry, ...history].slice(0, MAX);
  localStorage.setItem(KEY, JSON.stringify(updated));
  return updated;
}

export function clearHistory() {
  localStorage.removeItem(KEY);
}
