import "./globals.css";

export const metadata = {
  title: "Movie Recommender",
  description: "Tired of always asking 'What movie should I watch?' Get clean, cinematic recommendations with a sleek, modern feel.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 text-slate-900 dark:text-slate-100">
        {children}
      </body>
    </html>
  );
}
