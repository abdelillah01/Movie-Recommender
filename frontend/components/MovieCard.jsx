"use client";

import { motion } from "framer-motion";

export default function MovieCard({ title, poster, release_date }) {
  return (
    <motion.article
      whileHover={{ y: -2, scale: 1.01 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="group relative rounded-2xl overflow-hidden border border-white/10 bg-white/[0.03] backdrop-blur-xl"
    >
      {poster ? (
        <div className="relative">
          <img
            src={poster}
            alt={title}
            className="w-full aspect-[2/3] object-cover saturate-[1.05] contrast-[1.05] transition duration-300 group-hover:brightness-[0.95]"
          />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 p-4">
            <h3 className="font-semibold text-base sm:text-lg text-white drop-shadow">
              {title}
            </h3>
            <p className="text-xs text-slate-300">{release_date || ""}</p>
          </div>
        </div>
      ) : (
        <div className="w-full aspect-[2/3] flex items-center justify-center bg-slate-800 text-slate-300">
          No Poster Available
        </div>
      )}

      <div className="absolute inset-0 rounded-2xl ring-0 ring-white/0 group-hover:ring-1 group-hover:ring-white/20 transition" />
      <div className="absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition glow-indigo" />
    </motion.article>
  );
}
