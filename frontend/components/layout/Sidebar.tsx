"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Upload,
  MessageSquare,
  History,
  Shield,
  Zap,
  Menu,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Analytics", href: "/", icon: LayoutDashboard },
  { name: "Upload", href: "/upload", icon: Upload },
  { name: "AI Chat", href: "/chat", icon: MessageSquare },
  { name: "History", href: "/history", icon: History },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setIsMobileOpen(false);
      }
    };
    checkScreenSize();
    window.addEventListener("resize", checkScreenSize);
    return () => window.removeEventListener("resize", checkScreenSize);
  }, []);

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="flex h-16 md:h-20 items-center gap-3 px-4 md:px-6 border-b border-white/10">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl blur-lg opacity-50" />
          <Shield className="relative h-8 w-8 md:h-10 md:w-10 text-white" />
        </div>
        <div className="flex flex-col">
          <span className="text-base md:text-lg font-bold gradient-text">Compliance</span>
          <span className="text-[10px] md:text-xs text-white/50">Risk Copilot Enterprise</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 md:space-y-2 px-3 md:px-4 py-6 md:py-8">
        {navigation.map((item, index) => {
          const isActive = pathname === item.href;
          return (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link
                href={item.href}
                onClick={() => setIsMobileOpen(false)}
                className={cn(
                  "group relative flex items-center gap-2 md:gap-3 rounded-xl px-3 md:px-4 py-2 md:py-2.5 text-sm font-medium transition-all duration-300",
                  isActive
                    ? "bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                )}
              >
                <item.icon className="h-4 w-4 md:h-5 md:w-5" />
                <span>{item.name}</span>
                {isActive && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/20 to-blue-500/20"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
              </Link>
            </motion.div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 p-3 md:p-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 p-3 md:p-4"
        >
          <div className="relative">
            <div className="flex items-center gap-1 md:gap-2 mb-1 md:mb-2">
              <Zap className="h-3 w-3 md:h-4 md:w-4 text-purple-400" />
              <span className="text-[10px] md:text-xs font-medium text-white/80">AI Status</span>
            </div>
            <p className="text-[9px] md:text-xs text-white/60">DeepSeek 3.0</p>
            <p className="text-[8px] md:text-[10px] text-white/40">Real-time analysis</p>
          </div>
        </motion.div>
      </div>
    </>
  );

  // Desktop sidebar - always visible
  if (!isMobile) {
    return (
      <aside className="hidden md:flex md:flex-col md:w-64 lg:w-72 flex-shrink-0 h-screen glass-premium border-r border-white/10">
        {sidebarContent}
      </aside>
    );
  }

  // Mobile sidebar - drawer
  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 rounded-lg bg-white/10 backdrop-blur-lg border border-white/10"
      >
        <Menu className="h-5 w-5 text-white" />
      </button>

      {/* Mobile overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed left-0 top-0 z-50 w-72 h-screen glass-premium border-r border-white/10 md:hidden"
            >
              <div className="flex justify-end p-4">
                <button
                  onClick={() => setIsMobileOpen(false)}
                  className="p-2 rounded-lg bg-white/10"
                >
                  <X className="h-5 w-5 text-white" />
                </button>
              </div>
              <div className="flex flex-col h-full">
                {sidebarContent}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
