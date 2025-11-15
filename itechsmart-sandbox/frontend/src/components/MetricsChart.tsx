import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ResourceMetric } from '../types';
import { format } from 'date-fns';

interface MetricsChartProps {
  metrics: ResourceMetric[];
  dataKey: keyof ResourceMetric;
  title: string;
  color?: string;
  unit?: string;
}

const MetricsChart: React.FC<MetricsChartProps> = ({
  metrics,
  dataKey,
  title,
  color = '#2563eb',
  unit = '',
}) => {
  const data = metrics.map((metric) => ({
    time: format(new Date(metric.timestamp), 'HH:mm:ss'),
    value: metric[dataKey] as number,
  }));

  return (
    <div className="card">
      <h3 style={{ margin: '0 0 var(--spacing-md) 0', fontSize: '16px' }}>
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
          <XAxis
            dataKey="time"
            stroke="var(--text-secondary)"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="var(--text-secondary)"
            style={{ fontSize: '12px' }}
            unit={unit}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--border-radius-sm)',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            name={title}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;