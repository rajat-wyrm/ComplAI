"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { FileText, Eye, TrendingUp, Calendar, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getHistory } from "@/lib/api";
import type { Document } from "@/types";

export default function HistoryPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory();
        setDocuments(data.documents || []);
      } catch (error) {
        console.error("Failed to fetch history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const getRiskColor = (score: number) => {
    if (score >= 70) return "text-red-500 bg-red-500/10";
    if (score >= 40) return "text-yellow-500 bg-yellow-500/10";
    return "text-green-500 bg-green-500/10";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "analyzed":
        return "bg-green-500/20 text-green-500";
      case "processing":
        return "bg-yellow-500/20 text-yellow-500";
      case "failed":
        return "bg-red-500/20 text-red-500";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold gradient-text">Document History</h1>
        <p className="text-muted-foreground mt-2">
          View and manage all your analyzed compliance documents
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="glass-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-primary/10">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{documents.length}</p>
                  <p className="text-sm text-muted-foreground">Total Documents</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-green-500/10">
                  <TrendingUp className="h-6 w-6 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {documents.filter(d => d.status === "analyzed").length}
                  </p>
                  <p className="text-sm text-muted-foreground">Analyzed</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-yellow-500/10">
                  <Calendar className="h-6 w-6 text-yellow-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {documents.length > 0 ? Math.ceil(documents.reduce((acc, d) => {
                      const days = (new Date().getTime() - new Date(d.upload_date).getTime()) / (1000 * 60 * 60 * 24);
                      return acc + days;
                    }, 0) / documents.length) : 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Avg. Age (days)</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>All Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-20 bg-white/5 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                <p className="text-muted-foreground">No documents uploaded yet</p>
                <Button className="mt-4" asChild>
                  <Link href="/upload">Upload your first document</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc, index) => (
                  <motion.div
                    key={doc.document_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <FileText className="h-8 w-8 text-primary" />
                      <div className="flex-1">
                        <p className="font-medium">{doc.filename}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-muted-foreground">
                            {new Date(doc.upload_date).toLocaleDateString()}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                          </span>
                          <Badge className={getStatusColor(doc.status)}>
                            {doc.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {doc.risk_score && (
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(doc.risk_score)}`}>
                          Risk: {doc.risk_score}%
                        </div>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        asChild
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Link href={`/analysis/${doc.document_id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
