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
    console.log("Backend response:", data);

    // Ensure valid shape
    if (Array.isArray(data.recommendations)) {
      return data.recommendations;
    } else if (data.recommendations && typeof data.recommendations === "object") {
      return Object.values(data.recommendations);
    } else {
      throw new Error("Invalid data format from backend");
    }
  } catch (err) {
    console.error("Fetch failed:", err);
    throw err;
  }
}
