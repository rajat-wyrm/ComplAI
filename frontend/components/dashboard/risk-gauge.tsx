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

export function RiskGauge({ value, size = 200, title = "Global Risk Score", subtitle }: RiskGaugeProps) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const [windowWidth, setWindowWidth] = useState(200);
  
  useEffect(() => {
    const updateSize = () => {
      if (window.innerWidth < 640) setWindowWidth(160);
      else if (window.innerWidth < 768) setWindowWidth(180);
      else setWindowWidth(size);
    };
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [size]);
  
  const radius = windowWidth * 0.38;
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
    <GlassCard className="p-3 sm:p-4 md:p-6 text-center group" premium glow>
      <div className="relative">
        <h3 className="text-xs sm:text-sm font-medium text-white/60 mb-1 sm:mb-2">{title}</h3>
        {subtitle && <p className="text-[9px] sm:text-xs text-white/40 mb-2 sm:mb-4">{subtitle}</p>}
        
        <div className="relative flex justify-center py-2 sm:py-3">
          <svg width={windowWidth} height={windowWidth} viewBox={`0 0 ${windowWidth} ${windowWidth}`}>
            <defs>
              <linearGradient id="riskGaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={gradientColors[0]} />
                <stop offset="100%" stopColor={gradientColors[1]} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <circle
              cx={windowWidth / 2}
              cy={windowWidth / 2}
              r={radius}
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth={windowWidth * 0.08}
            />
            
            <motion.circle
              cx={windowWidth / 2}
              cy={windowWidth / 2}
              r={radius}
              fill="none"
              stroke="url(#riskGaugeGradient)"
              strokeWidth={windowWidth * 0.08}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 2, ease: "easeOut" }}
              style={{
                transformOrigin: `${windowWidth / 2}px ${windowWidth / 2}px`,
                transform: "rotate(-90deg)",
                filter: "url(#glow)",
              }}
            />
            
            <text
              x={windowWidth / 2}
              y={windowWidth / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-white text-2xl sm:text-3xl md:text-4xl font-bold"
            >
              {animatedValue}
              <tspan fontSize={windowWidth * 0.1} className="fill-white/50">%</tspan>
            </text>
          </svg>
          
          <motion.div
            className="absolute inset-0 rounded-full blur-xl opacity-40 group-hover:opacity-70 transition-opacity"
            style={{
              background: `radial-gradient(circle, ${gradientColors[0]} 0%, transparent 70%)`,
            }}
            animate={{
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: "reverse",
            }}
          />
        </div>
        
        <div className="flex justify-between mt-1 sm:mt-2 text-[8px] sm:text-xs text-white/40">
          <span>Low Risk</span>
          <span>Medium</span>
          <span>High Risk</span>
        </div>
        <div className="h-0.5 sm:h-1 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full mt-2 sm:mt-3" />
      </div>
    </GlassCard>
  );
}
