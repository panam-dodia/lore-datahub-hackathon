import AssetCard from "./AssetCard.jsx";

const COLUMNS = [
  { level: "CRITICAL", title: "Critical", dot: "bg-critical", hint: "score ≥ 0.80" },
  { level: "AT_RISK", title: "At Risk", dot: "bg-atrisk", hint: "score ≥ 0.50" },
  { level: "SAFE", title: "Safe", dot: "bg-safe", hint: "score < 0.50" },
];

export default function RiskDashboard({ assets }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {COLUMNS.map((col) => {
        const columnAssets = assets.filter((a) => a.risk_level === col.level);
        return (
          <div key={col.level} className="space-y-3">
            <h2 className="flex items-baseline gap-2 text-sm font-semibold text-gray-300">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${col.dot}`} />
                {col.title} ({columnAssets.length})
              </span>
              <span className="text-xs font-normal text-gray-400">{col.hint}</span>
            </h2>
            <div className="space-y-3 max-h-[75vh] overflow-y-auto pr-1">
              {columnAssets.map((asset) => (
                <AssetCard key={asset.asset_urn} asset={asset} />
              ))}
              {columnAssets.length === 0 && (
                <p className="text-sm text-gray-500">No assets in this tier.</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
