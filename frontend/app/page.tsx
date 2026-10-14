"use client";

import { useState } from "react";
import { motion, AnimatePresence, type Variants } from "framer-motion";
import SearchBar from "../components/SearchBar";
import MovieCard from "../components/MovieCard";
import LoadingSkeleton from "../components/LoadingSkeleton";
import BackgroundFX from "../components/BackgroundFX";
import recommendMovies, { type Movie } from "../lib/api";

const FEATURED = [
  "Inception", "The Dark Knight", "Toy Story", "Interstellar",
  "Pulp Fiction", "The Matrix", "Forrest Gump", "Parasite",
];

const fadeIn: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

const gridVariants: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.3, ease: "easeOut" } },
};

export default function Home() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [matched, setMatched] = useState<string | null>(null);

  const handleSearch = async (title: string) => {
    setError("");
    setMovies([]);
    setQuery(title);
    setMatched(null);
    setLoading(true);

    try {
      const { matched: m, recommendations } = await recommendMovies(title);
      setMatched(m);
      setMovies(recommendations);
    } catch (err) {
      console.error("Search failed:", err);
      setError("Could not fetch recommendations. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const hasResults = !loading && movies.length > 0;
  const isEmpty = !loading && movies.length === 0 && !error && !query;

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0B0F17] text-slate-100">
      <BackgroundFX />

      <div className="relative mx-auto w-full max-w-6xl px-6 py-12">
        {/* Header */}
        <motion.header
          initial="hidden"
          animate="show"
          variants={fadeIn}
          className="mb-10"
        >
          <div className="flex items-center gap-2.5 mb-1">
            <ClapperIcon />
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400">
                Movie Recommender
              </span>
            </h1>
          </div>
          <p className="text-sm text-slate-500 pl-[2.1rem]">
            Enter a film you love &mdash; get ten you&apos;ll want to watch next.
          </p>
        </motion.header>

        {/* Search Bar */}
        <motion.div initial="hidden" animate="show" variants={fadeIn} className="mb-10">
          <SearchBar onSearch={handleSearch} />
        </motion.div>

        {/* Loading skeletons */}
        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {[...Array(10)].map((_, i) => (
              <LoadingSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeIn}
            className="mt-2 p-4 rounded-xl glass text-red-300 border border-red-400/10 text-sm"
          >
            {error}
          </motion.div>
        )}

        {/* Result header */}
        <AnimatePresence>
          {hasResults && (
            <motion.div
              key="result-header"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="mb-5"
            >
              <p className="text-sm text-slate-400">
                <span className="text-slate-500">Because you watched</span>{" "}
                <span className="text-slate-200 font-medium">{matched || query}</span>
                <span className="ml-2 text-slate-600">· {movies.length} picks</span>
              </p>
              {matched && matched.toLowerCase() !== query.toLowerCase() && (
                <p className="mt-1 text-xs text-slate-500">
                  Matched &ldquo;{matched}&rdquo; for your search
                </p>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Movie grid */}
        {hasResults && (
          <motion.div
            key={query}
            variants={gridVariants}
            initial="hidden"
            animate="show"
            className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
          >
            {movies.map((m) => (
              <motion.div key={m.tmdb_id ?? m.title} variants={cardVariants}>
                <MovieCard
                  title={m.title}
                  poster={m.poster}
                  vote_average={m.vote_average}
                  release_date={m.release_date}
                />
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Empty state */}
        <AnimatePresence>
          {isEmpty && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="mt-4 text-center"
            >
              <p className="text-sm text-slate-500 mb-5">Not sure where to start?</p>
              <div className="flex flex-wrap justify-center gap-2.5">
                {FEATURED.map((film) => (
                  <button
                    key={film}
                    onClick={() => handleSearch(film)}
                    className="px-4 py-2 rounded-full glass text-sm text-slate-300 hover:text-white hover:border-slate-500 border border-white/10 transition-all active:scale-95"
                  >
                    {film}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* No results (searched but nothing found) */}
        {!loading && query && movies.length === 0 && !error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 text-center text-slate-500 text-sm"
          >
            No results for &ldquo;{query}&rdquo; &mdash; try a different title.
          </motion.p>
        )}
      </div>
    </main>
  );
}

function ClapperIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-indigo-400 shrink-0"
    >
      <path d="M4 11v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8H4Z" />
      <path d="m4 11-.88-2.87a2 2 0 0 1 1.33-2.5l11.48-3.5a2 2 0 0 1 2.5 1.32l.87 2.87L4 11Z" />
      <path d="m6.6 4.99 3.38 4.2" />
      <path d="m11.86 3.38 3.38 4.2" />
    </svg>
  );
}
