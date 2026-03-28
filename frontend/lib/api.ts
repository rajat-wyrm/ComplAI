import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const analyzeDocument = async (documentId: string) => {
  const response = await api.post("/analyze", { document_id: documentId });
  return response.data;
};

export const getInsights = async (documentId: string) => {
  const response = await api.get(`/insights/${documentId}`);
  return response.data;
};

export const chatWithDocument = async (documentId: string, message: string, sessionId?: string) => {
  const response = await api.post("/chat", { document_id: documentId, message, session_id: sessionId });
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get("/history");
  return response.data;
};

export const getDashboard = async () => {
  const response = await api.get("/insights/dashboard/summary");
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};
