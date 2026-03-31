'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FileText, TrendingUp, Calendar, Activity } from "lucide-react";
import { getHistory } from "@/lib/api";

export default function HistoryPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // =========================
  // REAL-TIME FETCH (OPTIMIZED)
  // =========================
  useEffect(() => {
    load();

    const interval = setInterval(load, 8000); // less aggressive = faster UX
    return () => clearInterval(interval);
  }, []);

  const load = async () => {
    try {
      const res = await getHistory();

      if (res?.documents) {
        setDocuments(res.documents);
      }
    } catch (e) {
      console.error("History fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // NAVIGATION (FULL DATA PASS)
  // =========================
  const openDocument = (doc: any) => {
    localStorage.setItem(
      "latestAnalysis",
      JSON.stringify({
        document_id: doc.document_id,
        report: {
          risk_score: doc.risk_score,
          compliance_score: doc.compliance_score,
          confidence_score: doc.confidence_score,
          summary: doc.summary,
          issues: doc.issues || []
        }
      })
    );

    router.push(`/dashboard?docId=${doc.document_id}`);
  };

  // =========================
  // STATS (SAFE)
  // =========================
  const total = documents.length;

  const avgRisk =
    total > 0
      ? Math.round(
          documents.reduce((a, d) => a + (d.risk_score || 0), 0) / total
        )
      : 0;

  const highRisk = documents.filter((d) => (d.risk_score || 0) > 70).length;

  // =========================
  // UI
  // =========================
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-purple-900 to-black text-white p-6 space-y-8">

      {/* HEADER */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Document Intelligence History
        </h1>
        <p className="text-gray-400">
          Real-time tracking of all analyzed documents
        </p>
      </motion.div>

      {/* ========================= */}
      {/* STATS */}
      {/* ========================= */}
      <div className="grid md:grid-cols-4 gap-6">

        <Stat icon={FileText} label="Total Docs" value={total} />
        <Stat icon={TrendingUp} label="Avg Risk" value={avgRisk + "%"} />
        <Stat icon={Activity} label="High Risk" value={highRisk} />
        <Stat icon={Calendar} label="System" value="Live" />

      </div>

      {/* ========================= */}
      {/* LIST */}
      {/* ========================= */}
      <div className="space-y-3">

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-white/5 animate-pulse rounded-xl" />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center text-gray-400 mt-20">
            No documents yet 🚀
          </div>
        ) : (
          documents.map((doc, i) => (
            <motion.div
              key={doc.document_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              onClick={() => openDocument(doc)}
              className="cursor-pointer p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 flex justify-between items-center transition-all"
            >

              {/* LEFT */}
              <div>
                <p className="font-medium">{doc.filename || "Untitled Document"}</p>
                <p className="text-xs text-gray-400">
                  {doc.upload_date
                    ? new Date(doc.upload_date).toLocaleString()
                    : "Unknown time"}
                </p>
              </div>

              {/* RIGHT */}
              <div className="flex items-center gap-4">

                <Badge score={doc.risk_score || 0} />

                <span className="text-gray-400 text-sm">
                  {doc.compliance_score ?? "--"}%
                </span>

              </div>

            </motion.div>
          ))
        )}
      </div>

    </div>
  );
}


// =========================
// COMPONENTS
// =========================

function Stat({ icon: Icon, label, value }: any) {
  return (
    <div className="p-5 bg-white/5 border border-white/10 rounded-xl flex items-center gap-4 backdrop-blur-xl">
      <Icon className="text-purple-400" />
      <div>
        <p className="text-sm text-gray-400">{label}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </div>
  );
}

function Badge({ score }: any) {
  const color =
    score > 70 ? "text-red-400" :
    score > 40 ? "text-yellow-400" :
    "text-green-400";

  return (
    <div className={`${color} font-semibold`}>
      {score ?? "--"}%
    </div>
  );
}