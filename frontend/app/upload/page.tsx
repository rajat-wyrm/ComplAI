'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadDocument } from '@/lib/api';

export default function UploadPage() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // =========================
  // FILE SELECT
  // =========================
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  // =========================
  // UPLOAD + ANALYZE (UPGRADED)
  // =========================
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setProgress(0);

      // 🔥 FAKE PROGRESS (ULTRA SMOOTH UX)
      let p = 0;
      const interval = setInterval(() => {
        p += 8;
        if (p <= 90) setProgress(p);
      }, 200);

      const result = await uploadDocument(file);

      clearInterval(interval);
      setProgress(100);

      // 🔥 STRICT RESPONSE VALIDATION
      if (!result?.success || !result?.report) {
        throw new Error('Invalid response from server');
      }

      // 🔥 STORE FULL DATA (IMPORTANT FOR DASHBOARD)
      localStorage.setItem(
        'latestAnalysis',
        JSON.stringify({
          document_id: result.document_id,
          report: result.report,
        })
      );

      // 🔥 INSTANT REDIRECT
      router.push(`/dashboard?docId=${result.document_id}`);

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // =========================
  // UI
  // =========================
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-[#0f172a] to-black text-white">

      <div className="w-full max-w-lg p-8 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 shadow-xl">

        <h1 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Upload Compliance Document
        </h1>

        {/* FILE INPUT */}
        <div className="mb-6 border-2 border-dashed border-purple-500/40 rounded-xl p-6 text-center hover:border-purple-500 transition">

          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
            className="hidden"
            id="file-upload"
          />

          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="text-5xl mb-3">📄</div>

            <p className="text-lg font-medium">
              {file ? file.name : 'Select Document'}
            </p>

            <p className="text-sm text-gray-400 mt-1">
              PDF, DOCX, TXT supported
            </p>
          </label>
        </div>

        {/* PROGRESS BAR */}
        {uploading && (
          <div className="mb-4">
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-1 text-center">
              Processing with AI...
            </p>
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div className="mb-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 p-3 rounded-lg">
            {error}
          </div>
        )}

        {/* BUTTON */}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 transition font-semibold"
        >
          {uploading ? 'Analyzing with AI...' : 'Upload & Analyze'}
        </button>

        {/* LOADER */}
        {uploading && (
          <div className="mt-4 text-center text-gray-400">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-white mb-2"></div>
          </div>
        )}

      </div>
    </div>
  );
}