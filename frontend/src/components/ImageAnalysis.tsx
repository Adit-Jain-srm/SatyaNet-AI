"use client";

import { motion } from "framer-motion";
import type { ImageAnalysisResult } from "@/lib/api";

interface ImageAnalysisProps {
  result: ImageAnalysisResult;
}

export default function ImageAnalysis({ result }: ImageAnalysisProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="glass-strong relative overflow-hidden p-6"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-purple-400/30 to-transparent" />

      <h3 className="mb-5 text-[11px] font-bold uppercase tracking-[0.15em] text-purple-400">
        Image Forensics
      </h3>

      <div className="grid grid-cols-2 gap-5">
        {[
          { label: "AI Generated", value: result.ai_probability, flag: result.is_ai_generated },
          { label: "Manipulated", value: result.manipulation_probability, flag: result.is_manipulated },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 + i * 0.1 }}
            className="space-y-2"
          >
            <p className="text-[11px] font-medium text-gray-500">{item.label}</p>
            <p
              className={`text-xl font-bold ${
                item.flag ? "text-red-400" : "text-satya-400"
              }`}
            >
              {item.flag ? "Likely" : "Unlikely"}
            </p>
            <div className="h-1 w-full overflow-hidden rounded-full bg-white/[0.04]">
              <motion.div
                className={`h-full rounded-full ${
                  item.value > 0.5 ? "bg-red-400" : "bg-satya-500"
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${item.value * 100}%` }}
                transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
              />
            </div>
            <p className="font-mono text-[11px] text-gray-600">
              {(item.value * 100).toFixed(1)}%
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
