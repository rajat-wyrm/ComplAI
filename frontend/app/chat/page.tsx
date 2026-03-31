'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';
import { getHistory, sendChatMessage } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // =========================
  // LOAD DOCUMENTS
  // =========================
  useEffect(() => {
    const loadDocs = async () => {
      try {
        const res = await getHistory();
        setDocuments(res.documents || []);
      } catch (e) {
        console.error(e);
      }
    };
    loadDocs();
  }, []);

  // =========================
  // AUTO SCROLL
  // =========================
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages]);

  // =========================
  // SEND MESSAGE
  // =========================
  const handleSend = async () => {
    if (!input.trim() || !selectedDoc) return;

    const userMsg = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(
        selectedDoc,
        input,
        messages
      );

      const aiMsg = { role: 'assistant', content: res.response };
      setMessages((prev) => [...prev, aiMsg]);

    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // UI
  // =========================
  return (
    <div className="min-h-screen bg-black text-white flex flex-col">

      {/* HEADER */}
      <div className="p-6 border-b border-white/10 backdrop-blur-xl">
        <h1 className="text-2xl font-bold">AI Compliance Copilot</h1>
      </div>

      <div className="flex flex-1">

        {/* LEFT PANEL */}
        <div className="w-80 border-r border-white/10 p-4 space-y-4 bg-white/5 backdrop-blur-xl">

          <h2 className="text-lg font-semibold">Documents</h2>

          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                onClick={() => setSelectedDoc(doc.document_id)}
                className={`p-3 rounded-xl cursor-pointer transition ${
                  selectedDoc === doc.document_id
                    ? 'bg-purple-600'
                    : 'bg-white/5 hover:bg-white/10'
                }`}
              >
                <p className="text-sm">{doc.filename}</p>
                <p className="text-xs text-gray-400">
                  Risk: {doc.risk_score}
                </p>
              </div>
            ))}
          </div>

        </div>

        {/* CHAT AREA */}
        <div className="flex-1 flex flex-col">

          {/* MESSAGES */}
          <div
            ref={scrollRef}
            className="flex-1 p-6 overflow-y-auto space-y-4"
          >
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                Select a document and start asking questions 🚀
              </div>
            )}

            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xl p-4 rounded-2xl backdrop-blur-xl ${
                    msg.role === 'user'
                      ? 'bg-purple-600'
                      : 'bg-white/10'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {msg.content}
                  </p>
                </div>
              </motion.div>
            ))}

            {loading && (
              <div className="flex">
                <div className="p-3 bg-white/10 rounded-xl">
                  <Loader2 className="animate-spin w-4 h-4" />
                </div>
              </div>
            )}
          </div>

          {/* INPUT */}
          <div className="p-4 border-t border-white/10 backdrop-blur-xl flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask compliance questions..."
              className="flex-1 px-4 py-2 rounded-xl bg-white/10 outline-none"
            />

            <button
              onClick={handleSend}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 rounded-xl hover:bg-purple-700 transition"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Send />}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}