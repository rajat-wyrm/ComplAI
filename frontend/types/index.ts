export interface Document {
  document_id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  status: string;
  risk_score?: number;
  confidence_score?: number;
}

export interface Analysis {
  analysis_id: string;
  document_id: string;
  risk_score: number;
  confidence_score: number;
  risks: Risk[];
  explanation: string;
  recommended_actions: string[];
  compliance_gaps: string[];
  created_at: string;
  status: string;
}

export interface Risk {
  category: string;
  description: string;
  severity: "high" | "medium" | "low";
  impact: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface DashboardStats {
  total_documents: number;
  analyzed_documents: number;
  average_risk_score: number;
  period_days: number;
}
