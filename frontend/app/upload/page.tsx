'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { uploadDocument } from '@/lib/api';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await uploadDocument(file);
      if (result.success) {
        setSuccess(`Document uploaded successfully! Risk Score: ${result.report.risk_score}`);
        setTimeout(() => {
          router.push(`/dashboard?docId=${result.document_id}`);
        }, 1500);
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          Upload Compliance Document
        </h1>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8"
        >
          <div className="space-y-6">
            <div className="border-2 border-dashed border-purple-500/50 rounded-lg p-8 text-center hover:border-purple-500 transition">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.docx,.txt"
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex flex-col items-center"
              >
                <div className="text-6xl mb-4">📄</div>
                <div className="text-white text-lg mb-2">
                  {file ? file.name : 'Click to select or drag and drop'}
                </div>
                <div className="text-gray-400 text-sm">
                  Supported formats: PDF, DOCX, TXT
                </div>
              </label>
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-200">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 text-green-200">
                {success}
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-all"
            >
              {uploading ? 'Analyzing Document...' : 'Upload & Analyze'}
            </button>

            {uploading && (
              <div className="text-center text-gray-400">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mb-2"></div>
                <p>Processing document with AI...</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
