"use client";

import { useTheme } from "@/lib/useTheme";

export default function ThemeToggle() {
  const { theme, toggle } = useTheme();

  return (
    <button
      onClick={toggle}
      className="theme-toggle"
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      <span className="toggle-track">
        <span className="toggle-thumb" />
        <span className="toggle-icon sun">☀️</span>
        <span className="toggle-icon moon">🌙</span>
      </span>
    </button>
  );
}
