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
        return <FileText className="h-3 w-3 sm:h-4 sm:w-4 text-blue-400" />;
      case "analysis":
        return <Clock className="h-3 w-3 sm:h-4 sm:w-4 text-purple-400" />;
      case "risk":
        return <AlertTriangle className="h-3 w-3 sm:h-4 sm:w-4 text-yellow-400" />;
      case "complete":
        return <CheckCircle2 className="h-3 w-3 sm:h-4 sm:w-4 text-green-400" />;
      default:
        return <Clock className="h-3 w-3 sm:h-4 sm:w-4 text-white/40" />;
    }
  };

  return (
    <GlassCard className="p-4 sm:p-6 h-full" premium>
      <h3 className="text-xs sm:text-sm font-medium text-white/60 mb-3 sm:mb-4">Recent Activity</h3>
      <div className="space-y-2 sm:space-y-3 max-h-[300px] sm:max-h-[400px] overflow-y-auto pr-1">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-start gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
          >
            <div className="p-1 sm:p-1.5 rounded-lg bg-white/10">
              {getIcon(activity.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs sm:text-sm font-medium truncate">{activity.title}</p>
              <p className="text-[10px] sm:text-xs text-white/40 mt-0.5 truncate">{activity.description}</p>
            </div>
            <p className="text-[9px] sm:text-xs text-white/30 whitespace-nowrap ml-1">{activity.time}</p>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  );
}
