"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { AnalysisRequest } from "@/lib/api";

interface AnalysisFormProps {
  onSubmit: (request: AnalysisRequest) => void;
  onFileSubmit: (file: File, type: string) => void;
  isLoading: boolean;
}

const EXAMPLES = [
  {
    label: "UPI Ban Hoax",
    lang: "EN",
    content:
      "BREAKING: Government has banned all UPI transactions in India! All digital payments stopped. Switch to cash immediately!",
    type: "text" as const,
  },
  {
    label: "5G षड्यंत्र",
    lang: "HI",
    content:
      "5G टावर COVID-19 फैला रहे हैं! सरकार छुपा रही है सच! तुरंत अपने आस-पास के 5G टावर को बंद करवाएं!",
    type: "text" as const,
  },
  {
    label: "தடுப்பூசி பொய்",
    lang: "TA",
    content:
      "COVID-19 தடுப்பூசிகளில் மைக்ரோசிப்கள் உள்ளன! அரசு மக்களை கண்காணிக்க திட்டமிடுகிறது!",
    type: "text" as const,
  },
  {
    label: "Free Laptop Scam",
    lang: "EN",
    content:
      "PM Modi is giving free laptops to all students! Click this WhatsApp link to register now. Limited time offer!",
    type: "text" as const,
  },
];

const TABS = [
  { key: "text", label: "Text", icon: "M4 6h16M4 12h16M4 18h7", accept: "" },
  { key: "image", label: "Image", icon: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", accept: "image/*" },
  { key: "audio", label: "Audio", icon: "M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z", accept: "audio/*" },
  { key: "video", label: "Video", icon: "M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z", accept: "video/*" },
  { key: "url", label: "URL", icon: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1", accept: "" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const MEDIA_TYPES = new Set(["image", "audio", "video"]);

export default function AnalysisForm({ onSubmit, onFileSubmit, isLoading }: AnalysisFormProps) {
  const [content, setContent] = useState("");
  const [activeTab, setActiveTab] = useState<TabKey>("text");
  const [fileName, setFileName] = useState("");
  const [fileSize, setFileSize] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isMedia = MEDIA_TYPES.has(activeTab);
  const activeTabDef = TABS.find((t) => t.key === activeTab)!;

  const handleTabSwitch = (key: TabKey) => {
    setActiveTab(key);
    setContent("");
    setFileName("");
    setSelectedFile(null);
    if (MEDIA_TYPES.has(key)) {
      setTimeout(() => fileInputRef.current?.click(), 50);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setFileSize(file.size);
    setSelectedFile(file);

    if (activeTab === "image") {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = (reader.result as string).split(",")[1];
        setContent(base64);
      };
      reader.readAsDataURL(file);
    } else {
      setContent(`__file__:${file.name}`);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() && !selectedFile) return;

    if (selectedFile && (activeTab === "audio" || activeTab === "video" || activeTab === "image")) {
      onFileSubmit(selectedFile, activeTab);
    } else if (content.trim()) {
      onSubmit({ content, content_type: activeTab });
    }
  };

  const clearFile = () => {
    setContent("");
    setFileName("");
    setFileSize(0);
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const fileLabel = () => {
    const sizeMb = (fileSize / (1024 * 1024)).toFixed(1);
    const sizeKb = Math.round(fileSize / 1024);
    const display = fileSize > 1024 * 1024 ? `${sizeMb} MB` : `${sizeKb} KB`;
    return `${fileName} (${display})`;
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Tabs */}
      <div className="flex gap-1 rounded-xl border border-white/[0.06] bg-white/[0.02] p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => handleTabSwitch(tab.key)}
            className={`relative flex-1 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-300 ${
              activeTab === tab.key ? "text-white" : "text-gray-500 hover:text-gray-300"
            }`}
          >
            {activeTab === tab.key && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 rounded-lg bg-white/[0.08] border border-white/[0.08]"
                transition={{ type: "spring", duration: 0.4, bounce: 0.15 }}
              />
            )}
            <span className="relative flex items-center justify-center gap-1.5">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={tab.icon} />
              </svg>
              <span className="hidden sm:inline">{tab.label}</span>
            </span>
          </button>
        ))}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={activeTabDef.accept}
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Input area */}
      <AnimatePresence mode="wait">
        {isMedia && (fileName || content) ? (
          <motion.div
            key="file-preview"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] p-5"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/[0.06]">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={activeTabDef.icon} />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-300">{fileName || `${activeTab} loaded`}</p>
                {fileSize > 0 && (
                  <p className="text-xs text-gray-500">{fileLabel()}</p>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={clearFile}
              className="text-sm text-red-400/80 transition-colors hover:text-red-300"
            >
              Remove
            </button>
          </motion.div>
        ) : isMedia ? (
          <motion.div
            key="file-drop"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            onClick={() => fileInputRef.current?.click()}
            className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-white/[0.08] bg-white/[0.01] p-10 transition-all hover:border-white/[0.15] hover:bg-white/[0.03]"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/[0.06]">
              <svg className="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-400">
                Click to upload {activeTab}
              </p>
              <p className="text-xs text-gray-600">
                {activeTab === "image" && "JPG, PNG, WebP up to 10MB"}
                {activeTab === "audio" && "WAV, MP3, OGG up to 25MB"}
                {activeTab === "video" && "MP4, WebM, MOV up to 50MB"}
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.div key="text-input" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={
                activeTab === "url"
                  ? "https://example.com/article..."
                  : "Paste text, news article, or WhatsApp forward to fact-check..."
              }
              className="input-field min-h-[160px] resize-y text-[15px] leading-relaxed"
              rows={5}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Examples (text tab only) */}
      {activeTab === "text" && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-600">
            Examples
          </span>
          {EXAMPLES.map((example) => (
            <button
              key={example.label}
              type="button"
              onClick={() => { setContent(example.content); setActiveTab("text"); }}
              className="group flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-1.5 text-xs text-gray-500 transition-all duration-300 hover:border-white/[0.12] hover:bg-white/[0.04] hover:text-gray-300"
            >
              <span className="rounded bg-white/[0.06] px-1 py-0.5 font-mono text-[10px] text-gray-600 transition-colors group-hover:text-gray-400">
                {example.lang}
              </span>
              {example.label}
            </button>
          ))}
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={(!content.trim() && !selectedFile) || isLoading}
        className="btn-primary w-full"
      >
        {isLoading ? (
          <span className="flex items-center gap-3">
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              className="inline-block"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            </motion.span>
            Analyzing across verified databases...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Analyze {activeTab === "text" ? "Content" : activeTab === "url" ? "URL" : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
          </span>
        )}
      </button>
    </form>
  );
}
