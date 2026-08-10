import { BookOpen, Search, Sparkles } from "lucide-react";

const STEPS = [
  {
    icon: Search,
    title: "1. Mine",
    desc: "Scans git history and DataHub's own lineage graph for clues about why an asset exists.",
  },
  {
    icon: Sparkles,
    title: "2. Synthesize",
    desc: "An LLM cross-references every clue into a plain-language explanation, quirks, and business context.",
  },
  {
    icon: BookOpen,
    title: "3. Preserve",
    desc: "High-confidence findings are written back into DataHub as real, evidence-linked documentation.",
  },
];

export default function HowItWorks() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 rounded-lg border border-gray-800 bg-gray-900/60 p-4">
      {STEPS.map(({ icon: Icon, title, desc }) => (
        <div key={title} className="flex gap-3">
          <Icon className="w-5 h-5 text-brand shrink-0 mt-0.5" strokeWidth={1.75} />
          <div>
            <h3 className="text-sm font-medium text-gray-200">{title}</h3>
            <p className="text-sm text-gray-400 mt-0.5">{desc}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
