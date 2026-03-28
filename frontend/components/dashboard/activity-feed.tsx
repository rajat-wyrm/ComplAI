"use client";

import { motion } from "framer-motion";
import { Clock, AlertTriangle, CheckCircle2, FileText } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";

interface Activity {
  id: string;
  type: "upload" | "analysis" | "risk" | "complete";
  title: string;
  description: string;
  time: string;
}

interface ActivityFeedProps {
  activities: Activity[];
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case "upload":
        return <FileText className="h-4 w-4 text-blue-400" />;
      case "analysis":
        return <Clock className="h-4 w-4 text-purple-400" />;
      case "risk":
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case "complete":
        return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      default:
        return <Clock className="h-4 w-4 text-white/40" />;
    }
  };

  return (
    <GlassCard className="p-6 h-full">
      <h3 className="text-sm font-medium text-white/60 mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
          >
            <div className="p-2 rounded-lg bg-white/10">
              {getIcon(activity.type)}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">{activity.title}</p>
              <p className="text-xs text-white/40 mt-1">{activity.description}</p>
            </div>
            <p className="text-xs text-white/30">{activity.time}</p>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  );
}
