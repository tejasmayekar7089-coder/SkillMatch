import React from 'react';

interface MatchScoreBadgeProps {
  score: number;
  showDot?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const MatchScoreBadge: React.FC<MatchScoreBadgeProps> = ({
  score,
  showDot = true,
  size = 'md',
  className = '',
}) => {
  const isHigh = score >= 80;
  const isModerate = score >= 50 && score < 80;

  const bgBorderText = isHigh
    ? 'bg-surface-container-low text-primary'
    : isModerate
    ? 'bg-[#FFFBEB] text-[#B45309]'
    : 'bg-surface-container-low text-secondary';

  const dotColor = isHigh ? 'bg-tertiary' : isModerate ? 'bg-[#F59E0B]' : 'bg-[#94A3B8]';

  const sizeClasses =
    size === 'sm'
      ? 'px-2 py-0.5 text-label-xs font-semibold'
      : size === 'lg'
      ? 'px-4 py-2 text-headline-sm font-bold'
      : 'px-3 py-1.5 text-label-md font-bold';

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-xl ${bgBorderText} ${sizeClasses} ${className}`}
    >
      {showDot && <span className={`w-2 h-2 rounded-full ${dotColor}`}></span>}
      <span className="tabular-nums">{score}% Match</span>
    </div>
  );
};
