"use client";

import { motion } from "framer-motion";
import type { ImageAnalysisResult } from "@/lib/api";

interface ImageAnalysisProps {
  result: ImageAnalysisResult;
}

export default function ImageAnalysis({ result }: ImageAnalysisProps) {
  const isVision = result.analysis_method === "gpt4o_vision";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="glass-strong relative overflow-hidden p-6"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-purple-400/30 to-transparent" />

      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.15em] text-purple-400">
          Image Forensics
        </h3>
        <span className="rounded-md bg-purple-500/10 px-2 py-0.5 text-[10px] font-medium text-purple-400">
          {isVision ? "GPT-4o Vision" : "Heuristic"}
        </span>
      </div>

      {/* Description */}
      {result.description && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-4 rounded-lg border border-white/[0.04] bg-white/[0.02] px-3 py-2.5 text-[13px] leading-relaxed text-gray-300"
        >
          {result.description}
        </motion.p>
      )}

      {/* Core metrics */}
      <div className="mb-5 grid grid-cols-2 gap-4">
        <MetricCard
          label="AI Generated"
          value={result.ai_probability}
          flag={result.is_ai_generated}
          delay={0}
        />
        <MetricCard
          label="Manipulated"
          value={result.manipulation_probability}
          flag={result.is_manipulated}
          delay={0.1}
        />
      </div>

      {/* Real photo badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className={`mb-4 flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium ${
          result.is_real_photo
            ? "border border-satya-500/20 bg-satya-500/[0.06] text-satya-400"
            : "border border-red-500/20 bg-red-500/[0.06] text-red-400"
        }`}
      >
        <span className={`h-2 w-2 rounded-full ${result.is_real_photo ? "bg-satya-400" : "bg-red-400"}`} />
        {result.is_real_photo ? "Appears to be a genuine photograph" : "May not be a genuine photograph"}
      </motion.div>

      {/* AI Reasoning */}
      {result.ai_reasoning && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mb-3 space-y-1"
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-600">
            AI Analysis
          </p>
          <p className="text-xs leading-relaxed text-gray-400">
            {result.ai_reasoning}
          </p>
        </motion.div>
      )}

      {/* Extracted text */}
      {result.extracted_text && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-3 space-y-1"
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-cyan-500">
            Text Found in Image
          </p>
          <p className="rounded-lg border border-cyan-500/10 bg-cyan-500/[0.04] px-3 py-2 text-xs italic leading-relaxed text-gray-300">
            {result.extracted_text}
          </p>
        </motion.div>
      )}

      {/* Content concerns */}
      {result.content_concerns.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
          className="mb-3 space-y-1.5"
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-amber-500">
            Concerns
          </p>
          <div className="space-y-1">
            {result.content_concerns.map((c, i) => (
              <div
                key={i}
                className="flex items-start gap-2 rounded-md border border-amber-500/10 bg-amber-500/[0.04] px-2.5 py-1.5 text-[11px] text-amber-300/80"
              >
                <svg className="mt-0.5 h-3 w-3 shrink-0 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {c}
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Context flags */}
      {result.context_flags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {result.context_flags.map((flag, i) => (
            <span
              key={i}
              className="rounded-md border border-red-500/15 bg-red-500/[0.06] px-2 py-1 text-[10px] text-red-400"
            >
              {flag}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

function MetricCard({
  label,
  value,
  flag,
  delay,
}: {
  label: string;
  value: number;
  flag: boolean;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 + delay }}
      className="space-y-2"
    >
      <p className="text-[11px] font-medium text-gray-500">{label}</p>
      <p className={`text-xl font-bold ${flag ? "text-red-400" : "text-satya-400"}`}>
        {flag ? "Likely" : "Unlikely"}
      </p>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.04]">
        <motion.div
          className={`h-full rounded-full ${value > 0.5 ? "bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.3)]" : "bg-satya-500 shadow-[0_0_8px_rgba(34,197,94,0.3)]"}`}
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 1, delay: 0.4 + delay, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <p className="font-mono text-[11px] text-gray-600">{(value * 100).toFixed(1)}%</p>
    </motion.div>
  );
}
