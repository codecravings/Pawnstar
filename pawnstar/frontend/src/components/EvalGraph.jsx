import React from 'react';

const EvalGraph = ({ values }) => {
  if (!values || values.length === 0) {
    return (
      <div className="h-32 bg-bg rounded border border-gray-600 flex items-center justify-center">
        <span className="text-gray-400 text-sm">No evaluation data</span>
      </div>
    );
  }

  const maxValue = Math.max(Math.abs(Math.max(...values)), Math.abs(Math.min(...values)), 200);
  const height = 128;
  const width = 300;
  const padding = 20;

  const normalizeValue = (value) => {
    const clamped = Math.max(-maxValue, Math.min(maxValue, value));
    return ((clamped / maxValue) * (height - padding * 2) / 2) + height / 2;
  };

  const points = values.map((value, index) => ({
    x: (index / (values.length - 1)) * (width - padding * 2) + padding,
    y: normalizeValue(-value) // Invert Y axis so positive is up
  }));

  const pathData = points.reduce((path, point, index) => {
    return path + (index === 0 ? `M ${point.x} ${point.y}` : ` L ${point.x} ${point.y}`);
  }, '');

  return (
    <div className="bg-bg rounded border border-gray-600 p-2">
      <svg width={width} height={height} className="w-full">
        {/* Center line */}
        <line
          x1={padding}
          y1={height / 2}
          x2={width - padding}
          y2={height / 2}
          stroke="#374151"
          strokeWidth="1"
          strokeDasharray="4,4"
        />
        
        {/* Grid lines */}
        {[-200, -100, 100, 200].map(value => {
          const y = normalizeValue(-value);
          return (
            <g key={value}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="#374151"
                strokeWidth="0.5"
                opacity="0.5"
              />
              <text
                x={padding - 5}
                y={y + 3}
                fill="#9CA3AF"
                fontSize="10"
                textAnchor="end"
              >
                {value > 0 ? `+${value}` : value}
              </text>
            </g>
          );
        })}
        
        {/* Evaluation line */}
        <path
          d={pathData}
          stroke="#22D3EE"
          strokeWidth="2"
          fill="none"
          className="eval-line"
        />
        
        {/* Points */}
        {points.map((point, index) => {
          const value = values[index];
          const isBlunder = Math.abs(value) >= 150;
          
          return (
            <circle
              key={index}
              cx={point.x}
              cy={point.y}
              r={isBlunder ? "4" : "2"}
              fill={isBlunder ? "#FF6B6B" : "#22D3EE"}
              className={isBlunder ? "blunder-pulse" : ""}
            />
          );
        })}
      </svg>
      
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span>Move 1</span>
        <span>Evaluation Graph</span>
        <span>Move {values.length}</span>
      </div>
    </div>
  );
};

export default EvalGraph;