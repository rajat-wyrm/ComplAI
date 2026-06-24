"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  ArrowLeft, AlertTriangle, CheckCircle2, Lightbulb, 
  Shield, Clock, Loader2, RefreshCw, TrendingUp, 
  AlertCircle, Zap
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { GlassCard } from "@/components/ui/glass-card";
import { getInsights, analyzeDocument } from "@/lib/api";
import type { InsightResponse } from "@/lib/api";

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params.id as string;
  const [analysis, setAnalysis] = useState<InsightResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalysis = useCallback(async () => {
    try {
      const data = await getInsights(documentId);
      setAnalysis(data);
    } catch (error) {
      console.error("Failed to fetch analysis:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [documentId]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await analyzeDocument(documentId);
    setTimeout(() => {
      fetchAnalysis();
    }, 3000);
  };

  useEffect(() => {
    fetchAnalysis();
  }, [documentId, fetchAnalysis]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (!analysis || analysis.status === "pending" || analysis.status === "processing") {
    return (
      <div className="text-center py-20">
        <Clock className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-2xl font-semibold mb-2">Analysis in Progress</h2>
        <p className="text-muted-foreground mb-6">
          Our AI is analyzing your document for compliance risks
        </p>
        <Button onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Refreshing...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Check Status
            </>
          )}
        </Button>
      </div>
    );
  }

  const riskScore = analysis.risk_score || 0;
  const confidenceScore = analysis.confidence_score || 0;
  const riskLevel = riskScore >= 70 ? "High" : riskScore >= 40 ? "Medium" : "Low";
  const riskColor = riskScore >= 70 ? "text-red-500" : riskScore >= 40 ? "text-yellow-500" : "text-green-500";
  const riskBg = riskScore >= 70 ? "bg-red-500/10" : riskScore >= 40 ? "bg-yellow-500/10" : "bg-green-500/10";

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center gap-4"
      >
        <Button variant="ghost" size="icon" onClick={() => router.back()} className="text-white/70 hover:text-white">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold gradient-text-premium">Risk Analysis</h1>
          <p className="text-white/40 mt-1">{analysis.filename}</p>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
        <GlassCard className={`p-6 ${riskBg}`} premium>
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="text-center md:text-left">
              <p className="text-sm text-white/60 mb-1">Overall Risk Score</p>
              <div className={`text-5xl md:text-6xl font-bold ${riskColor}`}>
                {riskScore.toFixed(0)}<span className="text-2xl">/100</span>
              </div>
              <Badge className={`mt-3 ${riskBg} ${riskColor}`}>{riskLevel} Risk</Badge>
            </div>
            <div className="text-center">
              <p className="text-sm text-white/60 mb-1">Confidence Level</p>
              <div className="text-3xl md:text-4xl font-bold text-primary">
                {confidenceScore.toFixed(0)}%
              </div>
              <Progress value={confidenceScore} className="mt-2 w-32 h-2" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-white/60 mb-2">Risk Trend</p>
              <div className="flex items-center gap-2">
                <TrendingUp className={`h-5 w-5 ${riskScore > 50 ? "text-red-400" : "text-green-400"}`} />
                <span className="text-sm text-white/60">
                  {riskScore > 50 ? "Above threshold - Action required" : "Below threshold - Monitor"}
                </span>
              </div>
            </div>
          </div>
          <div className="mt-4">
            <Progress value={riskScore} className="h-2" />
            <p className="text-sm text-white/40 mt-3">{analysis.explanation || "Analysis completed. Review risks below."}</p>
          </div>
        </GlassCard>
      </motion.div>

      {analysis.risks && analysis.risks.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="glass-card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                Identified Risks ({analysis.risks.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analysis.risks.map((risk, index) => (
                  <div key={index} className="p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg">{risk.category}</h4>
                        <p className="text-sm text-white/60 mt-1">{risk.description}</p>
                      </div>
                      <Badge variant="outline" className={
                        risk.severity === "high" ? "border-red-500 text-red-500" :
                        risk.severity === "medium" ? "border-yellow-500 text-yellow-500" :
                        "border-green-500 text-green-500"
                      }>
                        {risk.severity.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm mt-2">
                      <span className="text-white/40">Impact: </span>
                      <span className="text-white/80">{risk.impact}</span>
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {analysis.recommended_actions && analysis.recommended_actions.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="glass-card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                Recommended Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysis.recommended_actions.map((action, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-primary/5">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5" />
                    <span className="text-sm">{action}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {analysis.compliance_gaps && analysis.compliance_gaps.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card className="glass-card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Compliance Gaps
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {analysis.compliance_gaps.map((gap, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 rounded-lg bg-red-500/5">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm">{gap}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }} className="text-center text-sm text-white/40 pt-4">
        <Separator className="mb-4" />
        <div className="flex items-center justify-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="h-3 w-3 text-purple-400" />
            <span>Powered by DeepSeek AI</span>
          </div>
          <span>•</span>
          <span>Analysis ID: {analysis.analysis_id?.slice(0, 8)}...</span>
        </div>
      </motion.div>
    </div>
  );
}
