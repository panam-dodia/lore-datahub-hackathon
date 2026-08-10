export default function LoadingBar({ label }) {
  return (
    <div className="space-y-2">
      {label && <p className="text-sm text-gray-400">{label}</p>}
      <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full w-1/4 bg-brand rounded-full animate-loading-slide" />
      </div>
    </div>
  );
}
