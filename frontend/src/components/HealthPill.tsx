"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";

export default function HealthPill() {
  const [status, setStatus] = useState<"loading" | "healthy" | "error">("loading");
  const [collections, setCollections] = useState(0);

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setStatus(data.qdrant_connected ? "healthy" : "error");
        setCollections(data.collections.length);
      })
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div className="group relative flex items-center gap-1.5 rounded-full border border-white/[0.06] bg-white/[0.02] px-3 py-1.5 text-[10px] font-medium text-gray-500">
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === "healthy"
            ? "bg-satya-400"
            : status === "error"
              ? "bg-red-400"
              : "bg-gray-600 animate-pulse"
        }`}
      />
      Qdrant
      <div className="pointer-events-none absolute right-0 top-full mt-2 hidden rounded-lg border border-white/10 bg-gray-900 px-3 py-2 text-[10px] text-gray-400 shadow-xl group-hover:block">
        {status === "healthy"
          ? `Connected: ${collections} collection${collections !== 1 ? "s" : ""}`
          : status === "error"
            ? "Connection failed"
            : "Checking..."}
      </div>
    </div>
  );
}
