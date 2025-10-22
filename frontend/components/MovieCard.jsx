"use client";

import { motion } from "framer-motion";

/**
 * MovieCard
 * title: string like "Toy Story 2 (1999)" — we show title and small badge for year if present.
 * Optional enhancement: later add poster fetching from OMDb/TMDB.
 */
export default function MovieCard({ title }) {
  const { label, year } = parseTitle(title);

  return (
    <motion.article
      whileHover={{ scale: 1.03, y: -6 }}
      whileTap={{ scale: 0.98 }}
      layout
      className="relative p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-md border border-slate-100 dark:border-slate-700 cursor-pointer"
      title={title}
    >
      <div className="h-40 rounded-lg bg-gradient-to-br from-indigo-200 to-indigo-300 dark:from-indigo-900 dark:to-indigo-700 flex items-end p-3 text-white font-bold">
        {/* Poster placeholder: initials */}
        <div className="flex-1">
          <div className="text-sm opacity-80">{label}</div>
        </div>
      </div>

      <div className="mt-3 flex items-start justify-between">
        <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {label}
        </div>
        {year && (
          <div className="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200">
            {year}
          </div>
        )}
      </div>
    </motion.article>
  );
}

/* Utility — parse year from a title string like "Toy Story 2 (1999)" */
function parseTitle(raw) {
  if (!raw) return { label: "", year: null };
  const match = raw.match(/^(.*?)(?:\s*\((\d{4})\))?$/);
  if (!match) return { label: raw, year: null };
  return { label: match[1].trim(), year: match[2] || null };
}
