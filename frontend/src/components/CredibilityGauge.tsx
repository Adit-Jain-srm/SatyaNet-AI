"use client";

import { motion } from "framer-motion";
import { scoreColor } from "@/lib/utils";

interface CredibilityGaugeProps {
  score: number;
  size?: number;
}

export default function CredibilityGauge({
  score,
  size = 200,
}: CredibilityGaugeProps) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;
  const color = scoreColor(score);
  const pct = Math.round(score * 100);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Outer glow */}
      <div
        className="absolute inset-0 rounded-full blur-2xl opacity-30"
        style={{ background: `radial-gradient(circle, ${color}40 0%, transparent 70%)` }}
      />

      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        className="-rotate-90"
      >
        {/* Track */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="5"
          className="text-white/[0.06]"
        />
        {/* Progress */}
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
        />
        {/* Glow layer */}
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
          className="blur-[3px] opacity-40"
        />
      </svg>

      {/* Center label */}
      <div className="absolute flex flex-col items-center">
        <motion.span
          className="text-5xl font-extrabold tabular-nums"
          style={{ color }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          {pct}
        </motion.span>
        <span className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-gray-500">
          Credibility
        </span>
      </div>
    </div>
  );
}
