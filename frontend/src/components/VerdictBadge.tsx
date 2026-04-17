"use client";

import { motion } from "framer-motion";
import { cn, verdictBg, verdictColor, verdictLabel } from "@/lib/utils";

interface VerdictBadgeProps {
  verdict: string;
  className?: string;
}

export default function VerdictBadge({ verdict, className }: VerdictBadgeProps) {
  return (
    <motion.span
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "inline-flex items-center rounded-full border px-5 py-2 text-sm font-bold tracking-wide backdrop-blur-sm",
        verdictBg(verdict),
        verdictColor(verdict),
        className,
      )}
    >
      {verdictLabel(verdict)}
    </motion.span>
  );
}
