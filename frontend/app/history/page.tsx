'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDocumentHistory, HistoryDocument } from '@/lib/api';
import { motion } from 'framer-motion';

export default function HistoryPage() {
  const [documents, setDocuments] = useState<HistoryDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDocumentHistory().then(res => {
      if (res.success) setDocuments(res.documents);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          Document History
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map(doc => (
            <Link key={doc.document_id} href={`/dashboard?docId=${doc.document_id}`}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="glass-card p-6 cursor-pointer"
              >
                <h3 className="text-xl font-semibold text-white mb-2">{doc.company_name}</h3>
                <p className="text-gray-400 text-sm">{doc.filename}</p>
                <p className="text-gray-500 text-xs">{new Date(doc.upload_date).toLocaleString()}</p>
                <div className="mt-4 flex justify-between">
                  <span className="text-purple-300">Risk: {doc.risk_score}</span>
                  <span className="text-blue-300">Compliance: {doc.compliance_score}%</span>
                </div>
              </motion.div>
            </Link>
          ))}
          {documents.length === 0 && <p className="text-gray-400 text-center col-span-full">No documents yet</p>}
        </div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] flex items-center justify-center">
      <div className="text-center glass-card p-8">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mb-4"></div>
        <p className="text-white text-lg">Loading history...</p>
      </div>
    </div>
  );
}
