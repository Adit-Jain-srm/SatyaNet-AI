"use client";

import { motion } from "framer-motion";
import { languageName } from "@/lib/utils";

interface LanguageBadgeProps {
  code: string;
}

export default function LanguageBadge({ code }: LanguageBadgeProps) {
  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-1.5 text-xs font-medium text-gray-300 backdrop-blur-sm"
    >
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-satya-400 opacity-40" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-satya-400" />
      </span>
      {languageName(code)}
    </motion.span>
  );
}
