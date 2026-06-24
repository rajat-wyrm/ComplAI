"use client";

import { motion } from "framer-motion";
import { Bell, Search, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function TopBar() {
  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-premium sticky top-0 z-30 border-b border-white/10"
    >
      <div className="flex items-center justify-between px-4 md:px-6 py-3 md:py-4">
        <div className="flex items-center gap-4 flex-1">
          {/* Mobile menu button handled by Sidebar */}
          <div className="hidden md:flex relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
            <Input
              placeholder="Search documents, risks, or compliance issues..."
              className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-purple-500/50 focus:ring-purple-500/20"
            />
          </div>
        </div>

        <div className="flex items-center gap-1 md:gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="text-white/70 hover:text-white hover:bg-white/10 relative"
          >
            <Bell className="h-4 w-4 md:h-5 md:w-5" />
            <span className="absolute top-1 right-1 h-1.5 w-1.5 md:h-2 md:w-2 bg-purple-500 rounded-full animate-pulse" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            className="text-white/70 hover:text-white hover:bg-white/10 hidden sm:flex"
          >
            <Settings className="h-4 w-4 md:h-5 md:w-5" />
          </Button>
          
          <div className="h-5 w-px bg-white/10 mx-1 md:mx-2 hidden sm:block" />
          
          <Button
            variant="ghost"
            className="flex items-center gap-1 md:gap-2 text-white/70 hover:text-white hover:bg-white/10 px-2 md:px-3"
          >
            <div className="h-6 w-6 md:h-8 md:w-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
              <User className="h-3 w-3 md:h-4 md:w-4" />
            </div>
            <span className="hidden md:inline text-sm">Enterprise Admin</span>
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
