import ConfidenceBadge from "./ConfidenceBadge.jsx";
import EvidenceLink from "./EvidenceLink.jsx";

export default function KnowledgeCard({ knowledge }) {
  return (
    <div className="rounded-lg border border-gray-800 border-l-2 border-l-brand/50 bg-gray-900 p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-serif font-semibold text-gray-100 break-all">{knowledge.asset_name}</h3>
          <p className="text-sm text-gray-400">
            {knowledge.evidence?.length ?? 0} evidence sources
          </p>
        </div>
        <ConfidenceBadge level={knowledge.confidence_level} score={knowledge.confidence} />
      </div>

      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
          Why It Exists
        </h4>
        <p className="text-sm text-gray-300">{knowledge.why_it_exists}</p>
      </div>

      {knowledge.known_quirks && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
            Known Quirks
          </h4>
          <p className="text-sm text-gray-300">{knowledge.known_quirks}</p>
        </div>
      )}

      {knowledge.business_context && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
            Business Context
          </h4>
          <p className="text-sm text-gray-300">{knowledge.business_context}</p>
        </div>
      )}

      {knowledge.evidence?.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
            Evidence
          </h4>
          <div className="flex flex-wrap gap-2">
            {knowledge.evidence.map((e, i) => (
              <EvidenceLink key={i} evidence={e} />
            ))}
          </div>
        </div>
      )}

      {knowledge.knowledge_authors?.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
            Knowledge Authors
          </h4>
          <p className="text-sm text-gray-400">{knowledge.knowledge_authors.join(" · ")}</p>
        </div>
      )}
    </div>
  );
}
