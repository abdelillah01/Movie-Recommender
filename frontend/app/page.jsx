"use client";

import { useState } from "react";
import SearchBar from "../components/SearchBar";
import MovieCard from "../components/MovieCard";
import recommendMovies from "./api/recommend";

export default function Home() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (title) => {
    setLoading(true);
    setError("");
    setMovies([]);

    try {
      const results = await recommendMovies(title);
      console.log("🎥 Recommendations received:", results);
      setMovies(results || []);
    } catch (err) {
      console.error("❌ Fetch failed:", err);
      setError("Failed to fetch recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-6 text-blue-600">🎬 Movie Recommender</h1>
      <SearchBar onSearch={handleSearch} />

      {loading && <p className="mt-4 text-gray-600">Loading recommendations...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      {movies.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-6">
          {movies.map((movie, index) => (
            <MovieCard key={index} title={movie} />
          ))}
        </div>
      )}

      {!loading && movies.length === 0 && !error && (
        <p className="mt-6 text-gray-500">Enter a movie title to get recommendations 🎞️</p>
      )}
    </main>
  );
}
