"use client";

import { motion } from "framer-motion";

interface ExplanationCardProps {
  explanation: string;
}

export default function ExplanationCard({ explanation }: ExplanationCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="card group relative overflow-hidden"
    >
      {/* Accent border top */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-satya-500/50 to-transparent" />

      <h3 className="mb-4 flex items-center gap-3 text-[11px] font-bold uppercase tracking-[0.15em] text-gray-500">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-satya-500/10 text-satya-400">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        Why This Rating
      </h3>
      <div className="whitespace-pre-wrap text-[14px] leading-[1.8] text-gray-300/90">
        {explanation}
      </div>
    </motion.div>
  );
}
