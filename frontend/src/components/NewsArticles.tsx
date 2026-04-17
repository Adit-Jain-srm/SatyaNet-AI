"use client";

import { motion } from "framer-motion";
import type { NewsArticle } from "@/lib/api";

interface NewsArticlesProps {
  articles: NewsArticle[];
}

export default function NewsArticles({ articles }: NewsArticlesProps) {
  if (!articles.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="card relative overflow-hidden"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent" />

      <h3 className="mb-4 flex items-center gap-3 text-[11px] font-bold uppercase tracking-[0.15em] text-cyan-400">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/10">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        </div>
        Related News ({articles.length})
      </h3>

      <div className="space-y-3">
        {articles.map((article, i) => (
          <a
            key={i}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block rounded-lg border border-white/[0.04] bg-white/[0.02] p-3 transition-all hover:border-white/[0.1] hover:bg-white/[0.04]"
          >
            <p className="text-[13px] font-medium text-gray-300 group-hover:text-white">
              {article.title}
            </p>
            <div className="mt-1.5 flex items-center gap-2 text-[11px] text-gray-500">
              <span className="font-medium text-gray-400">{article.source}</span>
              {article.published_at && (
                <>
                  <span className="h-3 w-px bg-white/10" />
                  <span>{new Date(article.published_at).toLocaleDateString()}</span>
                </>
              )}
            </div>
            {article.description && (
              <p className="mt-1.5 text-xs text-gray-600 line-clamp-2">
                {article.description}
              </p>
            )}
          </a>
        ))}
      </div>
    </motion.div>
  );
}
