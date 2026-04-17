"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface PipelineLogProps {
  log: string[];
  detectionMethod: string;
}

export default function PipelineLog({ log, detectionMethod }: PipelineLogProps) {
  const [open, setOpen] = useState(false);

  if (!log.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="card"
    >
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between text-left"
      >
        <h3 className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.15em] text-gray-500">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Pipeline Trace ({log.length} steps)
        </h3>
        <motion.svg
          animate={{ rotate: open ? 180 : 0 }}
          className="h-4 w-4 text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-4 space-y-1.5">
              {log.map((entry, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 rounded-md bg-white/[0.02] px-3 py-2 text-xs"
                >
                  <span className="mt-px shrink-0 font-mono text-gray-700">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span className="text-gray-400">{entry}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 text-[10px] text-gray-600">
              Detection: {detectionMethod}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
