"use client";

import { motion } from "framer-motion";
import type { VideoAnalysisResult } from "@/lib/api";

interface VideoAnalysisProps {
  result: VideoAnalysisResult;
}

export default function VideoAnalysis({ result }: VideoAnalysisProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="glass-strong relative overflow-hidden p-6"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-rose-400/30 to-transparent" />

      <h3 className="mb-5 text-[11px] font-bold uppercase tracking-[0.15em] text-rose-400">
        Video Forensics
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Deepfake Detection</span>
          <span className={`text-lg font-bold ${result.is_deepfake ? "text-red-400" : "text-satya-400"}`}>
            {result.is_deepfake ? "Likely Deepfake" : "Likely Authentic"}
          </span>
        </div>

        <div className="space-y-2">
          {[
            { label: "Deepfake Probability", value: result.deepfake_probability },
            { label: "Lip Sync Score", value: result.lip_sync_score },
            { label: "Temporal Consistency", value: result.temporal_consistency },
          ].map((item) => (
            <div key={item.label} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">{item.label}</span>
                <span className="font-mono text-gray-600">{(item.value * 100).toFixed(0)}%</span>
              </div>
              <div className="h-1 w-full overflow-hidden rounded-full bg-white/[0.04]">
                <motion.div
                  className={`h-full rounded-full ${item.value > 0.5 ? "bg-red-400" : "bg-satya-500"}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${item.value * 100}%` }}
                  transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-4 text-xs text-gray-600">
          {result.frame_count_analyzed > 0 && <span>Frames: {result.frame_count_analyzed}</span>}
          {result.face_swap_detected && <span className="text-red-400">Face swap detected</span>}
        </div>
      </div>
    </motion.div>
  );
}
