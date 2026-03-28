"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
  animated?: boolean;
  gradient?: boolean;
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, children, glow = true, animated = true, gradient = false, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        whileHover={animated ? { y: -4, transition: { duration: 0.2 } } : undefined}
        className={cn(
          "relative rounded-2xl backdrop-blur-xl border transition-all duration-300",
          gradient ? "bg-gradient-to-br from-white/5 to-white/0" : "bg-white/5",
          glow && "hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]",
          "border-white/10 hover:border-purple-500/30",
          className
        )}
        {...props}
      >
        {gradient && (
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = "GlassCard";
