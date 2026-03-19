'use client';

import { motion } from 'framer-motion';

interface RadarDataPoint {
  label: string;
  value: number; // 0-100
}

interface RadarSeries {
  name: string;
  data: RadarDataPoint[];
  color: string;
}

interface RadarChartProps {
  title: string;
  series: RadarSeries[];
  size?: number;
}

export function RadarChart({
  title,
  series,
  size = 400,
}: RadarChartProps) {
  const numAxes = series[0]?.data.length || 5;
  const angleSlice = (Math.PI * 2) / numAxes;
  const center = size / 2;
  const maxRadius = size / 2.5;

  const getCoordinates = (value: number, angleIndex: number) => {
    const angle = angleSlice * angleIndex - Math.PI / 2;
    const radius = (value / 100) * maxRadius;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    };
  };

  const generatePolygon = (data: RadarDataPoint[]) => {
    return data
      .map((point, idx) => {
        const coords = getCoordinates(point.value, idx);
        return `${coords.x},${coords.y}`;
      })
      .join(' ');
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>

      <div className="flex items-center justify-center">
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="w-full max-w-md"
          style={{ aspectRatio: '1' }}
        >
          {/* Concentric circles (levels) */}
          {[20, 40, 60, 80, 100].map(level => (
            <circle
              key={`level-${level}`}
              cx={center}
              cy={center}
              r={(level / 100) * maxRadius}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}

          {/* Axes */}
          {Array.from({ length: numAxes }).map((_, idx) => {
            const angle = angleSlice * idx - Math.PI / 2;
            const x = center + maxRadius * Math.cos(angle);
            const y = center + maxRadius * Math.sin(angle);
            return (
              <line
                key={`axis-${idx}`}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="#d1d5db"
                strokeWidth="1"
              />
            );
          })}

          {/* Axis labels */}
          {series[0]?.data.map((point, idx) => {
            const angle = angleSlice * idx - Math.PI / 2;
            const labelDistance = maxRadius + 30;
            const x = center + labelDistance * Math.cos(angle);
            const y = center + labelDistance * Math.sin(angle);
            return (
              <text
                key={`label-${idx}`}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="12"
                fill="#374151"
                fontWeight="500"
              >
                {point.label}
              </text>
            );
          })}

          {/* Data polygons */}
          {series.map((s, seriesIdx) => (
            <motion.polygon
              key={s.name}
              points={generatePolygon(s.data)}
              fill={s.color}
              fillOpacity="0.15"
              stroke={s.color}
              strokeWidth="2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: seriesIdx * 0.2, duration: 0.6 }}
            />
          ))}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-6">
        {series.map(s => (
          <div key={s.name} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: s.color }} />
            <span className="text-sm font-medium text-gray-700">{s.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
