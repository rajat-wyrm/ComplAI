"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { GlassCard } from "./glass-card";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  trend?: number[];
  color?: string;
}

export function MetricCard({ title, value, change, icon, trend, color = "purple" }: MetricCardProps) {
  const isPositive = change && change > 0;
  
  return (
    <GlassCard className="p-6 group">
      <div className="flex items-start justify-between mb-4">
        <div className={cn(
          "p-3 rounded-xl bg-gradient-to-br",
          color === "purple" && "from-purple-500/20 to-purple-600/20",
          color === "blue" && "from-blue-500/20 to-cyan-500/20",
          color === "green" && "from-emerald-500/20 to-green-500/20",
          color === "red" && "from-red-500/20 to-orange-500/20"
        )}>
          {icon}
        </div>
        {change !== undefined && (
          <div className={cn(
            "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
            isPositive ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
          )}>
            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>
      
      <div>
        <p className="text-sm text-white/60 mb-1">{title}</p>
        <p className="text-3xl font-bold gradient-text">{value}</p>
      </div>
      
      {trend && (
        <div className="mt-4 h-12">
          <svg width="100%" height="48" viewBox="0 0 200 48" className="opacity-50 group-hover:opacity-100 transition-opacity">
            <polyline
              points={trend.map((v, i) => `${i * (200 / (trend.length - 1))},${48 - (v / 100) * 40}`).join(" ")}
              fill="none"
              stroke="url(#gradient)"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#a855f7" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      )}
    </GlassCard>
  );
}
