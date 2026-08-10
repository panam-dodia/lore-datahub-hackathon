const STYLES = {
  HIGH: "bg-brand/15 text-brand-light border-brand/40",
  MEDIUM: "bg-atrisk/15 text-atrisk border-atrisk/40",
  LOW: "bg-gray-800 text-gray-400 border-gray-700",
};

export default function ConfidenceBadge({ level, score }) {
  const style = STYLES[level] || STYLES.LOW;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${style}`}>
      ● {level} {typeof score === "number" ? `${Math.round(score * 100)}%` : ""}
    </span>
  );
}
