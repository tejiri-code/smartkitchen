'use client';

import { motion } from 'framer-motion';

interface LineDataPoint {
  label: string;
  value: number;
}

interface LineSeries {
  name: string;
  data: LineDataPoint[];
  color: string;
}

interface LineChartProps {
  title: string;
  series: LineSeries[];
  height?: number;
  showLegend?: boolean;
}

export function LineChart({
  title,
  series,
  height = 300,
  showLegend = true,
}: LineChartProps) {
  const allValues = series.flatMap(s => s.data.map(d => d.value));
  const maxValue = Math.max(...allValues);
  const minValue = Math.min(...allValues);
  const range = maxValue - minValue;

  const points = series[0]?.data.length || 0;
  const xStep = points > 1 ? 100 / (points - 1) : 0;

  const getY = (value: number) => {
    return ((value - minValue) / range) * 100;
  };

  const generatePath = (data: LineDataPoint[]) => {
    return data
      .map((point, idx) => {
        const x = idx * xStep;
        const y = 100 - getY(point.value);
        return `${x},${y}`;
      })
      .join(' ');
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>

      {showLegend && (
        <div className="flex gap-4 mb-4">
          {series.map(s => (
            <div key={s.name} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: s.color }} />
              <span className="text-sm text-gray-600">{s.name}</span>
            </div>
          ))}
        </div>
      )}

      <svg
        viewBox={`0 0 100 ${height}`}
        className="w-full border border-gray-200 rounded-lg"
        style={{ height: `${height}px` }}
      >
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map(y => (
          <line
            key={`grid-${y}`}
            x1="0"
            y1={y}
            x2="100"
            y2={y}
            stroke="#e5e7eb"
            strokeWidth="0.5"
          />
        ))}

        {/* Axes */}
        <line x1="5" y1="0" x2="5" y2="100" stroke="#d1d5db" strokeWidth="1" />
        <line x1="5" y1="100" x2="100" y2="100" stroke="#d1d5db" strokeWidth="1" />

        {/* Y-axis labels */}
        {[0, 25, 50, 75, 100].map(percent => {
          const value = minValue + (range * (100 - percent)) / 100;
          return (
            <text
              key={`label-${percent}`}
              x="2"
              y={percent}
              fontSize="2"
              fill="#6b7280"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {value.toFixed(1)}
            </text>
          );
        })}

        {/* X-axis labels */}
        {series[0]?.data.map((point, idx) => (
          <text
            key={`x-label-${idx}`}
            x={5 + idx * xStep}
            y="105"
            fontSize="2"
            fill="#6b7280"
            textAnchor="middle"
          >
            {point.label}
          </text>
        ))}

        {/* Data lines */}
        {series.map((s, seriesIdx) => (
          <motion.polyline
            key={s.name}
            points={generatePath(s.data)}
            fill="none"
            stroke={s.color}
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
            initial={{ strokeDasharray: 1000, strokeDashoffset: 1000 }}
            animate={{ strokeDasharray: 0, strokeDashoffset: 0 }}
            transition={{ delay: seriesIdx * 0.2, duration: 0.8 }}
          />
        ))}

        {/* Data points */}
        {series.map(s =>
          s.data.map((point, idx) => {
            const x = 5 + idx * xStep;
            const y = 100 - getY(point.value);
            return (
              <motion.circle
                key={`${s.name}-${idx}`}
                cx={x}
                cy={y}
                r="1"
                fill={s.color}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 + idx * 0.05 }}
              />
            );
          })
        )}
      </svg>
    </div>
  );
}
