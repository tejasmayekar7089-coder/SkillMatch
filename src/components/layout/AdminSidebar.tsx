import React, { useState, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { authService, AuthUser } from '../../services/authService';

interface AdminSidebarProps {
  onCloseMobile?: () => void;
}

export const AdminSidebar: React.FC<AdminSidebarProps> = ({ onCloseMobile }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());
  const navigate = useNavigate();

  useEffect(() => {
    authService.fetchCurrentUser().then((user) => {
      if (user) setCurrentUser(user);
    });
  }, []);

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  const adminNavSections = [
    {
      title: 'Talent & Opportunity Pipeline',
      items: [
        { to: '/admin', label: 'Executive Overview', icon: 'dashboard', badge: 'Live' },
        { to: '/admin/opportunities', label: 'Opportunity Vault', icon: 'work', badge: '16 Active' },
        { to: '/admin/verification', label: 'Compliance & Verification', icon: 'verified_user', badge: 'Action Required' },
        { to: '/admin/students', label: 'Talent Roster & Pools', icon: 'badge' },
      ],
    },
    {
      title: 'Intelligence & Operations',
      items: [
        { to: '/admin/analytics', label: 'Pipeline Intelligence', icon: 'query_stats' },
        { to: '/admin/settings', label: 'System Governance', icon: 'tune' },
      ],
    },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-[#0B132B] text-[#E0E6ED] border-r border-[#1C2541] z-50 flex flex-col justify-between overflow-y-auto font-sans shadow-2xl">
      <div className="flex flex-col">
        {/* MNC Corporate Brand Header */}
        <div className="h-20 px-5 flex items-center justify-between border-b border-[#1C2541] bg-[#0A1024]">
          <Link to="/admin" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-md shadow-blue-500/20">
              <span className="material-symbols-outlined text-[20px] text-white">admin_panel_settings</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-white tracking-tight text-sm">SkillMatch</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30">MNC</span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium tracking-wide">Enterprise Ops Console</p>
            </div>
          </Link>
        </div>

        {/* Global Security / Status Banner */}
        <div className="mx-3 mt-3.5 px-3 py-2 rounded-xl bg-[#1C2541]/70 border border-[#2E3C62] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300 font-medium text-[11px]">System Online</span>
          </div>
          <span className="text-[10px] uppercase font-bold text-blue-400 bg-blue-900/40 px-1.5 py-0.5 rounded border border-blue-500/20">
            RBAC Active
          </span>
        </div>

        {/* Navigation Sections */}
        <nav className="px-3 py-4 space-y-6">
          {adminNavSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-1">
              <p className="px-3 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {section.title}
              </p>
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/admin'}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                        : 'text-slate-300 hover:bg-[#1C2541] hover:text-white'
                    }`
                  }
                >
                  <div className="flex items-center gap-2.5">
                    <span className="material-symbols-outlined text-[19px] opacity-90">{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-md font-semibold bg-white/10 text-slate-200">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
      </div>

      {/* Operator Status & Portal Switch Footer */}
      <div className="p-3 border-t border-[#1C2541] bg-[#0A1024] space-y-2">
        {/* Admin User Card */}
        <div className="p-2 rounded-xl bg-[#131E3D] border border-[#23315B] flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-300 font-bold text-xs shrink-0">
              {currentUser?.role === 'admin' ? 'AD' : 'OP'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate leading-tight">
                {currentUser?.role === 'admin' ? currentUser.name : 'Corporate Admin'}
              </p>
              <p className="text-[10px] text-emerald-400 font-medium">Tier-1 Administrator</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out of Admin"
            className="p-1 text-slate-400 hover:text-rose-400 transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">logout</span>
          </button>
        </div>

        {/* Portal Switcher Button */}
        <Link
          to="/dashboard"
          className="w-full px-3 py-2 rounded-xl bg-[#1C2541] hover:bg-[#253259] text-slate-200 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors border border-slate-700/50"
        >
          <span className="material-symbols-outlined text-[16px] text-blue-400">switch_account</span>
          <span>Switch to Student View</span>
        </Link>
      </div>
    </aside>
  );
};
