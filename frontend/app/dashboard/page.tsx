'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { motion } from 'framer-motion';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const docId = searchParams.get('docId');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // Fetch dashboard data
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

  // Fetch history
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

    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'analysis_complete') {
        // Refresh data to show new report
        fetchData();
        fetchHistory();
      }
    };
    setSocket(ws);
    return () => ws.close();
  }, [fetchData, fetchHistory]);

  // Memoized chart data
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
  const analytics = data?.analytics;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Compliance Dashboard</h1>

        {/* Real-time Notification */}
        {socket && (
          <div className="fixed bottom-4 right-4 bg-green-500/20 backdrop-blur-lg rounded-full px-4 py-2 text-green-300 text-sm">
            🟢 Live updates active
          </div>
        )}

        {/* Latest Report Section */}
        {report && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <h2 className="text-2xl font-semibold text-white mb-4">Latest Analysis Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <MetricCard title="Risk Score" value={`${report.risk_score}/100`} color={getRiskColor(report.risk_score)} />
              <MetricCard title="Compliance Score" value={`${report.compliance_score}%`} color="blue" />
              <MetricCard title="Confidence" value={`${report.confidence_score}%`} color="purple" />
            </div>

            <GlassCard className="p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">Company Information</h3>
              <p className="text-gray-300">Company: {report.company_name}</p>
              <p className="text-gray-300">Document Type: {report.document_type}</p>
              <p className="text-gray-300">Document: {report.document_name}</p>
            </GlassCard>

            <GlassCard className="p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">Summary</h3>
              <p className="text-gray-300">{report.summary}</p>
            </GlassCard>

            {report.issues?.length > 0 && (
              <GlassCard className="p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-3">Issues & Risks</h3>
                <div className="space-y-4">
                  {report.issues.map((issue, idx) => (
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
                      <p className="text-purple-300 text-sm">💡 {issue.recommendation}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {report.next_actions?.length > 0 && (
              <GlassCard className="p-6">
                <h3 className="text-xl font-semibold text-white mb-3">Next Actions</h3>
                <ul className="space-y-2">
                  {report.next_actions.map((action, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-purple-400 mr-2">→</span>
                      <span className="text-gray-300">{action}</span>
                    </li>
                  ))}
                </ul>
              </GlassCard>
            )}
          </motion.div>
        )}

        {/* Charts Section */}
        {history.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <GlassCard className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Risk & Compliance Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={riskTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
                  <Legend />
                  <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} />
                  <Line type="monotone" dataKey="compliance" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Risk Distribution</h3>
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
            </GlassCard>
          </div>
        )}

        {/* Document History List */}
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
        <p className="text-white text-lg">Loading dashboard...</p>
      </div>
    </div>
  );
}

function ErrorDisplay({ error, onRetry }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <GlassCard className="p-8 text-center">
        <div className="text-red-400 text-xl mb-4">⚠️ Error</div>
        <p className="text-gray-300">{error}</p>
        <button onClick={onRetry} className="mt-4 px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700">
          Retry
        </button>
      </GlassCard>
    </div>
  );
}

function MetricCard({ title, value, color }) {
  const colorMap = {
    green: 'from-green-500 to-green-600',
    yellow: 'from-yellow-500 to-yellow-600',
    red: 'from-red-500 to-red-600',
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600'
  };
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} rounded-xl p-6 shadow-lg`}>
      <h3 className="text-white/90 text-sm font-medium mb-2">{title}</h3>
      <p className="text-white text-3xl font-bold">{value}</p>
    </div>
  );
}

function GlassCard({ children, className }) {
  return (
    <div className={`bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 ${className}`}>
      {children}
    </div>
  );
}

function getRiskColor(score) {
  if (score > 70) return 'red';
  if (score > 30) return 'yellow';
  return 'green';
}
