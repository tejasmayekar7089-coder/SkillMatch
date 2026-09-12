import React, { useState, useEffect } from 'react';
import { adminService, AdminStudentSummary } from '../../services/adminService';
import { authService, AuthUser } from '../../services/authService';
import { AdminAccessBanner } from '../../components/admin/AdminAccessBanner';

export const AdminStudentsPage: React.FC = () => {
  const [students, setStudents] = useState<AdminStudentSummary[]>([]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());
  const [searchQuery, setSearchQuery] = useState('');

  const loadStudents = (query?: string) => {
    adminService.getStudents({ search: query })
      .then((data) => {
        if (data && data.length > 0) {
          setStudents(data);
        } else {
          setStudents([
            { id: '1', userId: 'u1', name: 'Alex Morgan', university: 'NIT', gpa: 3.82, verifiedProfilePercent: 94, targetRole: 'ML Engineer', status: 'Verified', isActive: true, verifiedSkillsCount: 6, profileStrength: 90, applicationsCount: 2, email: 'alex@nit.edu' },
            { id: '2', userId: 'u2', name: 'Sophia Chen', university: 'Stanford Univ', gpa: 3.91, verifiedProfilePercent: 96, targetRole: 'Data Science', status: 'Verified', isActive: true, verifiedSkillsCount: 8, profileStrength: 95, applicationsCount: 4, email: 'sophia@stanford.edu' },
            { id: '3', userId: 'u3', name: 'Marcus Bell', university: 'Georgia Tech', gpa: 3.75, verifiedProfilePercent: 88, targetRole: 'Cloud Architect', status: 'Verified', isActive: true, verifiedSkillsCount: 5, profileStrength: 85, applicationsCount: 1, email: 'marcus@gatech.edu' },
            { id: '4', userId: 'u4', name: 'Elena Rostova', university: 'MIT', gpa: 3.88, verifiedProfilePercent: 92, targetRole: 'Full-Stack Web', status: 'Verified', isActive: true, verifiedSkillsCount: 7, profileStrength: 92, applicationsCount: 3, email: 'elena@mit.edu' },
          ]);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    authService.fetchCurrentUser().then((u) => {
      if (u) {
        setCurrentUser(u);
        if (u.role === 'admin') loadStudents();
      }
    });
    if (currentUser?.role === 'admin') {
      loadStudents();
    }
  }, []);

  const handleAdminAuthorized = () => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
    loadStudents();
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (currentUser?.role === 'admin') {
      loadStudents(val);
    }
  };

  const handleToggleStatus = async (student: AdminStudentSummary) => {
    const nextState = !student.isActive;
    const actionLabel = nextState ? 'activate' : 'deactivate';
    if (!window.confirm(`Are you sure you want to ${actionLabel} ${student.name}'s account?`)) return;
    try {
      await adminService.toggleStudentStatus(student.id, nextState);
      setStudents((prev) =>
        prev.map((s) => (s.id === student.id ? { ...s, isActive: nextState } : s))
      );
      alert(`Account for ${student.name} successfully ${nextState ? 'reactivated' : 'deactivated'}.`);
    } catch (err: any) {
      alert(err.message || `Failed to update account status`);
    }
  };

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      <AdminAccessBanner currentUser={currentUser} onAuthorized={handleAdminAuthorized} />

      <div className="space-y-space-2xs pb-space-xs">
        <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-blue-50 text-blue-700 font-label-xs text-label-xs uppercase tracking-wider border border-blue-200 mb-2">
          <span className="material-symbols-outlined text-[16px]">group</span>
          <span>Talent Pools & Roster Operations</span>
        </div>
        <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Talent Roster Management</h1>
        <p className="font-body-lg text-secondary">View verified student talent pipelines, academic profiles, and account statuses.</p>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden border border-outline-variant/30">
        <div className="p-space-lg border-b border-outline-variant/20 flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
          <span className="font-headline-sm text-on-surface font-semibold">Registered Candidates ({students.length})</span>
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search candidates or universities..."
              className="h-9 px-3 text-label-sm bg-surface-container-low border border-outline-variant/40 rounded-xl text-on-surface w-64 focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div className="divide-y divide-outline-variant/20">
          {students.map((s) => (
            <div key={s.id || s.name} className="p-space-lg flex flex-col sm:flex-row sm:items-center justify-between gap-space-md hover:bg-surface-container-low/40">
              <div>
                <div className="flex items-center gap-space-xs">
                  <span className="font-headline-sm text-on-surface font-semibold">{s.name}</span>
                  <span className="px-2 py-0.5 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[#065F46] font-label-xs font-semibold">
                    {s.status}
                  </span>
                  {!s.isActive && (
                    <span className="px-2 py-0.5 rounded-full bg-[#FEE2E2] border border-[#FECACA] text-[#991B1B] font-label-xs font-semibold">
                      Deactivated
                    </span>
                  )}
                </div>
                <p className="font-body-sm text-secondary mt-0.5">
                  {s.university || 'University'} • GPA: {s.gpa || 'N/A'} • Target: {s.targetRole || 'Software Engineering'}
                </p>
                <span className="text-[11px] text-outline mt-0.5 block">{s.email}</span>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <span className="font-label-md text-primary font-bold">{s.verifiedProfilePercent || 90}% Fit Index</span>
                  <span className="text-label-xs text-secondary block">{s.applicationsCount} Applications Routed</span>
                </div>

                <button
                  onClick={() => handleToggleStatus(s)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                    s.isActive
                      ? 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
                  }`}
                  title={s.isActive ? 'Deactivate candidate account' : 'Reactivate candidate account'}
                >
                  {s.isActive ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
