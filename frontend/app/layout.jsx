import "./globals.css";

export const metadata = {
  title: "Movie Recommender",
  description: "Clean modern UI for a Django movie recommender",
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
