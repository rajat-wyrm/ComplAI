'use client';

import { useEffect, useState, useCallback, useMemo, Suspense, lazy } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';

// Lazy load charts
const LineChart = lazy(() => import('recharts').then(mod => ({ default: mod.LineChart })));
const Line = lazy(() => import('recharts').then(mod => ({ default: mod.Line })));
const XAxis = lazy(() => import('recharts').then(mod => ({ default: mod.XAxis })));
const YAxis = lazy(() => import('recharts').then(mod => ({ default: mod.YAxis })));
const CartesianGrid = lazy(() => import('recharts').then(mod => ({ default: mod.CartesianGrid })));
const Tooltip = lazy(() => import('recharts').then(mod => ({ default: mod.Tooltip })));
const Legend = lazy(() => import('recharts').then(mod => ({ default: mod.Legend })));
const ResponsiveContainer = lazy(() => import('recharts').then(mod => ({ default: mod.ResponsiveContainer })));
const PieChart = lazy(() => import('recharts').then(mod => ({ default: mod.PieChart })));
const Pie = lazy(() => import('recharts').then(mod => ({ default: mod.Pie })));
const Cell = lazy(() => import('recharts').then(mod => ({ default: mod.Cell })));
const BarChart = lazy(() => import('recharts').then(mod => ({ default: mod.BarChart })));
const Bar = lazy(() => import('recharts').then(mod => ({ default: mod.Bar })));

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const docId = searchParams.get('docId');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [realtimeMessage, setRealtimeMessage] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const url = docId
        ? `http://localhost:8000/api/dashboard?doc_id=${docId}`
        : 'http://localhost:8000/api/dashboard';
      const res = await fetch(url);
      const result = await res.json();
      setData(result);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [docId]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/history');
      const result = await res.json();
      if (result.success) setHistory(result.documents);
    } catch (err) {
      console.error('History fetch error:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    fetchHistory();

    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'analysis_complete') {
        setRealtimeMessage('New analysis completed! Refreshing...');
        fetchData();
        fetchHistory();
        setTimeout(() => setRealtimeMessage(null), 3000);
      }
    };
    setSocket(ws);
    return () => ws.close();
  }, [fetchData, fetchHistory]);

  const riskTrend = useMemo(() => {
    return history.map(doc => ({
      name: new Date(doc.upload_date).toLocaleDateString(),
      risk: doc.risk_score,
      compliance: doc.compliance_score
    })).slice(-10);
  }, [history]);

  const riskDistribution = useMemo(() => {
    const dist = { Low: 0, Medium: 0, High: 0 };
    history.forEach(doc => {
      if (doc.risk_score < 30) dist.Low++;
      else if (doc.risk_score < 70) dist.Medium++;
      else dist.High++;
    });
    return Object.entries(dist).map(([name, value]) => ({ name, value }));
  }, [history]);

  const COLORS = ['#22c55e', '#eab308', '#ef4444'];

  if (loading && !data) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} onRetry={fetchData} />;

  const report = data?.report || data?.current_document?.analysis_report;
  const currentDoc = data?.current_document;
  const analytics = data?.analytics;

  const getDeadline = (risk: number) => {
    if (risk > 70) return 'Immediate (within 7 days)';
    if (risk > 30) return 'Within 30 days';
    return 'Within 90 days';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          Compliance Dashboard
        </h1>

        {socket && (
          <div className="fixed bottom-4 right-4 glass-card px-4 py-2 text-cyan-300 text-sm z-50 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Live updates active
          </div>
        )}
        <AnimatePresence>
          {realtimeMessage && (
            <motion.div
              initial={{ opacity: 0, y: -50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              className="fixed top-4 right-4 glass-card-highlight text-white px-4 py-2 rounded-lg shadow-lg z-50"
            >
              {realtimeMessage}
            </motion.div>
          )}
        </AnimatePresence>

        {report && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-12"
          >
            <h2 className="text-2xl font-semibold text-white mb-4">Latest Analysis Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <MetricCard title="Risk Score" value={`${report.risk_score}/100`} color={getRiskColor(report.risk_score)} />
              <MetricCard title="Compliance Score" value={`${report.compliance_score}%`} color="blue" />
              <MetricCard title="Confidence" value={`${report.confidence_score}%`} color="purple" />
            </div>

            <GlassCard className="p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">Company Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-200">
                <p><span className="text-purple-300">Company:</span> {report.company_name || currentDoc?.company_name || 'N/A'}</p>
                <p><span className="text-purple-300">Document Type:</span> {report.document_type}</p>
                <p><span className="text-purple-300">Document:</span> {report.document_name}</p>
                <p><span className="text-purple-300">Next Review Deadline:</span> <span className="text-cyan-300">{getDeadline(report.risk_score)}</span></p>
              </div>
            </GlassCard>

            <GlassCard className="p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">AI Summary</h3>
              <p className="text-gray-200 leading-relaxed">{report.summary}</p>
            </GlassCard>

            {report.out_of_domain_advice && (
              <GlassCard className="p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-3">Out‑of‑Domain Advice</h3>
                <p className="text-gray-200 leading-relaxed">{report.out_of_domain_advice}</p>
              </GlassCard>
            )}

            {report.issues?.length > 0 && (
              <GlassCard className="p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-3">Issues & Risks</h3>
                <div className="space-y-4">
                  {report.issues.map((issue: any, idx: number) => (
                    <div key={idx} className="border-l-4 border-red-500 pl-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-lg font-medium text-white">{issue.title}</h4>
                        <span className={`px-2 py-1 rounded text-sm ${
                          issue.severity === 'High' ? 'bg-red-500/20 text-red-300' :
                          issue.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-300' :
                          'bg-green-500/20 text-green-300'
                        }`}>
                          {issue.severity}
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm mb-2">{issue.description}</p>
                      <p className="text-cyan-300 text-sm">💡 {issue.recommendation}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {(report.recommendations?.length > 0 || report.next_actions?.length > 0) && (
              <GlassCard className="p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-3">AI Recommendations</h3>
                <ul className="space-y-2">
                  {(report.recommendations || report.next_actions).map((rec: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-purple-400 mr-2">→</span>
                      <span className="text-gray-200">{rec}</span>
                    </li>
                  ))}
                </ul>
              </GlassCard>
            )}

            {report.missing_elements?.length > 0 && (
              <GlassCard className="p-6">
                <h3 className="text-xl font-semibold text-white mb-3">Missing Compliance Elements</h3>
                <ul className="space-y-2">
                  {report.missing_elements.map((elem: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-red-400 mr-2">⚠️</span>
                      <span className="text-gray-200">{elem}</span>
                    </li>
                  ))}
                </ul>
              </GlassCard>
            )}
          </motion.div>
        )}

        {analytics && (
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-white mb-4">Analytics Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <MetricCard title="Total Documents" value={analytics.total_documents} color="cyan" />
              <MetricCard title="Avg Risk Score" value={analytics.average_risk_score.toFixed(1)} color={getRiskColor(analytics.average_risk_score)} />
              <MetricCard title="Avg Compliance" value={`${analytics.average_compliance_score.toFixed(1)}%`} color="blue" />
              <MetricCard title="Latest Risk" value={analytics.latest_risk_score} color={getRiskColor(analytics.latest_risk_score)} />
            </div>

            {analytics.top_issue_categories && analytics.top_issue_categories.length > 0 && (
              <GlassCard className="p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">Top Issue Categories</h3>
                <Suspense fallback={<div className="h-64 flex items-center justify-center"><p className="text-gray-400">Loading chart...</p></div>}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analytics.top_issue_categories}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#4a4a6a" />
                      <XAxis dataKey="category" stroke="#ccc" />
                      <YAxis stroke="#ccc" />
                      <Tooltip contentStyle={{ backgroundColor: '#1e1e3a', border: 'none', borderRadius: '8px' }} />
                      <Bar dataKey="count" fill="#a855f7" />
                    </BarChart>
                  </ResponsiveContainer>
                </Suspense>
              </GlassCard>
            )}
          </div>
        )}

        {history.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            <GlassCard className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Risk & Compliance Trend</h3>
              <Suspense fallback={<div className="h-64 flex items-center justify-center"><p className="text-gray-400">Loading chart...</p></div>}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={riskTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#4a4a6a" />
                    <XAxis dataKey="name" stroke="#ccc" />
                    <YAxis stroke="#ccc" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e1e3a', border: 'none', borderRadius: '8px' }} />
                    <Legend />
                    <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} />
                    <Line type="monotone" dataKey="compliance" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Suspense>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Risk Distribution</h3>
              <Suspense fallback={<div className="h-64 flex items-center justify-center"><p className="text-gray-400">Loading chart...</p></div>}>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={riskDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                      {riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Suspense>
            </GlassCard>
          </div>
        )}

        <GlassCard className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Document History</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {history.map(doc => (
              <Link
                key={doc.document_id}
                href={`/dashboard?docId=${doc.document_id}`}
                className="block p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-all cursor-pointer"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-white font-medium">{doc.company_name}</p>
                    <p className="text-gray-400 text-sm">{doc.filename}</p>
                    <p className="text-gray-500 text-xs">{new Date(doc.upload_date).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${doc.risk_score > 70 ? 'text-red-400' : doc.risk_score > 30 ? 'text-yellow-400' : 'text-green-400'}`}>
                      Risk: {doc.risk_score}
                    </p>
                    <p className="text-gray-400 text-sm">Compliance: {doc.compliance_score}%</p>
                  </div>
                </div>
              </Link>
            ))}
            {history.length === 0 && <p className="text-gray-400 text-center py-8">No documents uploaded yet</p>}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}

// Helper components
function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] flex items-center justify-center">
      <div className="text-center glass-card p-8">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mb-4"></div>
        <p className="text-white text-lg">Loading dashboard...</p>
      </div>
    </div>
  );
}

function ErrorDisplay({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] p-8">
      <GlassCard className="p-8 text-center">
        <div className="text-red-400 text-xl mb-4">⚠️ Error</div>
        <p className="text-gray-300">{error}</p>
        <button onClick={onRetry} className="mt-4 px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 transition">
          Retry
        </button>
      </GlassCard>
    </div>
  );
}

function MetricCard({ title, value, color }: { title: string; value: string | number; color: string }) {
  const colorMap: Record<string, string> = {
    green: 'from-green-500 to-green-600',
    yellow: 'from-yellow-500 to-yellow-600',
    red: 'from-red-500 to-red-600',
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    cyan: 'from-cyan-500 to-cyan-600'
  };
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} rounded-xl p-6 shadow-lg hover:shadow-2xl transition-shadow`}>
      <h3 className="text-white/90 text-sm font-medium mb-2">{title}</h3>
      <p className="text-white text-3xl font-bold">{value}</p>
    </div>
  );
}

function GlassCard({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-xl ${className || ''}`}>
      {children}
    </div>
  );
}

function getRiskColor(score: number): string {
  if (score > 70) return 'red';
  if (score > 30) return 'yellow';
  return 'green';
}
