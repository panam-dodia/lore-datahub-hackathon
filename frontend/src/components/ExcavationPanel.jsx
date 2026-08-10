import { CheckCircle2, Loader2 } from "lucide-react";

export default function ExcavationPanel({ messages, done }) {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-5 font-mono text-sm space-y-2">
      {messages.map((message, i) => {
        const isLast = i === messages.length - 1;
        const isFinal = isLast && done;
        return (
          <div key={i} className="flex items-start gap-2 text-gray-300">
            {isFinal || !isLast ? (
              <CheckCircle2 className="w-4 h-4 text-brand mt-0.5 shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 text-gray-500 mt-0.5 shrink-0 animate-spin" />
            )}
            <span>{message}</span>
          </div>
        );
      })}
      {messages.length === 0 && (
        <p className="text-gray-500">Waiting for excavation to start...</p>
      )}
    </div>
  );
}
