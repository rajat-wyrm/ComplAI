"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Shield, CheckCircle2, AlertTriangle, TrendingUp, 
  Activity, Zap, Clock, Bell, Sparkles, Target 
} from "lucide-react";
import { MetricCard } from "@/components/dashboard/metric-card";
import { RiskGauge } from "@/components/dashboard/risk-gauge";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { GlassCard } from "@/components/ui/glass-card";
import { 
  RiskTrendChart, 
  ComplianceBarChart, 
  RiskDistribution,
  RiskHeatmap 
} from "@/components/charts/premium-charts";

// Mock data
const mockRiskTrend = [
  { date: "Mon", risk: 45, confidence: 82, threshold: 60 },
  { date: "Tue", risk: 48, confidence: 84, threshold: 60 },
  { date: "Wed", risk: 52, confidence: 86, threshold: 60 },
  { date: "Thu", risk: 58, confidence: 85, threshold: 60 },
  { date: "Fri", risk: 55, confidence: 87, threshold: 60 },
  { date: "Sat", risk: 62, confidence: 88, threshold: 60 },
  { date: "Sun", risk: 68, confidence: 89, threshold: 60 },
];

const mockComplianceData = [
  { category: "GDPR", score: 72, target: 80 },
  { category: "HIPAA", score: 85, target: 85 },
  { category: "PCI DSS", score: 58, target: 75 },
  { category: "SOC2", score: 91, target: 90 },
  { category: "ISO 27001", score: 76, target: 85 },
  { category: "CCPA", score: 68, target: 75 },
];

const mockRiskDistribution = [
  { name: "Critical", value: 15, color: "#ef4444" },
  { name: "High", value: 25, color: "#f97316" },
  { name: "Medium", value: 35, color: "#eab308" },
  { name: "Low", value: 25, color: "#22c55e" },
];

const mockRiskHeatmap = [
  { category: "Data Privacy", risk: 78, impact: 85 },
  { category: "Security Controls", risk: 45, impact: 62 },
  { category: "Third Party", risk: 82, impact: 70 },
  { category: "Regulatory", risk: 58, impact: 88 },
];

const mockActivities = [
  { id: "1", type: "upload" as const, title: "Contract_2024_Q1.pdf uploaded", description: "Size: 2.4 MB • 156 pages", time: "2 min ago" },
  { id: "2", type: "analysis" as const, title: "AI Analysis started", description: "Processing document for compliance risks", time: "5 min ago" },
  { id: "3", type: "risk" as const, title: "High-risk clause detected", description: "Section 4.2: Data sharing agreement missing", time: "12 min ago" },
  { id: "4", type: "complete" as const, title: "Annual Report analysis complete", description: "Risk score: 64/100 • 3 recommendations", time: "1 hour ago" },
  { id: "5", type: "upload" as const, title: "Vendor_Agreement.docx uploaded", description: "Size: 856 KB • 42 pages", time: "2 hours ago" },
  { id: "6", type: "risk" as const, title: "GDPR non-compliance detected", description: "Data retention policy missing", time: "3 hours ago" },
];

export default function DashboardPage() {
  const [currentTime, setCurrentTime] = useState("");
  const [mounted, setMounted] = useState(false);
  
  const globalRiskScore = 64;
  const complianceScore = 76;
  const activeIssues = 12;
  const confidenceLevel = 89;
  const pendingReviews = 5;
  const avgResolutionTime = "2.4d";

  useEffect(() => {
    setMounted(true);
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString());
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-4">
      {/* Header - Responsive */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-transparent to-blue-500/20 blur-3xl" />
        <div className="relative flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold gradient-text-premium">
              Analytics Dashboard
            </h1>
            <p className="text-xs sm:text-sm text-white/40 mt-1">
              Real-time compliance risk monitoring & intelligence
            </p>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-white/5 border border-white/10">
              <Activity className="h-3 w-3 sm:h-4 sm:w-4 text-green-400 animate-pulse" />
              <span className="text-xs sm:text-sm text-white/70">Live</span>
            </div>
            <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30">
              <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 text-purple-400" />
              <span className="text-xs sm:text-sm text-white/70">AI Active</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Metric Cards - Responsive Grid */}
      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <MetricCard
          title="Global Risk Score"
          value={`${globalRiskScore}/100`}
          change={-8}
          icon={<Shield className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[65, 62, 58, 64, 68, 66, 64]}
          color="purple"
          subtitle="vs last month"
        />
        <MetricCard
          title="Compliance Score"
          value={`${complianceScore}%`}
          change={+5}
          icon={<CheckCircle2 className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[71, 73, 74, 75, 76, 76, 76]}
          color="blue"
          subtitle="Target: 80%"
        />
        <MetricCard
          title="Active Issues"
          value={activeIssues.toString()}
          change={+2}
          icon={<AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[8, 9, 10, 11, 12, 12, 12]}
          color="red"
          subtitle="Critical: 3"
        />
        <MetricCard
          title="Confidence"
          value={`${confidenceLevel}%`}
          change={+3}
          icon={<TrendingUp className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[82, 84, 85, 86, 87, 88, 89]}
          color="green"
          subtitle="AI accuracy"
        />
        <MetricCard
          title="Pending Review"
          value={pendingReviews.toString()}
          change={-2}
          icon={<Clock className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[7, 6, 5, 5, 5, 5, 5]}
          color="indigo"
          subtitle="Awaiting action"
        />
        <MetricCard
          title="Avg Resolution"
          value={avgResolutionTime}
          change={-0.3}
          icon={<Target className="h-4 w-4 sm:h-5 sm:w-5" />}
          trend={[3.2, 2.9, 2.7, 2.6, 2.5, 2.4, 2.4]}
          color="blue"
          subtitle="days to close"
        />
      </div>

      {/* Main Charts - Responsive */}
      <div className="grid gap-4 sm:gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RiskTrendChart data={mockRiskTrend} />
        </div>
        <div className="lg:col-span-1">
          <ComplianceBarChart data={mockComplianceData} />
        </div>
      </div>

      {/* Middle Row - Responsive */}
      <div className="grid gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
        <RiskGauge value={globalRiskScore} size={220} title="Enterprise Risk Score" subtitle="vs industry benchmark: 58%" />
        <RiskDistribution data={mockRiskDistribution} />
        <RiskHeatmap data={mockRiskHeatmap} />
      </div>

      {/* Bottom Row - Responsive */}
      <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
        <ActivityFeed activities={mockActivities} />
        
        {/* Mini Stats Card */}
        <GlassCard className="p-4 sm:p-6" premium>
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h3 className="text-xs sm:text-sm font-medium text-white/80">Quick Insights</h3>
            <Bell className="h-3 w-3 sm:h-4 sm:w-4 text-white/40" />
          </div>
          <div className="space-y-3 sm:space-y-4">
            <div className="p-2 sm:p-3 rounded-xl bg-white/5">
              <div className="flex items-center justify-between mb-1 sm:mb-2">
                <span className="text-[10px] sm:text-xs text-white/60">Top Risk Category</span>
                <span className="text-[10px] sm:text-xs text-orange-400">High</span>
              </div>
              <p className="text-xs sm:text-sm font-medium">Third Party Risk Management</p>
              <div className="mt-1.5 sm:mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full w-[82%] bg-gradient-to-r from-orange-500 to-red-500 rounded-full" />
              </div>
            </div>
            <div className="p-2 sm:p-3 rounded-xl bg-white/5">
              <div className="flex items-center justify-between mb-1 sm:mb-2">
                <span className="text-[10px] sm:text-xs text-white/60">Improvement Areas</span>
                <span className="text-[10px] sm:text-xs text-green-400">+12%</span>
              </div>
              <p className="text-xs sm:text-sm font-medium">Data Governance</p>
              <p className="text-[10px] sm:text-xs text-white/40 mt-0.5 sm:mt-1">Up 12% from last quarter</p>
            </div>
            <div className="p-2 sm:p-3 rounded-xl bg-gradient-to-r from-purple-500/20 to-blue-500/20">
              <div className="flex items-center gap-1 sm:gap-2">
                <Zap className="h-3 w-3 sm:h-4 sm:w-4 text-purple-400" />
                <span className="text-[10px] sm:text-xs font-medium">AI Recommendation</span>
              </div>
              <p className="text-[11px] sm:text-sm mt-0.5 sm:mt-1">Review data retention policies in section 4.2</p>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Footer - Responsive */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 sm:pt-6 border-t border-white/10"
      >
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 justify-center sm:justify-start">
          <Zap className="h-3 w-3 sm:h-4 sm:w-4 text-purple-400" />
          <span className="text-[10px] sm:text-xs text-white/40">Powered by DeepSeek AI v3.0</span>
          <div className="h-3 w-px bg-white/20 hidden sm:block" />
          <span className="text-[10px] sm:text-xs text-white/40">Real-time analysis • 99.9% uptime</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-1.5 sm:h-2 sm:w-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-[10px] sm:text-xs text-white/40">Last updated: {currentTime}</span>
        </div>
      </motion.div>
    </div>
  );
}
