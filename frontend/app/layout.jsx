import "./globals.css";

export const metadata = {
  title: "Movie Recommender",
  description: "AI-powered movie recommendations",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
