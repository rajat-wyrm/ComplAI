'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Upload,
  MessageSquare,
  History,
  Shield,
  Zap,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Analytics', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload', href: '/upload', icon: Upload },
  { name: 'AI Chat', href: '/chat', icon: MessageSquare },
  { name: 'History', href: '/history', icon: History },
];

export function Sidebar() {
  const pathname = usePathname();

  const [isMobile, setIsMobile] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  // =========================
  // RESPONSIVE
  // =========================
  useEffect(() => {
    const check = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) setIsMobileOpen(false);
    };
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // =========================
  // CONTENT
  // =========================
  const SidebarContent = (
    <>
      {/* HEADER */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-white/10">

        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 blur-lg opacity-50 rounded-xl" />
              <Shield className="relative h-8 w-8 text-white" />
            </div>

            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                Compliance
              </h1>
              <p className="text-xs text-white/40">
                Risk Copilot Enterprise
              </p>
            </div>
          </div>
        )}

        {!isMobile && (
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded-lg bg-white/10 hover:bg-white/20"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        )}
      </div>

      {/* NAV */}
      <nav className="flex-1 px-3 py-6 space-y-2">
        {navigation.map((item, i) => {
          const isActive = pathname === item.href;

          return (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link href={item.href} onClick={() => setIsMobileOpen(false)}>
                <div
                  className={cn(
                    'relative flex items-center gap-3 px-3 py-2 rounded-xl transition-all cursor-pointer',
                    isActive
                      ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white shadow-lg'
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                  )}
                >
                  <item.icon className="h-5 w-5 shrink-0" />

                  {!collapsed && <span>{item.name}</span>}

                  {/* ACTIVE BAR */}
                  {isActive && (
                    <motion.div
                      layoutId="active-bar"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 bg-gradient-to-b from-purple-400 to-blue-400 rounded-full"
                    />
                  )}
                </div>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      {/* FOOTER */}
      <div className="border-t border-white/10 p-4 space-y-4">

        {/* AI STATUS */}
        <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 p-3 rounded-xl">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="h-4 w-4 text-purple-400" />
            {!collapsed && (
              <span className="text-xs text-white/80">AI Status</span>
            )}
          </div>

          {!collapsed && (
            <>
              <p className="text-xs text-green-400">● AI Active</p>
              <p className="text-[10px] text-white/40">
                Real-time intelligence
              </p>
            </>
          )}
        </div>

        {/* USER */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
            R
          </div>

          {!collapsed && (
            <div>
              <p className="text-sm font-medium">Enterprise Admin</p>
              <p className="text-xs text-white/40">Secure Mode</p>
            </div>
          )}
        </div>

      </div>
    </>
  );

  // =========================
  // DESKTOP
  // =========================
  if (!isMobile) {
    return (
      <aside
        className={cn(
          'h-screen bg-white/5 backdrop-blur-xl border-r border-white/10 flex flex-col transition-all duration-300',
          collapsed ? 'w-20' : 'w-64'
        )}
      >
        {SidebarContent}
      </aside>
    );
  }

  // =========================
  // MOBILE
  // =========================
  return (
    <>
      <button
        onClick={() => setIsMobileOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 bg-white/10 rounded-lg"
      >
        <Menu className="text-white" />
      </button>

      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/60 z-40"
              onClick={() => setIsMobileOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            <motion.aside
              className="fixed left-0 top-0 w-64 h-screen bg-white/5 backdrop-blur-xl z-50"
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
            >
              <div className="flex justify-end p-4">
                <button onClick={() => setIsMobileOpen(false)}>
                  <X className="text-white" />
                </button>
              </div>

              {SidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}