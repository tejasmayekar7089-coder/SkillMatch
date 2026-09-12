import React from 'react';
import { useNavigate } from 'react-router-dom';

interface ProfileStrengthBarProps {
  strength?: number;
  delta?: string;
  onRunDiagnostic?: () => void;
}

export const ProfileStrengthBar: React.FC<ProfileStrengthBarProps> = ({
  strength = 82,
  delta = '+12% this month',
  onRunDiagnostic,
}) => {
  const navigate = useNavigate();

  return (
    <div className="relative overflow-hidden bg-surface-container-lowest rounded-xl shadow-sm p-space-lg lg:p-space-xl">
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-space-lg lg:gap-space-xl">
        <div className="flex-1 space-y-space-sm max-w-2xl">
          <div className="flex items-center gap-space-sm">
            <span className="font-headline-sm text-headline-sm text-on-surface">Profile Strength</span>
            <span className="px-2.5 py-0.5 rounded-full bg-surface-container text-primary font-label-md font-semibold">
              {strength}%
            </span>
            <span className="font-label-xs text-tertiary flex items-center gap-0.5">
              <span className="material-symbols-outlined text-[14px]">trending_up</span>
              {delta}
            </span>
          </div>

          {/* Segmented Calibration Bar */}
          <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden flex">
            <div className="bg-primary h-full rounded-l-full transition-all duration-700" style={{ width: '55%' }}></div>
            <div className="bg-tertiary h-full transition-all duration-700" style={{ width: '27%' }}></div>
            <div className="bg-surface-container-highest h-full" style={{ width: '18%' }}></div>
          </div>

          <p className="font-body-sm text-secondary">
            Complete your profile (add 1 project or cloud certification) to improve your match confidence to{' '}
            <span className="font-semibold text-on-surface">95%</span>.
          </p>
        </div>

        {/* Action Cluster */}
        <div className="flex items-center gap-space-sm shrink-0">
          <button
            onClick={onRunDiagnostic}
            className="h-10 px-space-md lg:px-space-lg rounded-xl bg-surface-container-low text-on-surface hover:bg-surface-container transition-colors font-label-md flex items-center gap-space-xs"
          >
            <span className="material-symbols-outlined text-[18px] text-secondary">switch_account</span>
            Run Diagnostic
          </button>
          <button
            onClick={() => navigate('/profile')}
            className="h-10 px-space-lg lg:px-space-xl rounded-xl bg-primary text-on-primary hover:bg-primary-container transition-colors font-label-md flex items-center gap-space-xs shadow-sm"
          >
            <span>Complete Profile</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  );
};
