'use client';

import { useEffect, useState } from 'react';
import { getInsights } from '@/lib/api';
import { motion } from 'framer-motion';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const res = await getInsights();
      setData(res.data);
    } catch {}
  };

  return (
    <div className="space-y-6">

      <h1 className="text-3xl font-bold">AI Intelligence Dashboard</h1>

      <div className="grid md:grid-cols-4 gap-6">
        {[
          { label: "Documents", value: data?.total_documents },
          { label: "Risk", value: data?.avg_risk_score },
          { label: "Compliance", value: data?.avg_compliance_score },
          { label: "Confidence", value: data?.avg_confidence_score },
        ].map((item, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.05 }}
            className="p-6 rounded-2xl bg-white/5 border border-white/10"
          >
            <p className="text-gray-400">{item.label}</p>
            <p className="text-3xl font-bold">{item.value || "--"}</p>
          </motion.div>
        ))}
      </div>

    </div>
  );
}
