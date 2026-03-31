interface RiskGaugeProps {
  riskScore: number;
  size?: 'small' | 'medium' | 'large';
}

export default function RiskGauge({ riskScore, size = 'medium' }: RiskGaugeProps) {
  const sizes = {
    small: 'w-24 h-24',
    medium: 'w-32 h-32',
    large: 'w-48 h-48'
  };

  const getColor = () => {
    if (riskScore < 30) return '#22c55e';
    if (riskScore < 70) return '#eab308';
    return '#ef4444';
  };

  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (riskScore / 100) * circumference;

  return (
    <div className={`relative ${sizes[size]}`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="50%"
          cy="50%"
          r="40"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
        />
        <circle
          cx="50%"
          cy="50%"
          r="40"
          fill="none"
          stroke={getColor()}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-bold text-white text-xl">{riskScore}</span>
      </div>
    </div>
  );
}
