/**
 * iTechSmart Citadel - Threat Map Component
 * Visualizes threat activity
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ThreatMap() {
  const data = [
    { day: 'Mon', threats: 12 },
    { day: 'Tue', threats: 8 },
    { day: 'Wed', threats: 15 },
    { day: 'Thu', threats: 6 },
    { day: 'Fri', threats: 10 },
    { day: 'Sat', threats: 4 },
    { day: 'Sun', threats: 5 },
  ];

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="day" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1f2937', 
            border: '1px solid #374151',
            borderRadius: '0.5rem'
          }}
        />
        <Bar dataKey="threats" fill="#ef4444" />
      </BarChart>
    </ResponsiveContainer>
  );
}