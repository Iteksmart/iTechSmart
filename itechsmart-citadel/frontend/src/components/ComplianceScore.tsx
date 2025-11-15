/**
 * iTechSmart Citadel - Compliance Score Component
 * Displays compliance scores across frameworks
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

export default function ComplianceScore() {
  const frameworks = [
    { name: 'HIPAA', score: 95 },
    { name: 'PCI-DSS', score: 92 },
    { name: 'SOC2', score: 88 },
    { name: 'ISO27001', score: 90 },
    { name: 'NIST', score: 93 },
    { name: 'GDPR', score: 87 },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      {frameworks.map((framework) => (
        <div key={framework.name}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-white font-medium">{framework.name}</span>
            <span className="text-gray-400">{framework.score}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${getScoreColor(framework.score)}`}
              style={{ width: `${framework.score}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}