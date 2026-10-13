"use client";

import { motion } from "framer-motion";

function parseTitle(raw) {
  const m = raw?.match(/^(.*?)\s*\((\d{4})\)\s*$/);
  return m ? { title: m[1].trim(), year: m[2] } : { title: raw || "", year: null };
}

function FilmIcon() {
  return (
    <svg
      width="40"
      height="40"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-slate-600"
    >
      <rect x="2" y="2" width="20" height="20" rx="2" />
      <line x1="7" y1="2" x2="7" y2="22" />
      <line x1="17" y1="2" x2="17" y2="22" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <line x1="2" y1="7" x2="7" y2="7" />
      <line x1="17" y1="7" x2="22" y2="7" />
      <line x1="17" y1="17" x2="22" y2="17" />
      <line x1="2" y1="17" x2="7" y2="17" />
    </svg>
  );
}

export default function MovieCard({ title: rawTitle, poster }) {
  const { title, year } = parseTitle(rawTitle);

  return (
    <motion.article
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="group relative rounded-2xl overflow-hidden border border-white/10 bg-white/[0.03] backdrop-blur-xl"
    >
      {poster ? (
        <div className="relative">
          <img
            src={poster}
            alt={title}
            className="w-full aspect-[2/3] object-cover saturate-[1.05] contrast-[1.02] transition duration-300 group-hover:brightness-90"
          />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 p-4">
            <h3 className="font-semibold text-sm leading-snug text-white drop-shadow line-clamp-2">
              {title}
            </h3>
            {year && <p className="mt-1 text-xs text-slate-400">{year}</p>}
          </div>
        </div>
      ) : (
        <div className="w-full aspect-[2/3] flex flex-col items-center justify-center gap-3 bg-slate-900/60">
          <FilmIcon />
          <div className="px-4 text-center">
            <p className="text-xs font-medium text-slate-400 line-clamp-2">{title}</p>
            {year && <p className="mt-1 text-xs text-slate-600">{year}</p>}
          </div>
        </div>
      )}

      <div className="absolute inset-0 rounded-2xl ring-0 ring-white/0 group-hover:ring-1 group-hover:ring-white/20 transition" />
      <div className="absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition glow-indigo" />
    </motion.article>
  );
}
