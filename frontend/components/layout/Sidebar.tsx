"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Upload,
  MessageSquare,
  History,
  Shield,
  Zap,
  BarChart3,
  FileCheck,
  Settings2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Analytics", href: "/", icon: LayoutDashboard, color: "from-blue-500 to-cyan-500" },
  { name: "Upload", href: "/upload", icon: Upload, color: "from-purple-500 to-pink-500" },
  { name: "AI Chat", href: "/chat", icon: MessageSquare, color: "from-indigo-500 to-purple-500" },
  { name: "History", href: "/history", icon: History, color: "from-teal-500 to-emerald-500" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed left-0 top-0 z-40 h-screen w-72 glass-premium border-r border-white/10"
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-20 items-center gap-3 px-6 border-b border-white/10">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl blur-lg opacity-50" />
            <Shield className="relative h-10 w-10 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold gradient-text">Compliance</span>
            <span className="text-xs text-white/50">Risk Copilot Enterprise</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 px-4 py-8">
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
                  className={cn(
                    "group relative flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300",
                    isActive
                      ? "bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white"
                      : "text-white/60 hover:text-white hover:bg-white/5"
                  )}
                >
                  <div className={cn(
                    "absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300",
                    isActive && "opacity-100",
                    !isActive && "group-hover:opacity-100"
                  )}>
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl" />
                  </div>
                  <item.icon className="relative h-5 w-5" />
                  <span className="relative">{item.name}</span>
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
        <div className="border-t border-white/10 p-4">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 p-4"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 animate-pulse" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4 text-purple-400" />
                <span className="text-xs font-medium text-white/80">AI Status</span>
              </div>
              <p className="text-xs text-white/60">DeepSeek 3.0</p>
              <p className="text-xs text-white/40">Real-time analysis</p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.aside>
  );
}
