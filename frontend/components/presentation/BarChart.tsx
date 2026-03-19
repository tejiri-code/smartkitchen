'use client';

import { motion } from 'framer-motion';

interface BarData {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  title: string;
  data: BarData[];
  horizontal?: boolean;
  max?: number;
  height?: number;
  showValue?: boolean;
}

export function BarChart({
  title,
  data,
  horizontal = false,
  max,
  height = 300,
  showValue = true,
}: BarChartProps) {
  const maxValue = max || Math.max(...data.map(d => d.value));
  const defaultColor = '#FF7A18';

  if (horizontal) {
    const barHeight = Math.max(30, height / data.length);

    return (
      <div className="w-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>
        <div className="space-y-4">
          {data.map((item, idx) => (
            <div key={item.label}>
              <div className="flex items-center justify-between mb-1">
                <label className="text-sm font-medium text-gray-700">{item.label}</label>
                {showValue && <span className="text-sm text-gray-600">{item.value.toFixed(2)}</span>}
              </div>
              <div className="relative w-full h-8 bg-gray-100 rounded-lg overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.value / maxValue) * 100}%` }}
                  transition={{ delay: idx * 0.05, duration: 0.6 }}
                  className="h-full rounded-lg"
                  style={{ backgroundColor: item.color || defaultColor }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Vertical bars
  const barWidth = Math.max(40, (100 / data.length) - 2);

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>
      <div style={{ height: `${height}px` }} className="flex items-end justify-around gap-2 px-4">
        {data.map((item, idx) => (
          <motion.div
            key={item.label}
            className="flex flex-col items-center gap-2 flex-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: idx * 0.05 }}
          >
            <div className="relative" style={{ height: `${height - 60}px`, width: '100%' }}>
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: `${(item.value / maxValue) * 100}%` }}
                transition={{ delay: idx * 0.05 + 0.1, duration: 0.6 }}
                className="w-full rounded-t-lg mx-auto"
                style={{
                  backgroundColor: item.color || defaultColor,
                  maxWidth: `${barWidth}%`,
                }}
              />
            </div>
            <div className="text-center w-full">
              <p className="text-xs font-medium text-gray-700">{item.label}</p>
              {showValue && <p className="text-sm font-semibold text-gray-900">{item.value.toFixed(0)}%</p>}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
