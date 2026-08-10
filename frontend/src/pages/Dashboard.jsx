import { useEffect, useState } from "react";
import { getRiskDashboard } from "../api/client.js";
import HowItWorks from "../components/HowItWorks.jsx";
import LoadingBar from "../components/LoadingBar.jsx";
import RiskDashboard from "../components/RiskDashboard.jsx";

export default function Dashboard() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  useEffect(() => {
    getRiskDashboard()
      .then(setAssets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-serif font-semibold text-gray-50">
          Knowledge at Risk
          <button
            onClick={() => setShowInfo((v) => !v)}
            className="text-gray-400 hover:text-brand transition-colors"
          >
            ?
          </button>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Computed live from your DataHub instance's lineage, ownership, and
          documentation — no external search involved yet.
        </p>
      </div>

      {showInfo && (
        <div className="space-y-3">
          <p className="text-sm text-gray-400 max-w-2xl">
            Each score weighs how many things depend on the asset (from
            DataHub's lineage graph), whether it's documented (DataHub's
            description field), and whether one person is the only registered
            owner. This score is known immediately for every asset — nothing
            here required searching GitHub.{" "}
            <span className="text-gray-300">Excavate</span> is a separate,
            on-demand step: click it on any card to have Lore search GitHub
            and synthesize an explanation for <em>why</em> that risk exists.
            It can come back with a confident answer, a partial one, or
            nothing at all — but the risk score above doesn't change either
            way, since it isn't based on what Excavate finds.
          </p>
          <HowItWorks />
        </div>
      )}

      {loading && <LoadingBar label="Loading risk dashboard..." />}
      {error && <p className="text-sm text-critical">Failed to load: {error}</p>}
      {!loading && !error && <RiskDashboard assets={assets} />}
    </div>
  );
}
