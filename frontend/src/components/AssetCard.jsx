import { Flame, Network, ShieldCheck, Search, TriangleAlert } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const RISK_META = {
  CRITICAL: { border: "border-critical/50", icon: Flame, iconColor: "text-critical" },
  AT_RISK: { border: "border-atrisk/50", icon: TriangleAlert, iconColor: "text-atrisk" },
  SAFE: { border: "border-safe/50", icon: ShieldCheck, iconColor: "text-safe" },
};

export default function AssetCard({ asset }) {
  const navigate = useNavigate();
  const { border, icon: RiskIcon, iconColor } = RISK_META[asset.risk_level];

  return (
    <div className={`rounded-lg border bg-gray-900 p-4 space-y-3 ${border}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <RiskIcon className={`w-4 h-4 mt-0.5 shrink-0 ${iconColor}`} strokeWidth={1.75} />
          <div>
            <h3 className="font-medium text-gray-100 break-all">{asset.asset_name}</h3>
            <p className="text-sm text-gray-400">
              {asset.platform} · {asset.asset_type}
            </p>
          </div>
        </div>
        <span
          className={`shrink-0 text-xs font-mono px-1.5 py-0.5 rounded border ${border} ${iconColor}`}
          title="Risk score (0-1): weighs downstream impact, missing docs, and ownership concentration"
        >
          {asset.risk_score.toFixed(2)}
        </span>
      </div>

      <div className="text-sm text-gray-400 space-y-1">
        <Link
          to={`/asset/${encodeURIComponent(asset.asset_urn)}`}
          className="inline-block hover:text-brand-light hover:underline underline-offset-2"
        >
          {asset.downstream_consumer_count} downstream consumers
        </Link>
        <div className="w-full bg-gray-800 rounded-full h-1.5">
          <div
            className="bg-brand/70 h-1.5 rounded-full"
            style={{ width: `${asset.documentation_coverage * 100}%` }}
          />
        </div>
        <p className="text-sm text-gray-400">
          {Math.round(asset.documentation_coverage * 100)}% documented
          {asset.last_owner_activity_days > 0 &&
            ` · owner inactive ${asset.last_owner_activity_days}d`}
        </p>
      </div>

      {asset.risk_reasons?.length > 0 && (
        <ul className="text-sm text-gray-400 list-disc list-inside space-y-0.5">
          {asset.risk_reasons.map((reason, i) => (
            <li key={i}>{reason}</li>
          ))}
        </ul>
      )}

      <div className="flex gap-2">
        <Link
          to={`/asset/${encodeURIComponent(asset.asset_urn)}`}
          className="flex-1 flex items-center justify-center gap-1.5 rounded border border-gray-700 hover:border-gray-600 text-gray-300 text-sm py-1.5 font-medium transition-colors"
        >
          <Network className="w-3.5 h-3.5" strokeWidth={2} />
          View Detail
        </Link>
        <button
          onClick={() =>
            navigate(`/excavate/${encodeURIComponent(asset.asset_urn)}`, {
              state: { assetName: asset.asset_name, riskAsset: asset },
            })
          }
          title="Search GitHub + AI to explain why this exists"
          className="flex-1 flex items-center justify-center gap-1.5 rounded border border-brand/40 bg-brand/10 hover:bg-brand/20 text-brand text-sm py-1.5 font-medium transition-colors"
        >
          <Search className="w-3.5 h-3.5" strokeWidth={2} />
          Excavate
        </button>
      </div>
    </div>
  );
}
