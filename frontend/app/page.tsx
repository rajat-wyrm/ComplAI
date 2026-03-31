'use client';

import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            AI Compliance & Risk Copilot
          </h1>
          <p className="text-xl text-gray-300">
            Intelligent compliance analysis powered by Generative AI
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 text-center hover:bg-white/20 transition-all">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-xl font-semibold text-white mb-2">Upload Documents</h3>
            <p className="text-gray-300">Upload compliance documents for instant AI analysis</p>
            <button
              onClick={() => router.push('/upload')}
              className="mt-4 px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
            >
              Get Started
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 text-center hover:bg-white/20 transition-all">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-white mb-2">View Dashboard</h3>
            <p className="text-gray-300">See compliance scores, risk metrics, and insights</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="mt-4 px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
            >
              View Dashboard
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 text-center hover:bg-white/20 transition-all">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-white mb-2">Chat with AI</h3>
            <p className="text-gray-300">Ask questions about your compliance documents</p>
            <button
              onClick={() => router.push('/chat')}
              className="mt-4 px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
            >
              Start Chat
            </button>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex gap-4">
            <div className="bg-green-500/20 px-4 py-2 rounded-full">
              <span className="text-green-300">✓ AI-Powered Analysis</span>
            </div>
            <div className="bg-blue-500/20 px-4 py-2 rounded-full">
              <span className="text-blue-300">✓ Real-time Insights</span>
            </div>
            <div className="bg-purple-500/20 px-4 py-2 rounded-full">
              <span className="text-purple-300">✓ Risk Detection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
