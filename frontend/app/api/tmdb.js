import axios from "axios";

const TMDB_API_KEY = process.env.NEXT_PUBLIC_TMDB_API_KEY;
const TMDB_BASE_URL = process.env.NEXT_PUBLIC_TMDB_BASE_URL || "https://api.themoviedb.org/3";
const TMDB_IMAGE_URL = process.env.NEXT_PUBLIC_TMDB_IMAGE_URL || "https://image.tmdb.org/t/p/w500";

export async function fetchMovieDetails(title) {
  try {
    const response = await axios.get(`${TMDB_BASE_URL}/search/movie`, {
      params: {
        api_key: TMDB_API_KEY,
        query: title,
      },
    });

    const movie = response.data.results[0];
    if (!movie) return null;

    return {
      title: movie.title,
      overview: movie.overview,
      poster: movie.poster_path ? `${TMDB_IMAGE_URL}${movie.poster_path}` : null,
      release_date: movie.release_date,
    };
  } catch (error) {
    console.error("Error fetching movie details:", error);
    return null;
  }
}
