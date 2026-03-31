import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Compliance Copilot",
  description: "AI compliance system",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="flex h-screen">

          <Sidebar />

          <div className="flex-1 flex flex-col">
            <TopBar />

            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>

        </div>
      </body>
    </html>
  );
}
