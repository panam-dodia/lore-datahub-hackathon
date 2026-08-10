import { ArrowLeft, CircleAlert, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getAssetDetail } from "../api/client.js";
import EvidenceLink from "../components/EvidenceLink.jsx";
import LineageGraph from "../components/LineageGraph.jsx";
import LoadingBar from "../components/LoadingBar.jsx";

const RISK_STYLES = {
  CRITICAL: "text-critical border-critical/40 bg-critical/10",
  AT_RISK: "text-atrisk border-atrisk/40 bg-atrisk/10",
  SAFE: "text-safe border-safe/40 bg-safe/10",
};

function recommendationFor(reason) {
  if (reason.includes("No documentation")) {
    return "Should be documented — add a description to this asset in DataHub.";
  }
  if (reason.includes("No registered owner")) {
    return "Should have an owner — assign one in DataHub's ownership settings.";
  }
  if (reason.includes("Single owner")) {
    return "Should have a backup — register a second owner for redundancy.";
  }
  return reason;
}

export default function AssetDetail() {
  const { assetUrn } = useParams();
  const navigate = useNavigate();
  const decodedUrn = decodeURIComponent(assetUrn);

  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    getAssetDetail(decodedUrn)
      .then(setDetail)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [assetUrn]);

  return (
    <div className="space-y-6 max-w-3xl">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-300"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Back to Dependency Graph
      </Link>

      {loading && <LoadingBar label="Loading asset detail..." />}
      {error && <p className="text-sm text-critical">Failed to load: {error}</p>}

      {detail && (
        <>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h1 className="text-xl font-serif font-semibold text-gray-50 break-all">
                {detail.asset_name}
              </h1>
              <p className="text-sm text-gray-400 mt-1">{detail.platform} · TABLE</p>
            </div>
            <span
              className={`shrink-0 text-sm font-mono px-2 py-1 rounded border ${RISK_STYLES[detail.risk.risk_level]}`}
            >
              {detail.risk.risk_level} · {detail.risk.risk_score.toFixed(2)}
            </span>
          </div>

          <section className="space-y-2">
            <h2 className="text-sm font-semibold text-gray-300">Connections</h2>
            <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4 overflow-x-auto">
              <LineageGraph lineage={detail} />
            </div>
          </section>

          <section className="space-y-2">
            <h2 className="text-sm font-semibold text-gray-300">
              Where It's Mentioned ({detail.evidence.length})
            </h2>
            {detail.evidence.length > 0 ? (
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-4 space-y-3">
                {detail.evidence.map((e, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <EvidenceLink evidence={e} />
                    <p className="text-sm text-gray-400 flex-1">{e.raw_excerpt}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                Nothing found in the connected GitHub repo mentioning this asset by name.
              </p>
            )}
          </section>

          <section className="space-y-2">
            <h2 className="text-sm font-semibold text-gray-300">
              Gaps — Where It's Not Mentioned, and Where It Should Be
            </h2>
            {detail.risk.risk_reasons.length > 0 ? (
              <ul className="rounded-lg border border-gray-800 bg-gray-900 p-4 space-y-2">
                {detail.risk.risk_reasons.map((reason, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <CircleAlert className="w-4 h-4 text-atrisk shrink-0 mt-0.5" strokeWidth={1.75} />
                    {recommendationFor(reason)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No gaps found — this asset is in good shape.</p>
            )}
          </section>

          <button
            onClick={() =>
              navigate(`/excavate/${encodeURIComponent(decodedUrn)}`, {
                state: { assetName: detail.asset_name, riskAsset: detail.risk },
              })
            }
            className="flex items-center gap-1.5 rounded border border-brand/40 bg-brand/10 hover:bg-brand/20 text-brand text-sm py-1.5 px-3 font-medium transition-colors"
          >
            <Search className="w-3.5 h-3.5" strokeWidth={2} />
            Write a full AI explanation (Excavate)
          </button>
        </>
      )}
    </div>
  );
}
