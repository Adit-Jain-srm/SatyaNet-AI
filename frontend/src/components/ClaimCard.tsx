"use client";

import { motion } from "framer-motion";
import type { ClaimResult } from "@/lib/api";
import VerdictBadge from "./VerdictBadge";

interface ClaimCardProps {
  claim: ClaimResult;
  index: number;
}

export default function ClaimCard({ claim, index }: ClaimCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1, ease: [0.16, 1, 0.3, 1] }}
      className="card group space-y-4"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/[0.06] text-xs font-bold text-gray-400">
            {index + 1}
          </span>
          <h4 className="text-[13px] font-semibold text-gray-300">Claim</h4>
        </div>
        <VerdictBadge verdict={claim.verdict} />
      </div>

      <p className="text-[14px] leading-relaxed text-gray-300/90">{claim.claim}</p>

      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span className="font-mono">{(claim.confidence * 100).toFixed(0)}% confidence</span>
        {claim.matched_misinfo && (
          <>
            <span className="h-3 w-px bg-white/10" />
            <span className="flex items-center gap-1 text-red-400/80">
              <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Known misinformation match
            </span>
          </>
        )}
      </div>

      {claim.evidence.length > 0 && (
        <div className="space-y-2">
          <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-gray-500">
            Evidence
          </p>
          <div className="space-y-1.5">
            {claim.evidence.map((e, i) => (
              <div
                key={i}
                className="rounded-lg border border-white/[0.04] bg-white/[0.02] px-3 py-2.5 text-xs leading-relaxed text-gray-400"
              >
                {e}
              </div>
            ))}
          </div>
        </div>
      )}

      {claim.source_scores.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {claim.source_scores.map((s, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1.5 rounded-md border border-white/[0.06] bg-white/[0.02] px-2.5 py-1 text-[11px] text-gray-400"
            >
              {s.source}
              <span className="font-mono text-gray-600">
                {(s.credibility * 100).toFixed(0)}%
              </span>
            </span>
          ))}
        </div>
      )}

      {claim.external_factchecks && claim.external_factchecks.length > 0 && (
        <div className="space-y-2 border-t border-white/[0.04] pt-3">
          <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-blue-400">
            External Fact-Checks (Google)
          </p>
          <div className="space-y-1.5">
            {claim.external_factchecks.map((fc, i) => (
              <a
                key={i}
                href={fc.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-2.5 rounded-lg border border-blue-500/10 bg-blue-500/[0.03] px-3 py-2.5 transition-all hover:border-blue-500/20 hover:bg-blue-500/[0.06]"
              >
                <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded bg-blue-500/10">
                  <svg className="h-3 w-3 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-gray-300 group-hover:text-white">
                    {fc.publisher_name}: <span className="font-bold text-blue-300">{fc.rating}</span>
                  </p>
                  {fc.title && (
                    <p className="truncate text-[11px] text-gray-500">{fc.title}</p>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
