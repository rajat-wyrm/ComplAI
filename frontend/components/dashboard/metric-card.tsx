"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { GlassCard } from "@/components/ui/glass-card";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  trend?: number[];
  color?: string;
  subtitle?: string;
}

export function MetricCard({ title, value, change, icon, trend, color = "purple", subtitle }: MetricCardProps) {
  const isPositive = change && change > 0;
  
  const colorGradients = {
    purple: "from-purple-500/30 to-purple-600/20",
    blue: "from-blue-500/30 to-cyan-500/20",
    green: "from-emerald-500/30 to-green-500/20",
    red: "from-red-500/30 to-orange-500/20",
    indigo: "from-indigo-500/30 to-purple-500/20",
  };
  
  return (
    <GlassCard className="p-5 group relative overflow-hidden" premium>
      {/* Animated background gradient */}
      <div className={cn(
        "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
        "bg-gradient-to-br",
        colorGradients[color as keyof typeof colorGradients]
      )} />
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div className={cn(
            "p-2.5 rounded-xl bg-gradient-to-br",
            colorGradients[color as keyof typeof colorGradients]
          )}>
            {icon}
          </div>
          {change !== undefined && (
            <div className={cn(
              "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium backdrop-blur-sm",
              isPositive ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
            )}>
              {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              <span>{Math.abs(change)}%</span>
            </div>
          )}
        </div>
        
        <div>
          <p className="text-xs text-white/50 uppercase tracking-wider mb-1">{title}</p>
          <p className="text-3xl font-bold gradient-text-premium">{value}</p>
          {subtitle && <p className="text-xs text-white/40 mt-1">{subtitle}</p>}
        </div>
        
        {trend && (
          <div className="mt-4 h-10">
            <svg width="100%" height="40" viewBox="0 0 200 40" className="sparkline">
              <defs>
                <linearGradient id={`sparkline-${title}`} x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
              </defs>
              <polyline
                points={trend.map((v, i) => `${i * (200 / (trend.length - 1))},${40 - (v / 100) * 32}`).join(" ")}
                fill="none"
                stroke={`url(#sparkline-${title})`}
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>
        )}
      </div>
    </GlassCard>
  );
}
