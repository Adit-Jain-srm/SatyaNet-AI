"use client";

import { motion } from "framer-motion";
import type { QdrantStats } from "@/lib/api";

interface QdrantInsightProps {
  stats: QdrantStats[];
}

const COLLECTION_META: Record<string, { label: string; accent: string }> = {
  verified_facts: { label: "Verified Facts", accent: "text-satya-400" },
  misinfo_patterns: { label: "Misinfo Patterns", accent: "text-red-400" },
  source_credibility: { label: "Source Trust", accent: "text-amber-400" },
};

export default function QdrantInsight({ stats }: QdrantInsightProps) {
  if (!stats.length) return null;

  const totalHits = stats.reduce((s, c) => s + c.hits, 0);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="card relative overflow-hidden"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-400/30 to-transparent" />

      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.15em] text-violet-400">
          <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
          </svg>
          Qdrant RAG
        </h3>
        <span className="rounded-md bg-violet-500/10 px-2 py-0.5 font-mono text-[10px] text-violet-400">
          {totalHits} vectors searched
        </span>
      </div>

      <div className="space-y-3">
        {stats.map((s, i) => {
          const meta = COLLECTION_META[s.collection] || { label: s.collection, accent: "text-gray-400" };
          return (
            <motion.div
              key={s.collection}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.08, duration: 0.4 }}
              className="flex items-center justify-between rounded-lg border border-white/[0.04] bg-white/[0.02] px-3 py-2.5"
            >
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${s.hits > 0 ? "bg-violet-400" : "bg-gray-700"}`} />
                <span className="text-xs font-medium text-gray-300">{meta.label}</span>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="text-gray-500">{s.hits} hit{s.hits !== 1 ? "s" : ""}</span>
                {s.top_score > 0 && (
                  <span className={`font-mono ${meta.accent}`}>
                    {(s.top_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
