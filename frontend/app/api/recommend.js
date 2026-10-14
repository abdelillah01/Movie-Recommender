export default async function recommendMovies(title) {
  if (!title) return [];

  try {
    const response = await fetch("http://127.0.0.1:8000/api/recommend/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Backend error:", response.status, text);
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();

    const recs = Array.isArray(data.recommendations)
      ? data.recommendations
      : data.recommendations && typeof data.recommendations === "object"
        ? Object.values(data.recommendations)
        : null;

    if (!recs) throw new Error("Invalid data format from backend");

    return { matched: data.matched || null, recommendations: recs };
  } catch (err) {
    console.error("Fetch failed:", err);
    throw err;
  }
}
