import React from 'react';

interface SkillBadgeProps {
  name: string;
  matched?: boolean;
  gap?: boolean;
  verified?: boolean;
  size?: 'sm' | 'md';
}

export const SkillBadge: React.FC<SkillBadgeProps> = ({
  name,
  gap = false,
  verified = false,
  size = 'sm',
}) => {
  const padding = size === 'sm' ? 'px-2 py-0.5 text-label-xs' : 'px-2.5 py-1 text-label-sm';

  if (verified) {
    return (
      <span
        className={`inline-flex items-center gap-1 rounded-md bg-[#ECFDF5] border border-[#A7F3D0] text-[#065F46] font-medium ${padding}`}
      >
        <span className="material-symbols-outlined text-[14px] text-tertiary">verified</span>
        <span>{name}</span>
      </span>
    );
  }

  if (gap) {
    return (
      <span
        className={`inline-flex items-center gap-1 rounded-md bg-surface-container-high text-secondary font-medium border border-dashed border-[#CBD5E1] ${padding}`}
      >
        <span className="material-symbols-outlined text-[14px] text-outline">priority_high</span>
        <span>{name}</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md bg-surface-container text-primary font-medium ${padding}`}
    >
      <span className="material-symbols-outlined text-[12px]">check</span>
      <span>{name}</span>
    </span>
  );
};
