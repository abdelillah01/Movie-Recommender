"use client";

import { motion } from "framer-motion";

export default function MovieCard({ title, poster, release_date }) {
  return (
    <motion.article
      whileHover={{ scale: 1.05 }}
      className="rounded-2xl overflow-hidden shadow-lg bg-white dark:bg-gray-900 transition-transform"
    >
      {poster ? (
        <img
          src={poster}
          alt={title}
          className="w-full h-80 object-cover"
        />
      ) : (
        <div className="w-full h-80 flex items-center justify-center bg-gray-700 text-gray-300">
          No Poster Available
        </div>
      )}

      <div className="p-4">
        <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100">
          {title}
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {release_date || "Unknown Year"}
        </p>
      </div>
    </motion.article>
  );
}
