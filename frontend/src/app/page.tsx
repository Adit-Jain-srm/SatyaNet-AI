"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AnalysisForm from "@/components/AnalysisForm";
import AudioAnalysis from "@/components/AudioAnalysis";
import BreakdownChart from "@/components/BreakdownChart";
import ClaimCard from "@/components/ClaimCard";
import CounterContent from "@/components/CounterContent";
import CredibilityGauge from "@/components/CredibilityGauge";
import ExplanationCard from "@/components/ExplanationCard";
import ImageAnalysis from "@/components/ImageAnalysis";
import LanguageBadge from "@/components/LanguageBadge";
import NewsArticles from "@/components/NewsArticles";
import VerdictBadge from "@/components/VerdictBadge";
import VideoAnalysis from "@/components/VideoAnalysis";
import PipelineLog from "@/components/PipelineLog";
import QdrantInsight from "@/components/QdrantInsight";
import {
  analyzeContent,
  analyzeFile,
  type AnalysisRequest,
  type AnalysisResponse,
} from "@/lib/api";

const FEATURES = [
  {
    icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
    title: "Multi-Modal Detection",
    desc: "Text, image, URL, audio & video analysis",
  },
  {
    icon: "M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z",
    title: "Audio & Video",
    desc: "Voice clone and deepfake detection",
  },
  {
    icon: "M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129",
    title: "Trilingual Intelligence",
    desc: "English, Hindi, and Tamil with auto-detection",
  },
  {
    icon: "M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z",
    title: "Live News",
    desc: "Real-time related news from global sources",
  },
];

export default function Home() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (request: AnalysisRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await analyzeContent(request);
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Analysis failed. Is the backend running?"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSubmit = async (file: File, type: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await analyzeFile(file, type);
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Analysis failed. Is the backend running?"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-16">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="text-center"
      >
        <div className="mx-auto max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-4 py-1.5 text-xs font-medium text-gray-400 backdrop-blur-sm">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-satya-400 opacity-75" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-satya-400" />
            </span>
            AI-Powered Fact Verification
          </div>

          <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl">
            <span className="block text-white">Fight Misinfo</span>
            <span className="block bg-gradient-to-r from-satya-400 via-emerald-300 to-teal-400 bg-clip-text text-transparent">
              with Truth
            </span>
          </h1>

          <p className="mx-auto max-w-xl text-lg leading-relaxed text-gray-500">
            SatyaNet detects, explains, and counters misinformation in real time
            across text, images, audio, and video — in English, Hindi, and Tamil.
          </p>
        </div>
      </motion.section>

      {/* Feature pills */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="mx-auto grid max-w-4xl grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4"
      >
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + i * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="group glass flex items-center gap-3 p-4 transition-all duration-300 hover:bg-white/[0.05]"
          >
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-satya-500/10 text-satya-400 transition-colors group-hover:bg-satya-500/15">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={f.icon} />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-200">{f.title}</p>
              <p className="text-[11px] text-gray-500">{f.desc}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Input Card */}
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="card mx-auto max-w-3xl"
      >
        <AnalysisForm onSubmit={handleAnalyze} onFileSubmit={handleFileSubmit} isLoading={isLoading} />
      </motion.section>

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="mx-auto max-w-3xl space-y-6 animate-pulse">
          <div className="card flex items-center justify-between">
            <div className="skeleton h-[180px] w-[180px] rounded-full" />
            <div className="space-y-3">
              <div className="skeleton h-8 w-32 rounded-full" />
              <div className="skeleton h-6 w-20 rounded-full" />
            </div>
          </div>
          <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
            <div className="skeleton h-64 rounded-2xl" />
            <div className="space-y-4">
              <div className="skeleton h-40 rounded-2xl" />
              <div className="skeleton h-32 rounded-2xl" />
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            className="glass mx-auto max-w-3xl border-red-500/20 bg-red-500/[0.06] p-5 text-[13px] text-red-400"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-500/10">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              {error}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="space-y-10"
          >
            {/* Divider */}
            <div className="glow-line mx-auto max-w-md" />

            {/* Score Header */}
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              className="card mx-auto max-w-3xl"
            >
              <div className="flex flex-col items-center justify-between gap-8 sm:flex-row">
                <CredibilityGauge score={result.credibility_score} />
                <div className="flex flex-col items-center gap-4 sm:items-end">
                  <VerdictBadge verdict={result.verdict} className="text-base" />
                  <LanguageBadge code={result.detected_language} />
                  <p className="text-center text-[11px] text-gray-600 sm:text-right">
                    Analyzed against{" "}
                    <span className="text-gray-400">3 Qdrant collections</span>
                    {" + "}
                    <span className="text-blue-400">Google Fact Check API</span>
                  </p>
                </div>
              </div>
              {result.verdict_reason && (
                <motion.p
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="mt-4 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3 text-[13px] leading-relaxed text-gray-400"
                >
                  {result.verdict_reason}
                </motion.p>
              )}
            </motion.div>

            {/* Two-column layout */}
            <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
              {/* Sidebar */}
              <div className="space-y-6">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                  className="card"
                >
                  <BreakdownChart breakdown={result.breakdown} />
                </motion.div>

                {result.image_analysis && (
                  <ImageAnalysis result={result.image_analysis} />
                )}

                {result.audio_analysis && (
                  <AudioAnalysis result={result.audio_analysis} />
                )}

                {result.video_analysis && (
                  <VideoAnalysis result={result.video_analysis} />
                )}

                {result.qdrant_stats?.length > 0 && (
                  <QdrantInsight stats={result.qdrant_stats} />
                )}
              </div>

              {/* Main content */}
              <div className="space-y-6">
                <ExplanationCard explanation={result.explanation} />

                <CounterContent
                  counterContent={result.counter_content}
                  shareableSummary={result.shareable_summary}
                />

                {result.news_articles?.length > 0 && (
                  <NewsArticles articles={result.news_articles} />
                )}

                {result.claims.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-[11px] font-bold uppercase tracking-[0.15em] text-gray-500">
                      Claims Analyzed ({result.claims.length})
                    </h3>
                    {result.claims.map((claim, i) => (
                      <ClaimCard key={i} claim={claim} index={i} />
                    ))}
                  </div>
                )}

                {result.processing_log?.length > 0 && (
                  <PipelineLog
                    log={result.processing_log}
                    detectionMethod={result.detection_method}
                  />
                )}
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="space-y-4 pt-8">
        <div className="glow-line mx-auto max-w-xs opacity-50" />
        <p className="text-center text-[11px] tracking-wide text-gray-700">
          SatyaNet AI &middot; Team Arize &middot; Qdrant + FastAPI + Azure OpenAI + News API
        </p>
      </footer>
    </div>
  );
}
