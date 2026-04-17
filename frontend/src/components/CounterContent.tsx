"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface CounterContentProps {
  counterContent: string;
  shareableSummary: string;
}

export default function CounterContent({
  counterContent,
  shareableSummary,
}: CounterContentProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(shareableSummary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-5">
      {/* Verified info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        className="glass-strong relative overflow-hidden p-6"
      >
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-satya-400/40 to-transparent" />
        <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-satya-500/[0.04] blur-3xl" />

        <h3 className="mb-4 flex items-center gap-3 text-[11px] font-bold uppercase tracking-[0.15em] text-satya-500">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-satya-500/10">
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          Verified Information
        </h3>
        <div className="whitespace-pre-wrap text-[14px] leading-[1.8] text-gray-300/90">
          {counterContent}
        </div>
      </motion.div>

      {/* Shareable summary */}
      {shareableSummary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="card"
        >
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-[11px] font-bold uppercase tracking-[0.15em] text-gray-500">
              Share on WhatsApp
            </h3>
            <button
              onClick={handleCopy}
              className="relative overflow-hidden rounded-lg border border-white/10 bg-white/[0.03] px-4 py-1.5 text-xs font-medium text-gray-400 transition-all duration-300 hover:bg-white/[0.06] hover:text-white"
            >
              <AnimatePresence mode="wait">
                {copied ? (
                  <motion.span
                    key="copied"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="text-satya-400"
                  >
                    Copied!
                  </motion.span>
                ) : (
                  <motion.span
                    key="copy"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    Copy
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          </div>
          <p className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 text-[13px] italic leading-relaxed text-gray-400">
            {shareableSummary}
          </p>
        </motion.div>
      )}
    </div>
  );
}
