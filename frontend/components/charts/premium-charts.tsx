"use client";

import dynamic from "next/dynamic";
import { GlassCard } from "@/components/ui/glass-card";

// Dynamic imports for better performance
const LineChart = dynamic(() => import("recharts").then(mod => mod.LineChart), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(mod => mod.BarChart), { ssr: false });
const PieChart = dynamic(() => import("recharts").then(mod => mod.PieChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(mod => mod.Line), { ssr: false });
const Bar = dynamic(() => import("recharts").then(mod => mod.Bar), { ssr: false });
const Pie = dynamic(() => import("recharts").then(mod => mod.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(mod => mod.Cell), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(mod => mod.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import("recharts").then(mod => mod.ResponsiveContainer), { ssr: false });

interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
}

export function ChartContainer({ title, children }: ChartContainerProps) {
  return (
    <GlassCard className="p-6">
      <h3 className="text-sm font-medium text-white/60 mb-4">{title}</h3>
      <div className="h-[300px]">{children}</div>
    </GlassCard>
  );
}

interface RiskTrendChartProps {
  data: Array<{ date: string; risk: number; confidence: number }>;
}

export function RiskTrendChart({ data }: RiskTrendChartProps) {
  return (
    <ChartContainer title="Risk Trend Analysis">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.4)" }} />
          <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.4)" }} />
          <Tooltip
            contentStyle={{
              background: "rgba(0,0,0,0.8)",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(139,92,246,0.3)",
              borderRadius: "8px",
            }}
          />
          <Line
            type="monotone"
            dataKey="risk"
            stroke="url(#riskGradient)"
            strokeWidth={3}
            dot={{ fill: "#a855f7", strokeWidth: 2 }}
            activeDot={{ r: 8 }}
          />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

interface ComplianceBarChartProps {
  data: Array<{ category: string; score: number }>;
}

export function ComplianceBarChart({ data }: ComplianceBarChartProps) {
  return (
    <ChartContainer title="Compliance by Category">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7"/>
              <stop offset="100%" stopColor="#3b82f6"/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="category" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.4)" }} />
          <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.4)" }} />
          <Tooltip
            contentStyle={{
              background: "rgba(0,0,0,0.8)",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(139,92,246,0.3)",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="score" fill="url(#barGradient)" radius={[8, 8, 0, 0]} />
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
    <ChartContainer title="Risk Distribution">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <defs>
            {data.map((item, index) => (
              <linearGradient key={index} id={`pieGradient${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={item.color} stopOpacity={0.8}/>
                <stop offset="100%" stopColor={item.color} stopOpacity={0.4}/>
              </linearGradient>
            ))}
          </defs>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
            labelLine={{ stroke: "rgba(255,255,255,0.3)" }}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={`url(#pieGradient${index})`} stroke="rgba(255,255,255,0.1)" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "rgba(0,0,0,0.8)",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(139,92,246,0.3)",
              borderRadius: "8px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
