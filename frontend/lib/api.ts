const API_BASE = 'http://localhost:8000';

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
  return res.json();
}

export async function getDashboardData(docId?: string) {
  const url = docId ? `${API_BASE}/api/dashboard?doc_id=${docId}` : `${API_BASE}/api/dashboard`;
  const res = await fetch(url);
  return res.json();
}

export async function getDocumentHistory() {
  const res = await fetch(`${API_BASE}/api/history`);
  return res.json();
}

export async function getDocumentDetail(documentId: string) {
  const res = await fetch(`${API_BASE}/api/history/${documentId}`);
  return res.json();
}

// Alias for history (for existing pages)
export const getHistory = getDocumentHistory;

export async function sendChatMessage(documentId: string, message: string, history: any[] = []) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, message, history })
  });
  return res.json();
}

export async function getInsights() {
  const res = await fetch(`${API_BASE}/api/insights`);
  return res.json();
}
