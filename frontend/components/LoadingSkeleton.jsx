export default function LoadingSkeleton() {
  return (
    <div className="p-4 rounded-2xl bg-white/30 dark:bg-slate-700/30 border border-slate-100/40 dark:border-slate-700/50">
      <div className="h-40 rounded-lg skeleton" />
      <div className="mt-3 space-y-2">
        <div className="h-4 w-3/4 rounded-md skeleton" />
        <div className="h-3 w-1/2 rounded-md skeleton" />
      </div>
    </div>
  );
}
