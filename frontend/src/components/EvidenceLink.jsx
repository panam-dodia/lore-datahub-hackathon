const LABELS = {
  pr_comment: "PR",
  commit_message: "Commit",
  code_comment: "Code comment",
  lineage_pattern: "Lineage signal",
  git_blame: "Git blame",
};

export default function EvidenceLink({ evidence }) {
  const label = LABELS[evidence.type] || evidence.type;

  const content = (
    <span className="inline-flex items-center rounded border border-gray-700 bg-gray-800 px-2 py-0.5 text-xs text-gray-300 hover:border-gray-500">
      {label}
    </span>
  );

  if (!evidence.url) return content;

  return (
    <a href={evidence.url} target="_blank" rel="noreferrer" title={evidence.raw_excerpt}>
      {content}
    </a>
  );
}
