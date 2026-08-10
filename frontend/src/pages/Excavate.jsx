import { ArrowLeft, Search, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { getExcavationJob, startExcavation } from "../api/client.js";
import ExcavationPanel from "../components/ExcavationPanel.jsx";
import KnowledgeCard from "../components/KnowledgeCard.jsx";
import { useWebSocket } from "../hooks/useWebSocket.jsx";

export default function Excavate() {
  const { assetUrn } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const riskAsset = location.state?.riskAsset;
  const assetName = location.state?.assetName || decodeURIComponent(assetUrn);

  const [jobId, setJobId] = useState(null);
  const [result, setResult] = useState(null);
  const { messages, done } = useWebSocket(jobId);

  useEffect(() => {
    startExcavation(decodeURIComponent(assetUrn), assetName).then(({ job_id }) =>
      setJobId(job_id)
    );
  }, [assetUrn]);

  useEffect(() => {
    if (!done || !jobId) return;
    getExcavationJob(jobId).then((job) => setResult(job.result));
  }, [done, jobId]);

  return (
    <div className="space-y-6 max-w-3xl">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-300"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Back
      </button>

      <div>
        <h1 className="text-xl font-serif font-semibold text-gray-50 flex items-center gap-2">
          <Search className="w-5 h-5 text-brand" strokeWidth={1.75} />
          Excavating {assetName}
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Searching GitHub history and DataHub lineage to explain why this asset was flagged.
        </p>
      </div>

      {riskAsset && (
        <div className="rounded-lg border border-atrisk/30 bg-atrisk/5 p-4 space-y-1">
          <p className="flex items-center gap-2 text-sm font-medium text-atrisk">
            <TriangleAlert className="w-4 h-4" strokeWidth={2} />
            Why this was flagged (risk score {riskAsset.risk_score.toFixed(2)}, from DataHub — unrelated to what's found below)
          </p>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-0.5">
            {riskAsset.risk_reasons.map((reason, i) => (
              <li key={i}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      <ExcavationPanel messages={messages} done={done} />

      {result && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold text-gray-300">
            What Lore Found While Explaining Why
          </h2>
          <p className="text-sm text-gray-400">
            The confidence badge below reflects how much evidence Lore found
            for this explanation — it isn't a re-assessment of the risk
            above, which stays the same either way.
          </p>
          <KnowledgeCard knowledge={result} />
        </div>
      )}
    </div>
  );
}
