'use client';

import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

export default function HomePage() {
  const router = useRouter();

  const features = [
    { icon: '📄', title: 'Upload Documents', description: 'Upload compliance documents for instant AI analysis', link: '/upload', color: 'from-purple-500 to-pink-500' },
    { icon: '📊', title: 'View Dashboard', description: 'See compliance scores, risk metrics, and insights', link: '/dashboard', color: 'from-blue-500 to-cyan-500' },
    { icon: '💬', title: 'Chat with AI', description: 'Ask questions about your compliance documents', link: '/chat', color: 'from-green-500 to-teal-500' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a2a] via-[#1a1a3a] to-[#2a1a4a]">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
            AI Compliance & Risk Copilot
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Intelligent compliance analysis powered by Generative AI
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6 text-center hover:bg-white/15 transition-all cursor-pointer group"
              onClick={() => router.push(feature.link)}
            >
              <div className={`text-5xl mb-4 bg-gradient-to-r ${feature.color} bg-clip-text text-transparent`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-300 mb-4">{feature.description}</p>
              <div className="inline-flex items-center text-purple-400 group-hover:translate-x-1 transition">
                Get started <span className="ml-1">→</span>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex gap-4 flex-wrap justify-center">
            <div className="bg-white/10 px-4 py-2 rounded-full">
              <span className="text-green-300">✓ AI-Powered Analysis</span>
            </div>
            <div className="bg-white/10 px-4 py-2 rounded-full">
              <span className="text-blue-300">✓ Real-time Insights</span>
            </div>
            <div className="bg-white/10 px-4 py-2 rounded-full">
              <span className="text-purple-300">✓ Risk Detection</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
