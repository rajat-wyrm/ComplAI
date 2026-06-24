'use client';

import { motion } from "framer-motion";
import * as Recharts from "recharts";
import { GlassCard } from "@/components/ui/glass-card";

interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  subtitle?: string;
}

interface RiskTrendPoint {
  date: string;
  risk_score: number;
}

interface ComplianceCategory {
  category: string;
  score: number;
}

interface RiskDistributionPoint {
  name: string;
  value: number;
}

interface HeatmapPoint {
  category: string;
  risk: number;
  impact: number;
}

interface BarProps {
  label: string;
  value: number;
  color: "purple" | "red" | "green" | "blue" | "yellow";
}

// =========================
// STYLES
// =========================
const axisStyle = {
  stroke: "rgba(255,255,255,0.2)",
  tick: { fill: "rgba(255,255,255,0.6)", fontSize: 11 }
};

const tooltipStyle = {
  background: "rgba(15, 15, 25, 0.95)",
  backdropFilter: "blur(12px)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "10px",
  color: "white",
  fontSize: "12px"
};

// =========================
// CONTAINER
// =========================
export function ChartContainer({ title, children, subtitle }: ChartContainerProps) {
  return (
    <GlassCard className="p-6 hover:scale-[1.01] transition" premium>
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-white/90">{title}</h3>
        {subtitle && <p className="text-xs text-white/40">{subtitle}</p>}
      </div>
      <div className="h-[300px]">{children}</div>
    </GlassCard>
  );
}

// =========================
// RISK TREND (REAL-TIME READY)
// =========================
export function RiskTrendChart({ data }: { data: RiskTrendPoint[] }) {
  if (!data || data.length === 0) return null;

  return (
    <ChartContainer title="Risk Trend" subtitle="Live AI monitoring">
      <Recharts.ResponsiveContainer width="100%" height="100%">
        <Recharts.LineChart data={data}>
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8}/>
              <stop offset="100%" stopColor="#a855f7" stopOpacity={0}/>
            </linearGradient>
          </defs>

          <Recharts.CartesianGrid stroke="rgba(255,255,255,0.08)" />
          <Recharts.XAxis dataKey="date" {...axisStyle} />
          <Recharts.YAxis domain={[0, 100]} {...axisStyle} />

          <Recharts.Tooltip contentStyle={tooltipStyle} />

          <Recharts.Area
            type="monotone"
            dataKey="risk_score"
            fill="url(#riskGradient)"
            stroke="none"
          />

          <Recharts.Line
            type="monotone"
            dataKey="risk_score"
            stroke="#a855f7"
            strokeWidth={2.5}
            dot={false}
          />
        </Recharts.LineChart>
      </Recharts.ResponsiveContainer>
    </ChartContainer>
  );
}

// =========================
// COMPLIANCE BAR (SMART COLORS)
// =========================
export function ComplianceBarChart({ data }: { data: ComplianceCategory[] }) {
  return (
    <ChartContainer title="Compliance Categories">
      <Recharts.ResponsiveContainer width="100%" height="100%">
        <Recharts.BarChart data={data} layout="vertical">

          <Recharts.XAxis type="number" domain={[0, 100]} {...axisStyle} />
          <Recharts.YAxis type="category" dataKey="category" {...axisStyle} />
          <Recharts.Tooltip contentStyle={tooltipStyle} />

          <Recharts.Bar dataKey="score" radius={[0, 8, 8, 0]}>
            {data.map((entry: ComplianceCategory, i: number) => (
              <Recharts.Cell
                key={i}
                fill={
                  entry.score > 80
                    ? "#22c55e"
                    : entry.score > 50
                    ? "#eab308"
                    : "#ef4444"
                }
              />
            ))}
          </Recharts.Bar>
        </Recharts.BarChart>
      </Recharts.ResponsiveContainer>
    </ChartContainer>
  );
}

// =========================
// RISK DISTRIBUTION (DONUT)
// =========================
export function RiskDistribution({ data }: { data: RiskDistributionPoint[] }) {
  return (
    <ChartContainer title="Risk Distribution">
      <Recharts.ResponsiveContainer width="100%" height="100%">
        <Recharts.PieChart>
          <Recharts.Pie
            data={data}
            innerRadius={60}
            outerRadius={90}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((_, i: number) => (
              <Recharts.Cell
                key={i}
                fill={["#22c55e", "#eab308", "#ef4444"][i]}
              />
            ))}
          </Recharts.Pie>

          <Recharts.Tooltip contentStyle={tooltipStyle} />
        </Recharts.PieChart>
      </Recharts.ResponsiveContainer>
    </ChartContainer>
  );
}

// =========================
// HEATMAP (AI VISUAL)
// =========================
export function RiskHeatmap({ data }: { data: HeatmapPoint[] }) {
  return (
    <ChartContainer title="AI Risk Heatmap">
      <div className="grid grid-cols-2 gap-3">

        {data.map((item: HeatmapPoint, i: number) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="p-3 rounded-xl bg-white/5 border border-white/10"
          >
            <p className="text-xs text-white/60">{item.category}</p>

            <Bar label="Risk" value={item.risk} color="purple" />
            <Bar label="Impact" value={item.impact} color="red" />

          </motion.div>
        ))}

      </div>
    </ChartContainer>
  );
}


// =========================
// SMALL BAR COMPONENT
// =========================
function Bar({ label, value, color }: BarProps) {
  return (
    <div className="mt-2">
      <p className="text-[10px] text-white/40">{label}</p>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className={`h-full bg-${color}-500`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
