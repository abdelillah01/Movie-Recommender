export default function LoadingSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden border border-white/10 bg-white/[0.03]">
      <div className="relative w-full aspect-[2/3] skeleton">
        <div className="absolute inset-x-0 bottom-0 p-4 space-y-1.5">
          <div className="h-4 w-3/4 rounded bg-white/10" />
          <div className="h-3 w-1/3 rounded bg-white/10" />
        </div>
      </div>
    </div>
  );
}
