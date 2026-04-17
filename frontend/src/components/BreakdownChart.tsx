"use client";

import { motion } from "framer-motion";
import type { CredibilityBreakdown } from "@/lib/api";

interface BreakdownChartProps {
  breakdown: CredibilityBreakdown;
}

const labels: Record<keyof CredibilityBreakdown, { label: string; icon: string }> = {
  ai_generation_score: { label: "AI Generation", icon: "🤖" },
  web_search_score: { label: "Web Search", icon: "🌐" },
  fact_evidence_score: { label: "Fact Evidence", icon: "📄" },
  source_credibility_score: { label: "Source Trust", icon: "🏛" },
  misinfo_pattern_score: { label: "Misinfo Pattern", icon: "🔍" },
  emotional_language_score: { label: "Emotional Tone", icon: "💬" },
  google_factcheck_score: { label: "Google Fact Check", icon: "✅" },
};

const barColor = (key: string, value: number): string => {
  const isPositive =
    key === "web_search_score" ||
    key === "fact_evidence_score" ||
    key === "source_credibility_score" ||
    key === "google_factcheck_score";
  if (isPositive) {
    return value >= 0.6 ? "bg-satya-500" : value >= 0.3 ? "bg-amber-400" : "bg-red-400";
  }
  return value <= 0.3 ? "bg-satya-500" : value <= 0.6 ? "bg-amber-400" : "bg-red-400";
};

const barGlow = (key: string, value: number): string => {
  const isPositive =
    key === "web_search_score" ||
    key === "fact_evidence_score" ||
    key === "source_credibility_score" ||
    key === "google_factcheck_score";
  if (isPositive) {
    return value >= 0.6
      ? "shadow-[0_0_12px_rgba(34,197,94,0.3)]"
      : value >= 0.3
        ? "shadow-[0_0_12px_rgba(251,191,36,0.2)]"
        : "shadow-[0_0_12px_rgba(248,113,113,0.2)]";
  }
  return value <= 0.3
    ? "shadow-[0_0_12px_rgba(34,197,94,0.3)]"
    : value <= 0.6
      ? "shadow-[0_0_12px_rgba(251,191,36,0.2)]"
      : "shadow-[0_0_12px_rgba(248,113,113,0.2)]";
};

export default function BreakdownChart({ breakdown }: BreakdownChartProps) {
  const entries = Object.entries(breakdown) as [keyof CredibilityBreakdown, number][];

  return (
    <div className="space-y-4">
      <h3 className="text-[11px] font-bold uppercase tracking-[0.15em] text-gray-500">
        Signal Breakdown
      </h3>
      {entries.map(([key, value], i) => (
        // Guard against future backend fields not yet mapped in labels.
        // Keeps UI stable instead of crashing.
        (() => {
          const labelMeta = labels[key] ?? {
            label: key.replace(/_/g, " "),
            icon: "•",
          };
          return (
        <motion.div
          key={key}
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-1.5"
        >
          <div className="flex items-center justify-between text-[13px]">
            <span className="flex items-center gap-2 text-gray-400">
              <span className="text-xs">{labelMeta.icon}</span>
              {labelMeta.label}
            </span>
            <span className="font-mono text-xs font-semibold text-gray-500">
              {(value * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.04]">
            <motion.div
              className={`h-full rounded-full ${barColor(key, value)} ${barGlow(key, value)}`}
              initial={{ width: 0 }}
              animate={{ width: `${value * 100}%` }}
              transition={{ duration: 1, delay: 0.3 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
        </motion.div>
          );
        })()
      ))}
    </div>
  );
}
