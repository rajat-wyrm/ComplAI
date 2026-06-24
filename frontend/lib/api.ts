const API_BASE = 'http://localhost:8000';

export interface ChatMessage {
  role: string;
  content: string;
}

export interface HistoryDocument {
  document_id: string;
  company_name: string;
  filename: string;
  upload_date: string;
  risk_score: number;
  compliance_score: number;
}

export interface ReportIssue {
  title: string;
  severity: 'High' | 'Medium' | 'Low';
  description: string;
  recommendation: string;
}

export interface DashboardReport {
  risk_score: number;
  compliance_score: number;
  confidence_score: number;
  company_name?: string;
  document_type?: string;
  document_name?: string;
  summary?: string;
  out_of_domain_advice?: string;
  issues?: ReportIssue[];
  recommendations?: string[];
  next_actions?: string[];
  missing_elements?: string[];
}

export interface DashboardAnalytics {
  total_documents: number;
  average_risk_score: number;
  average_compliance_score: number;
  latest_risk_score: number;
  top_issue_categories?: Array<{ category: string; count: number }>;
}

export interface DashboardResponse {
  report?: DashboardReport;
  current_document?: {
    analysis_report?: DashboardReport;
    company_name?: string;
  };
  analytics?: DashboardAnalytics;
}

export interface InsightResponse {
  analysis_id?: string;
  status?: string;
  risk_score?: number;
  confidence_score?: number;
  explanation?: string;
  filename?: string;
  risks?: Array<{
    category: string;
    description?: string;
    severity: 'high' | 'medium' | 'low';
    impact?: string;
  }>;
  recommended_actions?: string[];
  compliance_gaps?: string[];
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
  return res.json();
}

export async function getDashboardData(docId?: string) {
  const url = docId ? `${API_BASE}/api/dashboard?doc_id=${docId}` : `${API_BASE}/api/dashboard`;
  const res = await fetch(url, { cache: 'no-store' });
  return res.json();
}

export async function getDocumentHistory() {
  const res = await fetch(`${API_BASE}/api/history`, { cache: 'no-store' });
  return res.json();
}

// Alias for compatibility
export const getHistory = getDocumentHistory;

export async function getDocumentDetail(documentId: string) {
  const res = await fetch(`${API_BASE}/api/history/${documentId}`);
  return res.json();
}

export async function sendChatMessage(documentId: string, message: string, history: ChatMessage[] = []) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, message, history })
  });
  return res.json();
}

export async function getChatHistory(documentId: string) {
  const res = await fetch(`${API_BASE}/api/chat/history/${documentId}`);
  return res.json();
}

export async function getInsights(documentId?: string) {
  const url = documentId
    ? `${API_BASE}/api/insights/${documentId}`
    : `${API_BASE}/api/insights`;
  const res = await fetch(url);
  return res.json();
}

export async function analyzeDocument(documentId: string) {
  const res = await fetch(`${API_BASE}/api/analyze/${documentId}`, {
    method: 'POST',
  });
  return res.json();
}
