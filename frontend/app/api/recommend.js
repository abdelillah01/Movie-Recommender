import axios from "axios";

/**
 * recommendMovies(title)
 * Uses Axios to POST to your Django backend.
 * Returns an array of recommendations (strings or objects).
 */
export default async function recommendMovies(title) {
  if (!title) return [];
  try {
    console.log("[frontend] sending:", title);
    const res = await axios.post("http://127.0.0.1:8000/api/recommend/", { title }, {
      headers: { "Content-Type": "application/json" },
      timeout: 10000,
    });
    console.log("[frontend] response:", res.data);
    return res.data.recommendations || [];
  } catch (err) {
    // Rethrow so page.jsx can show an error message
    console.error("API call failed:", err);
    throw err;
  }
}
