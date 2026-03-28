"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/ui/glass-card";

interface RiskGaugeProps {
  value: number;
  size?: number;
  title?: string;
}

export function RiskGauge({ value, size = 200, title = "Global Risk Score" }: RiskGaugeProps) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const radius = size * 0.4;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - animatedValue / 100);
  
  const getColor = (val: number) => {
    if (val >= 70) return "#ef4444";
    if (val >= 40) return "#eab308";
    return "#22c55e";
  };
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);
  
  return (
    <GlassCard className="p-6 text-center" glow>
      <h3 className="text-sm text-white/60 mb-4">{title}</h3>
      
      <div className="relative flex justify-center">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={size * 0.08}
          />
          
          {/* Gradient stroke */}
          <defs>
            <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22c55e" />
              <stop offset="40%" stopColor="#eab308" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
          </defs>
          
          {/* Animated progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="url(#riskGradient)"
            strokeWidth={size * 0.08}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{
              transformOrigin: `${size / 2}px ${size / 2}px`,
              transform: "rotate(-90deg)",
            }}
          />
          
          {/* Center text */}
          <text
            x={size / 2}
            y={size / 2}
            textAnchor="middle"
            dominantBaseline="middle"
            className="text-4xl font-bold fill-white"
          >
            {animatedValue}
            <tspan fontSize="20" className="fill-white/60">%</tspan>
          </text>
        </svg>
        
        {/* Glow effect */}
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-30"
          style={{
            background: `radial-gradient(circle, ${getColor(value)} 0%, transparent 70%)`,
          }}
        />
      </div>
      
      <div className="flex justify-between mt-4 text-xs text-white/40">
        <span>Low Risk</span>
        <span>Medium</span>
        <span>High Risk</span>
      </div>
      <div className="h-1 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full mt-2" />
    </GlassCard>
  );
}
