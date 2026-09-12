import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { authService, AuthUser } from '../../services/authService';
import { AdminAccessBanner } from '../../components/admin/AdminAccessBanner';

export const AdminVerificationPage: React.FC = () => {
  const [items, setItems] = useState<any[]>([
    { id: '1', student: 'Alex Morgan', type: 'Proctored Python Assessment (95%)', date: '2 hours ago', status: 'Pending', isOpportunity: false },
    { id: '2', student: 'Sophia Chen', type: 'Stanford CS229 Coursework Certificate', date: '4 hours ago', status: 'Pending', isOpportunity: false },
    { id: '3', student: 'Marcus Bell', type: 'GitHub ViT PyTorch Repository Audit', date: '1 day ago', status: 'Pending', isOpportunity: false },
    { id: '4', student: 'Elena Rostova', type: 'AWS Solutions Architect Associate Voucher', date: '2 days ago', status: 'Pending', isOpportunity: false },
  ]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());

  const loadUnverified = () => {
    adminService.getOpportunities({ verified: false })
      .then((opps) => {
        if (opps && opps.length > 0) {
          const oppItems = opps.map((opp: any) => ({
            id: opp.id,
            student: opp.organization,
            type: `Opportunity: ${opp.title} (${opp.categoryLabel || opp.category})`,
            date: opp.postedAgo || 'Recently',
            status: opp.verified ? 'Approved' : 'Pending',
            isOpportunity: true,
          }));
          setItems((prev) => {
            const existingOppIds = new Set(prev.filter((i) => i.isOpportunity).map((i) => i.id));
            const newOpps = oppItems.filter((o) => !existingOppIds.has(o.id));
            return [...newOpps, ...prev];
          });
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    authService.fetchCurrentUser().then((u) => {
      if (u) {
        setCurrentUser(u);
        if (u.role === 'admin') loadUnverified();
      }
    });
    if (currentUser?.role === 'admin') {
      loadUnverified();
    }
  }, []);

  const handleAdminAuthorized = () => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
    loadUnverified();
  };

  const handleApprove = async (id: string, isOpp?: boolean) => {
    if (isOpp) {
      try {
        await adminService.verifyOpportunity(id);
      } catch (err: any) {
        alert(err.message || 'Verification failed');
        return;
      }
    }
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'Approved' } : item)));
  };

  const handleReject = async (id: string, isOpp?: boolean) => {
    if (isOpp) {
      try {
        await adminService.rejectOpportunity(id, "Rejected in verification review");
      } catch (err: any) {
        alert(err.message || 'Rejection failed');
        return;
      }
    }
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'Rejected' } : item)));
  };

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      <AdminAccessBanner currentUser={currentUser} onAuthorized={handleAdminAuthorized} />

      <div className="space-y-space-2xs pb-space-xs">
        <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-blue-50 text-blue-700 font-label-xs text-label-xs uppercase tracking-wider border border-blue-200 mb-2">
          <span className="material-symbols-outlined text-[16px]">verified</span>
          <span>Compliance & Verification Queue</span>
        </div>
        <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Opportunity & Credential Verification</h1>
        <p className="font-body-lg text-secondary">Review and approve academic transcripts, proctored test results, and partner opportunity submissions.</p>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden border border-outline-variant/30">
        <div className="p-space-lg border-b border-outline-variant/20 flex items-center justify-between">
          <span className="font-headline-sm text-on-surface font-semibold">Verification Queue ({items.length})</span>
        </div>

        <div className="divide-y divide-outline-variant/20">
          {items.map((item) => (
            <div key={item.id} className="p-space-lg flex items-center justify-between gap-space-md hover:bg-surface-container-low/40">
              <div>
                <div className="flex items-center gap-space-xs">
                  <span className="font-headline-sm text-on-surface font-semibold">{item.student}</span>
                  <span
                    className={`px-2 py-0.5 rounded font-label-xs font-semibold ${
                      item.status === 'Approved'
                        ? 'bg-[#ECFDF5] text-[#065F46]'
                        : item.status === 'Rejected'
                        ? 'bg-[#FEE2E2] text-[#991B1B]'
                        : 'bg-surface-container text-primary'
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <p className="font-body-sm text-secondary mt-0.5">{item.type}</p>
                <span className="text-[11px] text-outline">Submitted {item.date}</span>
              </div>

              <div className="flex items-center gap-space-xs">
                {item.status === 'Pending' ? (
                  <>
                    <button
                      onClick={() => handleApprove(item.id, item.isOpportunity)}
                      className="px-space-md py-1.5 bg-primary text-on-primary font-label-sm font-semibold rounded-xl hover:bg-primary-container"
                    >
                      Approve & Verify
                    </button>
                    <button
                      onClick={() => handleReject(item.id, item.isOpportunity)}
                      className="px-space-sm py-1.5 bg-surface-container-low text-secondary font-label-sm rounded-xl hover:bg-surface-container"
                    >
                      Reject
                    </button>
                  </>
                ) : (
                  <span className="inline-flex items-center gap-1 text-tertiary font-label-sm font-semibold">
                    <span className="material-symbols-outlined text-[16px]">
                      {item.status === 'Approved' ? 'check_circle' : 'cancel'}
                    </span>
                    {item.status}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
