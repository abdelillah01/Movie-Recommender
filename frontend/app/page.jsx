"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import SearchBar from "../components/SearchBar";
import MovieCard from "../components/MovieCard";
import LoadingSkeleton from "../components/LoadingSkeleton";
import DarkToggle from "../components/DarkToggle";
import recommendMovies from "./api/recommend";

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

      // Normalize: backend should return [{ title, poster, release_date }, ...]
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
    <main className="min-h-screen flex flex-col items-center px-6 py-12">
      <div className="w-full max-w-5xl">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <motion.h1
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100"
            >
              Movie Recommender
            </motion.h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">
              Clean modern UI — search a movie to get recommendations.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <DarkToggle />
          </div>
        </header>

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} />
        </div>

        {/* Loading Skeletons */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <LoadingSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Error Message */}
        {!loading && error && (
          <div className="mt-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800 text-red-700 dark:text-red-200">
            {error}
          </div>
        )}

        {/* Empty State */}
        <AnimatePresence>
          {!loading && movies.length === 0 && !error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 text-center text-slate-500 dark:text-slate-300"
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
