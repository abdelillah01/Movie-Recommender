// components/BackgroundFX.jsx
"use client";

export default function BackgroundFX() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10">
      <div className="absolute inset-0 bg-cinema" />
      <div className="absolute inset-0 vignette" />
      <div className="absolute inset-0 grain opacity-[0.06]" />
    </div>
  );
}
