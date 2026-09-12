import React from 'react';
import { authService, AuthUser } from '../../services/authService';

interface AdminAccessBannerProps {
  currentUser: AuthUser | null;
  onAuthorized?: () => void;
}

export const AdminAccessBanner: React.FC<AdminAccessBannerProps> = ({ currentUser, onAuthorized }) => {
  if (currentUser?.role === 'admin') {
    return null;
  }

  const handleElevate = async () => {
    try {
      await authService.login('admin@skillmatch.edu', 'AdminPassword123!');
      if (onAuthorized) {
        onAuthorized();
      } else {
        window.location.reload();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to authorize Corporate Admin credentials');
    }
  };

  return (
    <div className="p-4 rounded-2xl bg-[#0B132B] border border-blue-500/40 text-white shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400 shrink-0">
          <span className="material-symbols-outlined text-[24px]">verified_user</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white text-sm">Enterprise Talent Operations Clearance Required</h3>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Student Session
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-0.5">
            You are currently browsing with a student account ({currentUser?.name || 'Student'}). To execute administrative actions, manage listings, and view live metrics, switch to Corporate Administrator clearance.
          </p>
        </div>
      </div>
      <button
        onClick={handleElevate}
        className="whitespace-nowrap px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-md transition-all flex items-center gap-1.5 shrink-0"
      >
        <span className="material-symbols-outlined text-[16px]">admin_panel_settings</span>
        <span>Authorize Corporate Admin</span>
      </button>
    </div>
  );
};
