"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface SearchBarProps {
  onSearch: (title: string) => void;
}

function SearchIcon() {
  return (
    <svg
      className="w-4 h-4 shrink-0 text-slate-500 ml-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function ClearIcon() {
  return (
    <svg
      className="w-3.5 h-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [title, setTitle] = useState("");

  const submit = (e: React.FormEvent) => {
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
      className="flex items-center gap-0 rounded-xl glass max-w-3xl mx-auto"
    >
      <SearchIcon />
      <input
        className="flex-1 bg-transparent px-3 py-3.5 focus:outline-none text-slate-100 placeholder:text-slate-500 text-sm"
        placeholder="Search a movie — e.g. Inception, Toy Story, Parasite"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        aria-label="Movie title"
      />
      {title && (
        <button
          type="button"
          onClick={() => setTitle("")}
          className="p-2 mr-1 rounded-lg text-slate-600 hover:text-slate-300 transition"
          aria-label="Clear search"
        >
          <ClearIcon />
        </button>
      )}
      <button
        type="submit"
        className="m-1.5 shrink-0 inline-flex items-center gap-1.5 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-400 hover:to-violet-500 active:scale-95 text-white font-medium px-5 py-2.5 rounded-lg shadow text-sm transition-all"
      >
        Find
      </button>
    </motion.form>
  );
}
