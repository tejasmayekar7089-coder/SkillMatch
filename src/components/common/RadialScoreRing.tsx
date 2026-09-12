import React from 'react';

interface RadialScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  subtext?: string;
}

export const RadialScoreRing: React.FC<RadialScoreRingProps> = ({
  score,
  size = 80,
  strokeWidth = 3.5,
}) => {
  return (
    <div
      style={{ width: `${size}px`, height: `${size}px` }}
      className="relative flex-shrink-0 flex items-center justify-center"
    >
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
        <path
          className="text-surface-container-highest"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
        />
        <path
          className="text-primary transition-all duration-700 ease-out"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeDasharray={`${score}, 100`}
          strokeLinecap="round"
          strokeWidth={strokeWidth}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="font-headline-sm text-label-md font-bold text-on-surface tabular-nums">
          {score}%
        </span>
      </div>
    </div>
  );
};
