import { useEffect, useState } from "react";
import { getAllKnowledge } from "../api/client.js";
import KnowledgeCard from "../components/KnowledgeCard.jsx";
import LoadingBar from "../components/LoadingBar.jsx";

export default function Knowledge() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllKnowledge()
      .then(setEntries)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-serif font-semibold text-gray-50">
          Knowledge Written to DataHub
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          {entries.length} knowledge unit{entries.length === 1 ? "" : "s"} preserved so far.
          Only HIGH-confidence findings are written back automatically, so
          everything below is HIGH confidence by definition.
        </p>
      </div>

      {loading && <LoadingBar label="Loading knowledge..." />}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {entries.map((knowledge) => (
            <KnowledgeCard key={knowledge.asset_urn} knowledge={knowledge} />
          ))}
          {entries.length === 0 && (
            <p className="text-sm text-gray-500">No knowledge written back yet.</p>
          )}
        </div>
      )}
    </div>
  );
}
