import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Movie Recommender",
  description:
    "Tired of always asking 'What movie should I watch?' Get clean, cinematic recommendations with a sleek, modern feel.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#0B0F17] text-slate-100">
        {children}
      </body>
    </html>
  );
}
