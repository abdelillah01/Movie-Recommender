"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import SearchBar from "../components/SearchBar";
import MovieCard from "../components/MovieCard";
import LoadingSkeleton from "../components/LoadingSkeleton";
import DarkToggle from "../components/DarkToggle";
import recommendMovies from "./api/recommend";
import BackgroundFX from "../components/BackgroundFX";

const fadeIn = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } },
};

export default function Home() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (title) => {
    setError("");
    setMovies([]);
    setLoading(true);

    try {
      const results = await recommendMovies(title);

      const normalized = Array.isArray(results)
        ? results.map((r) => ({
            title: r.title || r.text || String(r),
            poster: r.poster || "",
            release_date: r.release_date || "",
          }))
        : [];

      setMovies(normalized);
    } catch (err) {
      console.error("Search failed:", err);
      setError("Could not fetch recommendations. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0B0F17] text-slate-100">
      <BackgroundFX />

      <div className="relative mx-auto w-full max-w-6xl px-6 py-12">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <motion.div initial="hidden" animate="show" variants={fadeIn}>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-100 to-slate-300">
                Movie Recommender
              </span>
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Tired of always asking 'What movie should I watch?' Get clean, cinematic recommendations with a sleek, modern feel.
            </p>
          </motion.div>

          <div className="flex items-center gap-3">
            <DarkToggle />
          </div>
        </header>

        {/* Search Bar */}
        <motion.div initial="hidden" animate="show" variants={fadeIn} className="mb-8">
          <SearchBar onSearch={handleSearch} />
        </motion.div>

        {/* Loading Skeletons */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
          >
            {[...Array(8)].map((_, i) => (
              <LoadingSkeleton key={i} />
            ))}
          </motion.div>
        )}

        {/* Error Message */}
        {!loading && error && (
          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeIn}
            className="mt-6 p-4 rounded-xl glass text-red-200 border-red-300/10"
          >
            {error}
          </motion.div>
        )}

        {/* Empty State */}
        <AnimatePresence>
          {!loading && movies.length === 0 && !error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 text-center text-slate-400"
            >
              Try “Toy Story” or another movie — recommendations will appear here.
            </motion.div>
          )}
        </AnimatePresence>

        {/* Movie Cards */}
        {!loading && movies.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            layout
            className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
          >
            {movies.map((m, idx) => (
              <MovieCard
                key={idx}
                title={m.title}
                poster={m.poster}
                release_date={m.release_date}
              />
            ))}
          </motion.div>
        )}
      </div>
    </main>
  );
}
