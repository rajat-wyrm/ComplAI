// =========================
// BASE CONFIG
// =========================
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEFAULT_TIMEOUT = 15000;
const RETRIES = 2;


// =========================
// GENERIC FETCH (ULTRA SAFE)
// =========================
async function safeFetch(
  url: string,
  options: RequestInit = {},
  timeout = DEFAULT_TIMEOUT,
  retries = RETRIES
): Promise<any> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.headers || {}),
      },
    });

    clearTimeout(id);

    let data: any = {};
    try {
      data = await res.json();
    } catch {
      data = {};
    }

    if (!res.ok) {
      throw new Error(data?.error || data?.detail || "Request failed");
    }

    return data;

  } catch (err: any) {
    clearTimeout(id);

    if (retries > 0) {
      console.warn("Retrying request...", url);
      return safeFetch(url, options, timeout, retries - 1);
    }

    console.error("🔥 API ERROR:", err.message);

    // 🔥 NEVER BREAK FRONTEND
    return { success: false, fallback: true };
  }
}


// =========================
// UPLOAD + ANALYZE
// =========================
export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await safeFetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  // 🔥 ALWAYS RETURN SAFE STRUCTURE
  return {
    success: res?.success ?? true,
    document_id: res?.document_id ?? crypto.randomUUID(),
    report: res?.report ?? {
      risk_score: 50,
      compliance_score: 50,
      confidence_score: 60,
      summary: "Fallback: Document processed with limited data.",
      issues: [],
      document_type: "Unknown",
      key_points: [],
      sensitive_data: [],
      missing_items: [],
    },
  };
}


// =========================
// INSIGHTS
// =========================
export async function getInsights() {
  const res = await safeFetch(`${API_BASE_URL}/insights`);

  return {
    success: res?.success ?? true,
    data: res?.data ?? {
      total_documents: 0,
      avg_risk_score: 0,
      avg_compliance_score: 0,
      avg_confidence_score: 0,
      severity_distribution: { low: 0, medium: 0, high: 0 },
      document_types: {},
      risk_trend: [],
      recent_activity: [],
      compliance_categories: [],
    },
  };
}


// =========================
// HISTORY
// =========================
export async function getHistory(limit = 50) {
  const res = await safeFetch(`${API_BASE_URL}/history?limit=${limit}`);

  return {
    success: res?.success ?? true,
    documents: res?.documents ?? [],
    total: res?.total ?? 0,
    companies: res?.companies ?? [],
  };
}


// =========================
// SINGLE DOCUMENT
// =========================
export async function getDocumentAnalysis(documentId: string) {
  const res = await safeFetch(
    `${API_BASE_URL}/history/${documentId}`
  );

  return {
    success: res?.success ?? true,
    document: res?.document ?? null,
  };
}


// =========================
// CHAT
// =========================
export async function sendChatMessage(
  documentId: string,
  message: string,
  history: any[] = []
) {
  const res = await safeFetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_id: documentId,
      message,
      history,
    }),
  });

  return {
    success: res?.success ?? true,
    response:
      res?.response ??
      "AI fallback: Unable to generate full response. Please try again.",
    timestamp: res?.timestamp ?? new Date().toISOString(),
  };
}


// =========================
// CHAT HISTORY
// =========================
export async function getChatHistory(documentId: string) {
  const res = await safeFetch(
    `${API_BASE_URL}/chat/history/${documentId}`
  );

  return {
    success: res?.success ?? true,
    history: res?.history ?? [],
  };
}


// =========================
// HEALTH CHECK
// =========================
export async function getSystemHealth() {
  return safeFetch(`${API_BASE_URL}/health`);
}