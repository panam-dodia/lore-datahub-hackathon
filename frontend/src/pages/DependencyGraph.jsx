import { Search, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { getDependencyGraph, searchAssets } from "../api/client.js";
import LoadingBar from "../components/LoadingBar.jsx";
import { layoutGraph } from "../utils/graphLayout.js";

const NODE_STYLE = {
  background: "#251f1a",
  border: "1px solid #6f5f4d",
  borderRadius: 8,
  color: "#f7f3ec",
  fontSize: 14,
  fontWeight: 500,
  padding: 10,
  whiteSpace: "pre-line",
};

export default function DependencyGraph() {
  const navigate = useNavigate();
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);

  useEffect(() => {
    getDependencyGraph()
      .then(setGraph)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const { nodes, edges } = useMemo(() => {
    if (!graph) return { nodes: [], edges: [] };

    const rfNodes = graph.nodes.map((n) => ({
      id: n.urn,
      data: { label: `${n.name}\n${n.platform}` },
      position: { x: 0, y: 0 },
      style: NODE_STYLE,
    }));

    const rfEdges = graph.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      style: { stroke: "#6b5d4d" },
    }));

    return { nodes: layoutGraph(rfNodes, rfEdges), edges: rfEdges };
  }, [graph]);

  const runSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setSearchResults(null);
      setSearchError(null);
      return;
    }
    setSearching(true);
    setSearchError(null);
    try {
      setSearchResults(await searchAssets(query));
    } catch {
      setSearchError("Search is unavailable — the MCP bridge may not be set up (see README).");
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-serif font-semibold text-gray-50">Dependency Graph</h1>
        <p className="text-sm text-gray-400 mt-1">
          Every asset in your DataHub instance and how they connect. Click any node for its full
          picture: connections, evidence already found, and gaps.
        </p>
      </div>

      <form onSubmit={runSearch} className="space-y-2">
        <div className="flex gap-2 max-w-lg">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search assets — e.g. warehouse, customer analytics..."
              className="w-full bg-gray-900 border border-gray-800 rounded pl-9 pr-3 py-1.5 text-sm text-gray-200 placeholder:text-gray-500 focus:outline-none focus:border-brand/50"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="flex items-center gap-1.5 rounded border border-brand/40 bg-brand/10 hover:bg-brand/20 disabled:opacity-50 text-brand text-sm px-3 py-1.5 font-medium transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" strokeWidth={2} />
            {searching ? "Searching..." : "Search via MCP"}
          </button>
        </div>

        {searchError && <p className="text-sm text-critical">{searchError}</p>}

        {searchResults && (
          <div className="max-w-lg rounded-lg border border-gray-800 bg-gray-900 divide-y divide-gray-800">
            {searchResults.length === 0 && (
              <p className="text-sm text-gray-500 p-3">No matches found.</p>
            )}
            {searchResults.map((r) => (
              <button
                key={r.urn}
                onClick={() => navigate(`/asset/${encodeURIComponent(r.urn)}`)}
                className="w-full text-left p-3 hover:bg-gray-800 transition-colors"
              >
                <p className="text-sm text-gray-200">{r.name}</p>
                <p className="text-xs text-gray-500 break-all">{r.urn}</p>
              </button>
            ))}
          </div>
        )}
      </form>

      {loading && (
        <LoadingBar label="Loading dependency graph — this also gathers GitHub evidence for every asset up front, so clicking a node afterward is instant..." />
      )}
      {error && <p className="text-sm text-critical">Failed to load: {error}</p>}

      {!loading && !error && (
        <div className="h-[75vh] rounded-lg border border-gray-800 bg-gray-950 overflow-hidden relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodeClick={(_, node) => navigate(`/asset/${encodeURIComponent(node.id)}`)}
            fitView
          >
            <Background color="#3a322b" gap={24} />
            <Controls />
          </ReactFlow>
        </div>
      )}
    </div>
  );
}
