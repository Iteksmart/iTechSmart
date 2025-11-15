/**
 * iTechSmart Supreme Plus - Metrics Chart Component
 * Displays incident trends over time
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function MetricsChart() {
  // Sample data - in production, fetch from API
  const data = [
    { date: 'Mon', incidents: 12, resolved: 10 },
    { date: 'Tue', incidents: 15, resolved: 13 },
    { date: 'Wed', incidents: 8, resolved: 8 },
    { date: 'Thu', incidents: 18, resolved: 15 },
    { date: 'Fri', incidents: 10, resolved: 9 },
    { date: 'Sat', incidents: 5, resolved: 5 },
    { date: 'Sun', incidents: 7, resolved: 6 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1e293b', 
            border: '1px solid #334155',
            borderRadius: '0.5rem'
          }}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="incidents" 
          stroke="#ef4444" 
          strokeWidth={2}
          name="Incidents Created"
        />
        <Line 
          type="monotone" 
          dataKey="resolved" 
          stroke="#22c55e" 
          strokeWidth={2}
          name="Incidents Resolved"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}