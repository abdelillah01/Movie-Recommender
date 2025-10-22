"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export default function SearchBar({ onSearch }) {
  const [title, setTitle] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onSearch(title.trim());
  };

  return (
    <motion.form
      onSubmit={submit}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="flex items-center gap-3 p-3 rounded-xl glass border border-slate-200/60 dark:border-slate-700 max-w-3xl mx-auto"
    >
      <input
        className="flex-1 bg-transparent px-4 py-3 rounded-lg focus:outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
        placeholder="Enter movie title (e.g. Toy Story)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        aria-label="Movie title"
      />
      <button
        type="submit"
        className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold px-4 py-2 rounded-lg shadow"
      >
        Recommend
      </button>
    </motion.form>
  );
}
