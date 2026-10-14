export interface Movie {
  title: string;
  poster: string | null;
  release_date: string | null;
  vote_average: number | null;
  tmdb_id: number | null;
}

export interface RecommendResponse {
  matched: string;
  query?: string;
  recommendations: Movie[];
}

export default async function recommendMovies(title: string): Promise<RecommendResponse> {
  if (!title) return { matched: "", recommendations: [] };

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const response = await fetch(`${apiBase}/api/v1/recommend/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    const text = await response.text();
    console.error("Backend error:", response.status, text);
    throw new Error(`Backend returned ${response.status}`);
  }

  const data: RecommendResponse = await response.json();

  const recs = Array.isArray(data.recommendations)
    ? data.recommendations
    : data.recommendations && typeof data.recommendations === "object"
      ? (Object.values(data.recommendations) as Movie[])
      : null;

  if (!recs) throw new Error("Invalid data format from backend");

  return { matched: data.matched, query: data.query, recommendations: recs };
}
