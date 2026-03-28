"use client";

import { motion } from "framer-motion";
import { FileText, Shield, AlertTriangle, CheckCircle2, TrendingUp, Activity, Zap } from "lucide-react";
import { MetricCard } from "@/components/dashboard/metric-card";
import { RiskGauge } from "@/components/dashboard/risk-gauge";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { RiskTrendChart, ComplianceBarChart, RiskDistribution } from "@/components/charts/premium-charts";

// Mock data for premium dashboard
const mockRiskTrend = [
  { date: "Mon", risk: 45, confidence: 82 },
  { date: "Tue", risk: 48, confidence: 84 },
  { date: "Wed", risk: 52, confidence: 86 },
  { date: "Thu", risk: 58, confidence: 85 },
  { date: "Fri", risk: 55, confidence: 87 },
  { date: "Sat", risk: 62, confidence: 88 },
  { date: "Sun", risk: 68, confidence: 89 },
];

const mockComplianceData = [
  { category: "GDPR", score: 72 },
  { category: "HIPAA", score: 85 },
  { category: "PCI DSS", score: 58 },
  { category: "SOC2", score: 91 },
  { category: "ISO 27001", score: 76 },
];

const mockRiskDistribution = [
  { name: "Critical", value: 15, color: "#ef4444" },
  { name: "High", value: 25, color: "#f97316" },
  { name: "Medium", value: 35, color: "#eab308" },
  { name: "Low", value: 25, color: "#22c55e" },
];

const mockActivities = [
  {
    id: "1",
    type: "upload" as const,
    title: "Contract_2024_Q1.pdf uploaded",
    description: "Size: 2.4 MB • 156 pages",
    time: "2 min ago",
  },
  {
    id: "2",
    type: "analysis" as const,
    title: "AI Analysis started",
    description: "Processing document for compliance risks",
    time: "5 min ago",
  },
  {
    id: "3",
    type: "risk" as const,
    title: "High-risk clause detected",
    description: "Section 4.2: Data sharing agreement missing",
    time: "12 min ago",
  },
  {
    id: "4",
    type: "complete" as const,
    title: "Annual Report analysis complete",
    description: "Risk score: 64/100 • 3 recommendations",
    time: "1 hour ago",
  },
  {
    id: "5",
    type: "upload" as const,
    title: "Vendor_Agreement.docx uploaded",
    description: "Size: 856 KB • 42 pages",
    time: "2 hours ago",
  },
];

export default function DashboardPage() {
  const globalRiskScore = 64;
  const complianceScore = 76;
  const activeIssues = 12;
  const confidenceLevel = 89;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold gradient-text">Analytics Dashboard</h1>
          <p className="text-white/40 mt-1">Real-time compliance risk monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5">
            <Activity className="h-4 w-4 text-green-400 animate-pulse" />
            <span className="text-sm text-white/60">Live Updates</span>
          </div>
        </div>
      </motion.div>

      {/* Metric Cards Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Global Risk Score"
          value={`${globalRiskScore}/100`}
          change={-8}
          icon={<Shield className="h-5 w-5" />}
          trend={[65, 62, 58, 64, 68, 66, 64]}
          color="purple"
        />
        <MetricCard
          title="Compliance Score"
          value={`${complianceScore}%`}
          change={+5}
          icon={<CheckCircle2 className="h-5 w-5" />}
          trend={[71, 73, 74, 75, 76, 76, 76]}
          color="blue"
        />
        <MetricCard
          title="Active Issues"
          value={activeIssues.toString()}
          change={+2}
          icon={<AlertTriangle className="h-5 w-5" />}
          trend={[8, 9, 10, 11, 12, 12, 12]}
          color="red"
        />
        <MetricCard
          title="Confidence Level"
          value={`${confidenceLevel}%`}
          change={+3}
          icon={<TrendingUp className="h-5 w-5" />}
          trend={[82, 84, 85, 86, 87, 88, 89]}
          color="green"
        />
      </div>

      {/* Main Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RiskTrendChart data={mockRiskTrend} />
        <ComplianceBarChart data={mockComplianceData} />
      </div>

      {/* Risk Gauge and Distribution Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RiskGauge value={globalRiskScore} size={280} title="Enterprise Risk Score" />
        <RiskDistribution data={mockRiskDistribution} />
      </div>

      {/* Activity Feed */}
      <div className="grid gap-6">
        <ActivityFeed activities={mockActivities} />
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex items-center justify-between pt-4 border-t border-white/10"
      >
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-purple-400" />
          <span className="text-xs text-white/40">Powered by DeepSeek AI</span>
        </div>
        <div className="text-xs text-white/40">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </motion.div>
    </div>
  );
}
