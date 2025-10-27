"use client";

import { useEffect, useState } from "react";

export default function DarkToggle() {
  const [mode, setMode] = useState("light");
  const [mounted, setMounted] = useState(false);

  // Detect system or saved theme only on the client
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const current = saved || (prefersDark ? "dark" : "light");
    setMode(current);
    document.documentElement.classList.toggle("dark", current === "dark");
    setMounted(true); // ✅ Avoid SSR/client mismatch
  }, []);

  const toggleMode = () => {
    const next = mode === "dark" ? "light" : "dark";
    setMode(next);
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("theme", next);
  };

  // ⛔ Prevent mismatch: render nothing until mounted
  if (!mounted) {
    return (
      <button
        className="px-3 py-2 rounded-md border border-slate-200/60 dark:border-slate-700 bg-white/60 dark:bg-slate-700/60 shadow-sm"
        aria-label="Toggle dark mode"
      >
        {/* render a placeholder to preserve layout */}
        <span className="opacity-0">🌙</span>
      </button>
    );
  }

  return (
    <button
      onClick={toggleMode}
      className="px-3 py-2 rounded-md border border-slate-200/60 dark:border-slate-700 bg-white/60 dark:bg-slate-700/60 shadow-sm"
      aria-label="Toggle dark mode"
    >
      {mode === "dark" ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}
