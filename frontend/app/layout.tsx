import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { ToastProvider } from "@/components/ui/toast";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Compliance & Risk Copilot",
  description: "RegTech AI for legal and compliance document analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <ToastProvider>
          <Sidebar />
          <main className="ml-64 min-h-screen">
            <div className="container mx-auto p-8">{children}</div>
          </main>
          <Toaster />
        </ToastProvider>
      </body>
    </html>
  );
}
