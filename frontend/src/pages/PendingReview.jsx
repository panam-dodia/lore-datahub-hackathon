import { Check, X } from "lucide-react";
import { useEffect, useState } from "react";
import { approvePendingReview, getPendingReview, rejectPendingReview } from "../api/client.js";
import KnowledgeCard from "../components/KnowledgeCard.jsx";
import LoadingBar from "../components/LoadingBar.jsx";

export default function PendingReview() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyUrn, setBusyUrn] = useState(null);

  const load = () => {
    setLoading(true);
    getPendingReview()
      .then(setEntries)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handle = async (action, urn) => {
    setBusyUrn(urn);
    await action(urn);
    await load();
    setBusyUrn(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-serif font-semibold text-gray-50">Pending Review</h1>
        <p className="text-sm text-gray-400 mt-1">
          MEDIUM-confidence explanations Lore found but isn't sure enough about to write back
          automatically. Approve to publish to DataHub, or reject to discard.
        </p>
      </div>

      {loading && <LoadingBar label="Loading pending review queue..." />}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {entries.map((knowledge) => (
            <div key={knowledge.asset_urn} className="space-y-2">
              <KnowledgeCard knowledge={knowledge} />
              <div className="flex gap-2">
                <button
                  disabled={busyUrn === knowledge.asset_urn}
                  onClick={() => handle(approvePendingReview, knowledge.asset_urn)}
                  className="flex-1 flex items-center justify-center gap-1.5 rounded border border-safe/40 bg-safe/10 hover:bg-safe/20 disabled:opacity-50 text-safe text-sm py-1.5 font-medium transition-colors"
                >
                  <Check className="w-3.5 h-3.5" strokeWidth={2} />
                  Approve
                </button>
                <button
                  disabled={busyUrn === knowledge.asset_urn}
                  onClick={() => handle(rejectPendingReview, knowledge.asset_urn)}
                  className="flex-1 flex items-center justify-center gap-1.5 rounded border border-critical/40 bg-critical/10 hover:bg-critical/20 disabled:opacity-50 text-critical text-sm py-1.5 font-medium transition-colors"
                >
                  <X className="w-3.5 h-3.5" strokeWidth={2} />
                  Reject
                </button>
              </div>
            </div>
          ))}
          {entries.length === 0 && (
            <p className="text-sm text-gray-500">Nothing pending review right now.</p>
          )}
        </div>
      )}
    </div>
  );
}
