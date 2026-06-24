"use client";

import { motion } from "framer-motion";
import type { HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends HTMLMotionProps<"div"> {
  glow?: boolean;
  animated?: boolean;
  gradient?: boolean;
  premium?: boolean;
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, children, glow = true, animated = true, gradient = false, premium = true, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        whileHover={animated ? { y: -2, transition: { duration: 0.2 } } : undefined}
        className={cn(
          premium ? "glass-card-premium" : "glass-ultra",
          glow && "hover:glow-purple-hover",
          gradient && "border-gradient-animated",
          "transition-all duration-300",
          className
        )}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = "GlassCard";
