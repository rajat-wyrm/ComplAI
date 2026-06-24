'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { sendChatMessage, getChatHistory, ChatMessage } from '@/lib/api';

interface HistoryItem {
  question: string;
  answer: string;
}

export default function ChatPage() {
  const searchParams = useSearchParams();
  const docId = searchParams.get('docId');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (docId) {
      getChatHistory(docId).then(res => {
        if (res.success) {
          const history = (res.history as HistoryItem[]).map((item) => [
            { role: 'user', content: item.question },
            { role: 'assistant', content: item.answer }
          ]).flat();
          setMessages(history);
        }
      });
    }
  }, [docId]);

  const sendMessage = async () => {
    if (!message.trim() || !docId) return;
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setMessage('');
    setLoading(true);
    try {
      const res = await sendChatMessage(docId, message, messages);
      if (res.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, an error occurred.' }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, an error occurred.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a] p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
          Chat with Document
        </h1>
        {!docId && (
          <div className="glass-card p-6 text-center">
            <p className="text-gray-300">Please select a document from the dashboard to start chatting.</p>
            <a href="/dashboard" className="mt-4 inline-block px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700">Go to Dashboard</a>
          </div>
        )}
        {docId && (
          <div className="glass-card p-6">
            <div className="h-96 overflow-y-auto mb-4 space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-purple-600 text-white' : 'bg-white/10 text-gray-200'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 p-3 rounded-lg text-gray-400">Typing...</div>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask a question about this document..."
                className="flex-1 px-4 py-2 bg-white/10 rounded-lg border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !message.trim()}
                className="px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
