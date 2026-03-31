'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const docId = searchParams.get('docId');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [docId]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const url = docId 
        ? `http://localhost:8000/api/dashboard?doc_id=${docId}`
        : 'http://localhost:8000/api/dashboard';
      
      const response = await fetch(url);
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
          <p className="text-white text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
          <div className="text-red-400 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-300">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const report = data?.report || data?.current_document?.analysis_report;
  const analytics = data?.analytics;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Compliance Dashboard</h1>

        {report && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">Latest Analysis Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className={`bg-gradient-to-br ${report.risk_score > 70 ? 'from-red-500 to-red-600' : report.risk_score > 30 ? 'from-yellow-500 to-yellow-600' : 'from-green-500 to-green-600'} rounded-xl p-6 shadow-lg`}>
                <h3 className="text-white/90 text-sm font-medium mb-2">Risk Score</h3>
                <p className="text-white text-3xl font-bold">{report.risk_score}/100</p>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 shadow-lg">
                <h3 className="text-white/90 text-sm font-medium mb-2">Compliance Score</h3>
                <p className="text-white text-3xl font-bold">{report.compliance_score}%</p>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 shadow-lg">
                <h3 className="text-white/90 text-sm font-medium mb-2">Confidence</h3>
                <p className="text-white text-3xl font-bold">{report.confidence_score}%</p>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">Company Information</h3>
              <p className="text-gray-300">Company: {report.company_name}</p>
              <p className="text-gray-300">Document Type: {report.document_type}</p>
              <p className="text-gray-300">Document: {report.document_name}</p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6 mb-6">
              <h3 className="text-xl font-semibold text-white mb-3">Summary</h3>
              <p className="text-gray-300">{report.summary}</p>
            </div>

            {report.issues && report.issues.length > 0 && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6 mb-6">
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
                      <p className="text-purple-300 text-sm">💡 {issue.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {report.next_actions && report.next_actions.length > 0 && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6">
                <h3 className="text-xl font-semibold text-white mb-3">Next Actions</h3>
                <ul className="space-y-2">
                  {report.next_actions.map((action: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-purple-400 mr-2">→</span>
                      <span className="text-gray-300">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {analytics && analytics.total_documents > 0 && (
          <div>
            <h2 className="text-2xl font-semibold text-white mb-4">Overall Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl p-6 shadow-lg">
                <h3 className="text-white/90 text-sm font-medium mb-2">Total Documents</h3>
                <p className="text-white text-3xl font-bold">{analytics.total_documents}</p>
              </div>
              <div className={`bg-gradient-to-br ${analytics.average_risk_score > 70 ? 'from-red-500 to-red-600' : analytics.average_risk_score > 30 ? 'from-yellow-500 to-yellow-600' : 'from-green-500 to-green-600'} rounded-xl p-6 shadow-lg`}>
                <h3 className="text-white/90 text-sm font-medium mb-2">Avg Risk Score</h3>
                <p className="text-white text-3xl font-bold">{analytics.average_risk_score.toFixed(1)}</p>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 shadow-lg">
                <h3 className="text-white/90 text-sm font-medium mb-2">Avg Compliance</h3>
                <p className="text-white text-3xl font-bold">{analytics.average_compliance_score.toFixed(1)}%</p>
              </div>
              <div className={`bg-gradient-to-br ${analytics.latest_risk_score > 70 ? 'from-red-500 to-red-600' : analytics.latest_risk_score > 30 ? 'from-yellow-500 to-yellow-600' : 'from-green-500 to-green-600'} rounded-xl p-6 shadow-lg`}>
                <h3 className="text-white/90 text-sm font-medium mb-2">Latest Risk</h3>
                <p className="text-white text-3xl font-bold">{analytics.latest_risk_score}</p>
              </div>
            </div>
          </div>
        )}

        {!report && (!analytics || analytics.total_documents === 0) && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-8 text-center">
            <p className="text-gray-300 text-lg">No data available. Upload a document to get started.</p>
            <button
              onClick={() => window.location.href = '/upload'}
              className="mt-4 px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
            >
              Upload Document
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
