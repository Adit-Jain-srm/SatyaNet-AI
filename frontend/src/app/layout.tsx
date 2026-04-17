import type { Metadata } from "next";
import HealthPill from "@/components/HealthPill";
import "./globals.css";

export const metadata: Metadata = {
  title: "SatyaNet AI — Misinformation Detection",
  description:
    "AI-powered multimodal, multilingual misinformation detection and counter-response system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen font-[Inter,system-ui,sans-serif]">
        {/* Ambient background */}
        <div className="pointer-events-none fixed inset-0 -z-10">
          <div className="absolute left-1/2 top-0 h-[600px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-satya-600/[0.07] blur-[120px]" />
          <div className="absolute bottom-0 right-0 h-[400px] w-[600px] translate-x-1/4 translate-y-1/4 rounded-full bg-blue-600/[0.04] blur-[100px]" />
          <div className="dot-grid absolute inset-0 opacity-50" />
        </div>

        {/* Nav */}
        <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-[#07080a]/70 backdrop-blur-2xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <a href="/" className="group flex items-center gap-3">
              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-satya-500 to-emerald-400 text-lg font-extrabold text-white shadow-lg shadow-satya-600/20 transition-transform duration-300 group-hover:scale-105">
                S
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight leading-none">
                  Satya<span className="text-satya-400">Net</span>
                </span>
                <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-gray-600">
                  AI Truth Engine
                </span>
              </div>
            </a>
            <nav className="flex items-center gap-2">
              <HealthPill />
              <a
                href="/"
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-400 transition-colors hover:bg-white/[0.04] hover:text-white"
              >
                Analyze
              </a>
              <a
                href="https://github.com/Adit-Jain-srm/SatyaNet-AI"
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-500 transition-colors hover:bg-white/[0.04] hover:text-gray-300"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-6 py-12">{children}</main>
      </body>
    </html>
  );
}
