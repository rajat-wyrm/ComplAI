"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/ui/glass-card";

interface RiskGaugeProps {
  value: number;
  size?: number;
  title?: string;
  subtitle?: string;
}

export function RiskGauge({ value, size = 260, title = "Global Risk Score", subtitle }: RiskGaugeProps) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const radius = size * 0.38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - animatedValue / 100);
  
  const getGradientColors = (val: number) => {
    if (val >= 70) return ["#ef4444", "#f97316"];
    if (val >= 40) return ["#eab308", "#f59e0b"];
    return ["#22c55e", "#10b981"];
  };
  
  const gradientColors = getGradientColors(value);
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 200);
    return () => clearTimeout(timer);
  }, [value]);
  
  return (
    <GlassCard className="p-6 text-center group" premium glow>
      <div className="relative">
        <h3 className="text-sm font-medium text-white/60 mb-2">{title}</h3>
        {subtitle && <p className="text-xs text-white/40 mb-4">{subtitle}</p>}
        
        <div className="relative flex justify-center py-4">
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
            <defs>
              <linearGradient id="riskGaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={gradientColors[0]} />
                <stop offset="100%" stopColor={gradientColors[1]} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth={size * 0.08}
            />
            
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="url(#riskGaugeGradient)"
              strokeWidth={size * 0.08}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 2, ease: "easeOut" }}
              style={{
                transformOrigin: `${size / 2}px ${size / 2}px`,
                transform: "rotate(-90deg)",
                filter: "url(#glow)",
              }}
            />
            
            <text
              x={size / 2}
              y={size / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-5xl font-bold fill-white"
            >
              {animatedValue}
              <tspan fontSize="24" className="fill-white/50">%</tspan>
            </text>
          </svg>
          
          <motion.div
            className="absolute inset-0 rounded-full blur-2xl opacity-40 group-hover:opacity-70 transition-opacity"
            style={{
              background: `radial-gradient(circle, ${gradientColors[0]} 0%, transparent 70%)`,
            }}
            animate={{
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: "reverse",
            }}
          />
        </div>
        
        <div className="flex justify-between mt-2 text-xs text-white/40">
          <span>Low Risk</span>
          <span>Medium</span>
          <span>High Risk</span>
        </div>
        <div className="h-1 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full mt-3" />
      </div>
    </GlassCard>
  );
}
