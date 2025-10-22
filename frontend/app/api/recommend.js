import axios from "axios";

export default async function recommendMovies(title) {
  console.log("📤 Sending request to Django with title:", title);

  try {
    const response = await axios.post(
      "http://127.0.0.1:8000/api/recommend/",
      { title },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    console.log("✅ Django API response:", response.data);
    return response.data.recommendations;
  } catch (error) {
    console.error("❌ Error fetching recommendations:", error);
    if (error.response) {
      console.error("Server responded with:", error.response.data);
    }
    throw error;
  }
}
