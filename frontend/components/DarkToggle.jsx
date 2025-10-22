"use client";

import { useEffect, useState } from "react";

export default function DarkToggle() {
  const [mode, setMode] = useState(() => {
    if (typeof window === "undefined") return "light";
    return localStorage.theme === "dark" || (!("theme" in localStorage) && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
      ? "dark"
      : "light";
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (mode === "dark") {
      root.classList.add("dark");
      localStorage.theme = "dark";
    } else {
      root.classList.remove("dark");
      localStorage.theme = "light";
    }
  }, [mode]);

  return (
    <button
      onClick={() => setMode(mode === "dark" ? "light" : "dark")}
      className="px-3 py-2 rounded-md border border-slate-200/60 dark:border-slate-700 bg-white/60 dark:bg-slate-700/60 shadow-sm"
      aria-label="Toggle dark mode"
    >
      {mode === "dark" ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}
