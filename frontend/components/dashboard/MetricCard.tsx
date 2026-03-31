interface MetricCardProps {
  title: string;
  value: string | number;
  color?: 'red' | 'green' | 'yellow' | 'blue' | 'purple' | 'cyan';
}

export default function MetricCard({ title, value, color = 'blue' }: MetricCardProps) {
  const colors = {
    red: 'from-red-500 to-red-600',
    green: 'from-green-500 to-green-600',
    yellow: 'from-yellow-500 to-yellow-600',
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    cyan: 'from-cyan-500 to-cyan-600'
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-xl p-6 shadow-lg`}>
      <h3 className="text-white/90 text-sm font-medium mb-2">{title}</h3>
      <p className="text-white text-3xl font-bold">{value}</p>
    </div>
  );
}
