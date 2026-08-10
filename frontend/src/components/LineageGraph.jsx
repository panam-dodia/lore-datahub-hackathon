import { ArrowRight } from "lucide-react";

function NodeCard({ node, highlight }) {
  return (
    <div
      className={`rounded-lg border px-3 py-2 text-sm ${
        highlight
          ? "border-brand bg-brand/10 text-gray-50 font-medium"
          : "border-gray-800 bg-gray-900 text-gray-300"
      }`}
    >
      <p className="break-all">{node.name}</p>
      <p className="text-sm text-gray-400">{node.platform}</p>
    </div>
  );
}

function NodeStack({ nodes, emptyText }) {
  return (
    <div className="flex-1 min-w-0 space-y-2">
      {nodes.map((node) => (
        <NodeCard key={node.urn} node={node} />
      ))}
      {nodes.length === 0 && <p className="text-sm text-gray-500">{emptyText}</p>}
    </div>
  );
}

export default function LineageGraph({ lineage }) {
  const thisNode = { name: lineage.asset_name, platform: lineage.platform, urn: lineage.asset_urn };

  return (
    <div className="space-y-3">
      {/* Header row — fixed at the top regardless of how many boxes each column has */}
      <div className="flex items-start gap-3">
        <h3 className="flex-1 min-w-0 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Upstream — feeds this ({lineage.upstream.length})
        </h3>
        <span className="w-4 shrink-0" />
        <h3 className="flex-1 min-w-0 text-xs font-semibold uppercase tracking-wide text-gray-400">
          This Asset
        </h3>
        <span className="w-4 shrink-0" />
        <h3 className="flex-1 min-w-0 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Downstream — depends on this ({lineage.downstream.length})
        </h3>
      </div>

      {/* Content row — boxes vertically centered relative to the tallest column */}
      <div className="flex items-center gap-3">
        <NodeStack nodes={lineage.upstream} emptyText="Nothing feeds into this asset." />
        <ArrowRight className="w-4 h-4 text-gray-700 shrink-0" />
        <div className="flex-1 min-w-0">
          <NodeCard node={thisNode} highlight />
        </div>
        <ArrowRight className="w-4 h-4 text-gray-700 shrink-0" />
        <NodeStack nodes={lineage.downstream} emptyText="Nothing depends on this asset." />
      </div>
    </div>
  );
}
