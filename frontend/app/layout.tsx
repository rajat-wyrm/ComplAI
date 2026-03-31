import { PreloadRoutes } from '@/components/utils/PreloadRoutes';
import type { Metadata } from "next";
import { PreloadRoutes } from '@/components/utils/PreloadRoutes';
import { Inter } from "next/font/google";
import { PreloadRoutes } from '@/components/utils/PreloadRoutes';
import "./globals.css";

import { PreloadRoutes } from '@/components/utils/PreloadRoutes';
import { Sidebar } from "@/components/layout/Sidebar";
import { PreloadRoutes } from '@/components/utils/PreloadRoutes';
import { TopBar } from "@/components/layout/TopBar";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Compliance & Risk Copilot | Enterprise RegTech",
  description:
    "Enterprise-grade AI-powered compliance, risk intelligence and document analysis platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.className} bg-black text-white antialiased`}
      >

        {/* =========================
            GLOBAL BACKGROUND (OPTIMIZED PREMIUM)
        ========================= */}
        <div className="fixed inset-0 -z-10 overflow-hidden">

          {/* base */}
          <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0b1120] to-black" />

          {/* glow (LOW GPU COST) */}
          <div className="absolute top-[-10%] left-[-10%] w-[350px] h-[350px] bg-purple-600/20 blur-[80px] rounded-full" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[350px] h-[350px] bg-blue-600/20 blur-[80px] rounded-full" />

          {/* grid overlay */}
          <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(circle,white_1px,transparent_1px)] [background-size:24px_24px]" />
        </div>

        {/* =========================
            APP LAYOUT
        ========================= */}
        <div className="flex h-screen overflow-hidden">

          {/* SIDEBAR */}
          <aside className="w-[260px] border-r border-white/10 bg-white/5 backdrop-blur-xl">

            {/* depth */}
            <div className="h-full bg-gradient-to-b from-white/5 to-transparent">
              <Sidebar />
            </div>

          </aside>

          {/* MAIN AREA */}
          <div className="flex-1 flex flex-col overflow-hidden">

            {/* TOPBAR */}
            <header className="border-b border-white/10 bg-white/5 backdrop-blur-xl">
              <TopBar />
            </header>

            {/* CONTENT */}
            <main className="flex-1 overflow-y-auto scroll-smooth">

              <div className="max-w-[1400px] mx-auto px-4 md:px-6 py-6 space-y-6">

                {/* glass container */}
                <div className="rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-lg p-4 md:p-6 shadow-inner">
                  <PreloadRoutes />
{children}
                </div>

              </div>

            </main>

          </div>

        </div>

      </body>
    </html>
  );
}
