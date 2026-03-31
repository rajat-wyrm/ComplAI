'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  getInsights,
  getDocumentAnalysis,
} from '@/lib/api';

export default function DashboardPage() {
  const params = useSearchParams();
  const docId = params.get('docId');

  const [report, setReport] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [document, setDocument] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();

    // 🔥 REAL-TIME REFRESH
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, [docId]);

  const load = async () => {
    try {
      setLoading(true);

      // 🔥 FETCH SELECTED DOCUMENT
      if (docId) {
        const res = await getDocumentAnalysis(docId);
        if (res?.document) {
          setDocument(res.document);
          setReport(res.document.analysis || res.document.report);
        }
      }

      // 🔥 FALLBACK
      if (!report) {
        const latest = localStorage.getItem('latestAnalysis');
        if (latest) {
          const parsed = JSON.parse(latest);
          setReport(parsed.report);
        }
      }

      // 🔥 ANALYTICS
      const ins = await getInsights();
      setAnalytics(ins.data);

    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // EXPORT REPORT
  // =========================
  const exportReport = () => {
    if (!report) return;

    const content = `
AI Compliance Report

Summary:
${report.summary}

Risk Score: ${report.risk_score}
Compliance Score: ${report.compliance_score}
Confidence: ${report.confidence_score}

Issues:
${report.issues?.map((i:any)=>`- ${i.title}: ${i.description}`).join('\n')}
    `;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'ai_report.txt';
    a.click();
  };

  // =========================
  // LOADING UI
  // =========================
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-black text-white">
        ⚡ AI Processing...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-purple-900 to-black text-white p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            AI Compliance Intelligence
          </h1>

          {document && (
            <p className="text-gray-400 text-sm mt-1">
              📄 {document.filename} • {new Date(document.upload_date).toLocaleString()}
            </p>
          )}
        </div>

        <button
          onClick={exportReport}
          className="px-4 py-2 bg-purple-600 rounded-xl hover:bg-purple-700 transition"
        >
          Export Report
        </button>
      </div>

      {/* ========================= */}
      {/* METRICS */}
      {/* ========================= */}
      <div className="grid md:grid-cols-5 gap-6 mb-8">

        <Metric title="Risk" value={report?.risk_score} color="red" />
        <Metric title="Compliance" value={report?.compliance_score} color="blue" />
        <Metric title="Issues" value={report?.issues?.length} color="orange" />
        <Metric title="Confidence" value={report?.confidence_score} color="green" />
        <Metric title="Documents" value={analytics?.total_documents} color="purple" />

      </div>

      {/* ========================= */}
      {/* MAIN GRID */}
      {/* ========================= */}
      <div className="grid lg:grid-cols-3 gap-6">

        {/* LEFT SIDE */}
        <div className="lg:col-span-2 space-y-6">

          {/* SUMMARY */}
          <Glass>
            <h3 className="title">AI Summary</h3>
            <p className="text-gray-300">{report?.summary}</p>
          </Glass>

          {/* ISSUES */}
          <Glass>
            <h3 className="title">Detected Issues</h3>

            <div className="space-y-3 mt-3">
              {report?.issues?.map((i:any, idx:number)=>(
                <div key={idx} className="p-3 rounded-xl bg-white/5 border border-white/10">

                  <div className="flex justify-between">
                    <span>{i.title}</span>
                    <span className={`text-xs ${
                      i.severity === 'high' ? 'text-red-400' :
                      i.severity === 'medium' ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {i.severity}
                    </span>
                  </div>

                  <p className="text-gray-400 text-sm">{i.description}</p>

                  <p className="text-purple-300 text-sm mt-1">
                    💡 {i.recommendation}
                  </p>

                </div>
              ))}
            </div>
          </Glass>

          {/* RISK CHART */}
          <Glass>
            <h3 className="title">Risk Trend</h3>

            <div className="flex items-end gap-2 h-32 mt-4">
              {analytics?.risk_trend?.map((p:any,i:number)=>(
                <div
                  key={i}
                  className="w-4 bg-purple-500 rounded"
                  style={{ height: `${p.risk_score}%` }}
                />
              ))}
            </div>
          </Glass>

        </div>

        {/* RIGHT SIDE */}
        <div className="space-y-6">

          {/* AI SUGGESTIONS */}
          <Glass>
            <h3 className="title">AI Suggestions</h3>
            {report?.issues?.map((i:any, idx:number)=>(
              <p key={idx} className="text-purple-300 text-sm">
                💡 {i.recommendation}
              </p>
            ))}
          </Glass>

          {/* SENSITIVE DATA */}
          {report?.sensitive_data?.length > 0 && (
            <Glass>
              <h3 className="title text-red-400">Sensitive Data</h3>
              {report.sensitive_data.map((s:string,i:number)=>(
                <p key={i}>• {s}</p>
              ))}
            </Glass>
          )}

          {/* MISSING */}
          {report?.missing_items?.length > 0 && (
            <Glass>
              <h3 className="title text-yellow-400">Missing Compliance</h3>
              {report.missing_items.map((m:string,i:number)=>(
                <p key={i}>• {m}</p>
              ))}
            </Glass>
          )}

          {/* SYSTEM */}
          <Glass>
            <h3 className="title">System Status</h3>
            <p className="text-green-400">✔ AI Active</p>
            <p className="text-green-400">✔ Real-time Analysis</p>
          </Glass>

        </div>
      </div>
    </div>
  );
}


/* ========================= */
/* COMPONENTS */
/* ========================= */

function Glass({ children }: any) {
  return (
    <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10">
      {children}
    </div>
  );
}

function Metric({ title, value, color }: any) {
  return (
    <div className="p-6 bg-white/5 rounded-xl border border-white/10 backdrop-blur-xl">
      <p className="text-gray-400 text-sm">{title}</p>
      <p className={`text-3xl font-bold text-${color}-400`}>
        {value ?? '--'}
      </p>
    </div>
  );
}