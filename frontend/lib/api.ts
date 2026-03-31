const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Upload failed');
  }

  return response.json();
}

export async function getDashboardData(docId?: string) {
  const url = docId 
    ? `${API_BASE_URL}/api/dashboard?doc_id=${docId}`
    : `${API_BASE_URL}/api/dashboard`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard data');
  }
  
  return response.json();
}

export async function getDocumentAnalysis(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${documentId}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch document analysis');
  }
  
  return response.json();
}

export async function getInsights() {
  const response = await fetch(`${API_BASE_URL}/api/insights`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch insights');
  }
  
  return response.json();
}

export async function sendChatMessage(documentId: string, message: string, history: any[] = []) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      document_id: documentId,
      message,
      history,
    }),
  });

  if (!response.ok) {
    throw new Error('Chat request failed');
  }

  return response.json();
}

export async function getChatHistory(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat/history/${documentId}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch chat history');
  }
  
  return response.json();
}
