"use client";

import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/ui/glass-card";

// Dynamic imports for performance
const LineChart = dynamic(() => import("recharts").then(mod => mod.LineChart), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(mod => mod.BarChart), { ssr: false });
const PieChart = dynamic(() => import("recharts").then(mod => mod.PieChart), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(mod => mod.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(mod => mod.Area), { ssr: false });
const Line = dynamic(() => import("recharts").then(mod => mod.Line), { ssr: false });
const Bar = dynamic(() => import("recharts").then(mod => mod.Bar), { ssr: false });
const Pie = dynamic(() => import("recharts").then(mod => mod.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(mod => mod.Cell), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(mod => mod.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import("recharts").then(mod => mod.ResponsiveContainer), { ssr: false });
const Legend = dynamic(() => import("recharts").then(mod => mod.Legend), { ssr: false });

interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  subtitle?: string;
}

export function ChartContainer({ title, children, subtitle }: ChartContainerProps) {
  return (
    <GlassCard className="p-6" premium>
      <div className="mb-4">
        <h3 className="text-sm font-medium text-white/80">{title}</h3>
        {subtitle && <p className="text-xs text-white/40 mt-1">{subtitle}</p>}
      </div>
      <div className="h-[320px]">{children}</div>
    </GlassCard>
  );
}

interface RiskTrendChartProps {
  data: Array<{ date: string; risk: number; confidence: number; threshold?: number }>;
}

export function RiskTrendChart({ data }: RiskTrendChartProps) {
  return (
    <ChartContainer title="Risk Trend Analysis" subtitle="30-day rolling average with confidence bands">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
              <feMerge>
                <feMergeNode in="offsetblur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
          <XAxis 
            dataKey="date" 
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
            tickLine={{ stroke: "rgba(255,255,255,0.1)" }}
          />
          <YAxis 
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
            tickLine={{ stroke: "rgba(255,255,255,0.1)" }}
            domain={[0, 100]}
          />
          
          <Tooltip
            contentStyle={{
              background: "rgba(10, 10, 20, 0.95)",
              backdropFilter: "blur(12px)",
              border: "1px solid rgba(139, 92, 246, 0.4)",
              borderRadius: "12px",
              padding: "12px 16px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
            }}
            labelStyle={{ color: "rgba(255,255,255,0.7)", fontSize: "12px" }}
            itemStyle={{ fontSize: "12px" }}
          />
          
          <Legend 
            wrapperStyle={{ color: "rgba(255,255,255,0.6)", fontSize: "12px" }}
            iconType="circle"
          />
          
          <Area
            type="monotone"
            dataKey="confidence"
            stroke="none"
            fill="url(#confidenceGradient)"
            fillOpacity={0.3}
          />
          
          <Line
            type="monotone"
            dataKey="risk"
            stroke="url(#riskGradient)"
            strokeWidth={3}
            dot={{ fill: "#a855f7", strokeWidth: 2, r: 4, stroke: "rgba(139,92,246,0.5)" }}
            activeDot={{ r: 8, fill: "#a855f7", stroke: "white", strokeWidth: 2 }}
            animationDuration={1500}
            animationEasing="ease-out"
          />
          
          <Line
            type="monotone"
            dataKey="threshold"
            stroke="#f97316"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface ComplianceBarChartProps {
  data: Array<{ category: string; score: number; target?: number }>;
}

export function ComplianceBarChart({ data }: ComplianceBarChartProps) {
  return (
    <ChartContainer title="Compliance by Category" subtitle="Score vs target threshold">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} layout="vertical">
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#a855f7"/>
              <stop offset="100%" stopColor="#3b82f6"/>
            </linearGradient>
            <linearGradient id="targetGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#f97316"/>
              <stop offset="100%" stopColor="#ef4444"/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" horizontal={false} />
          <XAxis 
            type="number"
            domain={[0, 100]}
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
          />
          <YAxis 
            dataKey="category" 
            type="category"
            stroke="rgba(255,255,255,0.3)" 
            tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }}
            width={80}
          />
          
          <Tooltip
            contentStyle={{
              background: "rgba(10, 10, 20, 0.95)",
              backdropFilter: "blur(12px)",
              border: "1px solid rgba(139, 92, 246, 0.4)",
              borderRadius: "12px",
              padding: "12px 16px",
            }}
          />
          
          <Legend wrapperStyle={{ color: "rgba(255,255,255,0.6)", fontSize: "12px" }} />
          
          <Bar 
            dataKey="score" 
            fill="url(#barGradient)" 
            radius={[0, 8, 8, 0]}
            animationDuration={1200}
            animationEasing="ease-out"
            label={{ 
              position: 'right', 
              fill: 'rgba(255,255,255,0.7)', 
              fontSize: 11,
              formatter: (value: number) => `${value}%`
            }}
          />
          
          <Bar 
            dataKey="target" 
            fill="url(#targetGradient)" 
            radius={[0, 8, 8, 0]}
            fillOpacity={0.5}
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface RiskDistributionProps {
  data: Array<{ name: string; value: number; color: string }>;
}

export function RiskDistribution({ data }: RiskDistributionProps) {
  return (
    <ChartContainer title="Risk Distribution" subtitle="By severity level">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <defs>
            {data.map((item, index) => (
              <linearGradient key={index} id={`pieGradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={item.color} stopOpacity={0.9}/>
                <stop offset="100%" stopColor={item.color} stopOpacity={0.5}/>
              </linearGradient>
            ))}
            <filter id="pieGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
              <feMerge>
                <feMergeNode in="offsetblur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
            animationDuration={1500}
            animationEasing="ease-out"
            label={({ name, percent }) => `${name}\n${(percent * 100).toFixed(0)}%`}
            labelLine={{ stroke: "rgba(255,255,255,0.3)", strokeWidth: 1 }}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={`url(#pieGradient-${index})`} 
                stroke="rgba(255,255,255,0.2)" 
                strokeWidth={2}
                style={{ filter: "url(#pieGlow)" }}
              />
            ))}
          </Pie>
          
          <Tooltip
            contentStyle={{
              background: "rgba(10, 10, 20, 0.95)",
              backdropFilter: "blur(12px)",
              border: "1px solid rgba(139, 92, 246, 0.4)",
              borderRadius: "12px",
              padding: "8px 12px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface RiskHeatmapProps {
  data: Array<{ category: string; risk: number; impact: number }>;
}

export function RiskHeatmap({ data }: RiskHeatmapProps) {
  return (
    <ChartContainer title="Risk Heatmap" subtitle="Impact vs Likelihood">
      <div className="grid grid-cols-2 gap-2 h-full">
        {data.map((item, idx) => (
          <motion.div
            key={item.category}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
            className="p-3 rounded-xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10"
          >
            <p className="text-xs text-white/60">{item.category}</p>
            <div className="mt-2 space-y-1">
              <div>
                <p className="text-[10px] text-white/40">Risk Score</p>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${item.risk}%` }}
                    transition={{ duration: 1, delay: idx * 0.1 }}
                  />
                </div>
                <p className="text-[10px] text-white/60 mt-0.5">{item.risk}%</p>
              </div>
              <div>
                <p className="text-[10px] text-white/40">Impact Score</p>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${item.impact}%` }}
                    transition={{ duration: 1, delay: idx * 0.15 }}
                  />
                </div>
                <p className="text-[10px] text-white/60 mt-0.5">{item.impact}%</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </ChartContainer>
  );
}
