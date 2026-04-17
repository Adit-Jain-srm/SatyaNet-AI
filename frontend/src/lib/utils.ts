import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function verdictColor(verdict: string): string {
  switch (verdict) {
    case "true":
      return "text-satya-400";
    case "false":
      return "text-danger-400";
    case "misleading":
      return "text-warn-400";
    default:
      return "text-gray-400";
  }
}

export function verdictBg(verdict: string): string {
  switch (verdict) {
    case "true":
      return "bg-satya-600/20 border-satya-600/40";
    case "false":
      return "bg-danger-500/20 border-danger-500/40";
    case "misleading":
      return "bg-warn-500/20 border-warn-500/40";
    default:
      return "bg-gray-700/20 border-gray-600/40";
  }
}

export function verdictLabel(verdict: string): string {
  switch (verdict) {
    case "true":
      return "Verified True";
    case "false":
      return "Likely False";
    case "misleading":
      return "Misleading";
    default:
      return "Unverified";
  }
}

export function scoreColor(score: number): string {
  if (score >= 0.75) return "#22c55e";
  if (score >= 0.5) return "#6b7280";
  if (score >= 0.25) return "#f59e0b";
  return "#ef4444";
}

export function languageName(code: string): string {
  const map: Record<string, string> = {
    en: "English",
    hi: "Hindi",
    ta: "Tamil",
  };
  return map[code] || code.toUpperCase();
}
