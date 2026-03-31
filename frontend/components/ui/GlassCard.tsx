interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
}

export default function GlassCard({ children, className = '' }: GlassCardProps) {
  return (
    <div className={`bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-xl ${className}`}>
      {children}
    </div>
  );
}
