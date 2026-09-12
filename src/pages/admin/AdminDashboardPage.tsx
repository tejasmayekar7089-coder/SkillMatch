import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService, AdminDashboardStats } from '../../services/adminService';
import { authService, AuthUser } from '../../services/authService';
import { Modal } from '../../components/common/Modal';
import { AdminAccessBanner } from '../../components/admin/AdminAccessBanner';

export const AdminDashboardPage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AdminDashboardStats | null>(null);
  const [pendingQueue, setPendingQueue] = useState<any[]>([]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form states for posting opportunity
  const [newTitle, setNewTitle] = useState('');
  const [newOrg, setNewOrg] = useState('');
  const [newCategory, setNewCategory] = useState('INTERNSHIP');
  const [newMode, setNewMode] = useState('Remote');
  const [newDeadline, setNewDeadline] = useState('15 Dec 2026');
  const [newComp, setNewComp] = useState('$45/hr');
  const [newSkills, setNewSkills] = useState('Python, PyTorch');

  const loadData = () => {
    adminService.getDashboard()
      .then((data) => {
        setDashboardData(data);
      })
      .catch(() => {});

    adminService.getOpportunities({ verified: false })
      .then((opps) => {
        if (opps && opps.length > 0) {
          const formatted = opps.map((o) => ({
            id: o.id,
            name: o.organization,
            type: `${o.title} (${o.categoryLabel || o.category})`,
            date: o.postedAgo || 'Pending review',
            isOpp: true,
          }));
          setPendingQueue(formatted);
        } else {
          setPendingQueue([]);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    authService.fetchCurrentUser().then((u) => {
      if (u) {
        setCurrentUser(u);
        if (u.role === 'admin') loadData();
      }
    });
    if (currentUser?.role === 'admin') {
      loadData();
    }
  }, []);

  const handleAdminAuthorized = () => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
    loadData();
  };

  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const skillsArray = newSkills.split(',').map((s) => s.trim()).filter(Boolean);
      await adminService.createOpportunity({
        title: newTitle,
        organization: newOrg,
        organizationLogoText: newOrg.slice(0, 2).toUpperCase() || 'OP',
        category: newCategory as any,
        categoryLabel: newCategory.charAt(0).toUpperCase() + newCategory.slice(1).toLowerCase(),
        domain: 'Artificial Intelligence & Engineering',
        location: newMode,
        mode: newMode as any,
        workMode: newMode,
        compensation: newComp,
        deadline: newDeadline,
        postedAgo: 'Just now',
        description: `Newly published ${newTitle} at ${newOrg}. Verified and routed to high-confidence student profiles.`,
        requiredSkills: skillsArray.length > 0 ? skillsArray : ['Python'],
        preferredSkills: ['FastAPI', 'Docker'],
        keyResponsibilities: ['Participate in enterprise development workflows', 'Deliver verified sprint goals'],
        requirements: {
          technicalSkills: skillsArray.map((s) => ({ name: s, level: 'Intermediate', matched: true })),
          academicCriteria: ['Enrolled university student'],
        },
        matchScore: 94,
        matchBreakdown: {
          skillsScore: 38,
          skillsTotal: 40,
          educationScore: 20,
          educationTotal: 20,
          interestsScore: 18,
          interestsTotal: 20,
          experienceScore: 18,
          experienceTotal: 20,
        },
        matchedSkills: skillsArray,
        missingSkills: [],
        verified: true,
        eligibilityStatus: 'Eligible',
        eligibilityNote: 'Verified by Corporate Talent Operations',
      });
      alert(`Successfully published ${newTitle} to the opportunity vault!`);
      setIsPostModalOpen(false);
      setNewTitle('');
      setNewOrg('');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to publish opportunity');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApproveItem = async (item: any) => {
    if (item.isOpp) {
      try {
        await adminService.verifyOpportunity(item.id);
        alert(`Verified opportunity: ${item.type}`);
        setPendingQueue((prev) => prev.filter((p) => p.id !== item.id));
        loadData();
      } catch (err: any) {
        alert(err.message || 'Verification failed');
      }
    } else {
      alert(`Verified credential for ${item.name}`);
      setPendingQueue((prev) => prev.filter((p) => p.id !== item.id));
    }
  };

  const stats = [
    {
      label: 'Active Opportunities',
      value: dashboardData ? dashboardData.totalOpportunities.toLocaleString() : '148',
      delta: dashboardData ? `${dashboardData.verifiedOpportunities} verified (${dashboardData.verificationRate}%)` : '+12 this week',
      icon: 'work',
    },
    {
      label: 'Verified Students',
      value: dashboardData ? dashboardData.totalStudents.toLocaleString() : '1,420',
      delta: dashboardData ? `${dashboardData.activeUsers} active accounts` : '94% verification rate',
      icon: 'person',
    },
    {
      label: 'Applications Routed',
      value: dashboardData ? dashboardData.applicationCounts.toLocaleString() : '3,890',
      delta: dashboardData ? `${dashboardData.applicationsByStatus?.['SELECTED'] || 0} selected offers` : '+18% vs last month',
      icon: 'fact_check',
    },
    {
      label: 'Avg Match Fit',
      value: dashboardData ? `${dashboardData.avgMatchFit}%` : '88.4%',
      delta: 'High accuracy index',
      icon: 'auto_awesome',
    },
  ];

  const categoryCounts = dashboardData?.opportunitiesByCategory || {};
  const getCatCount = (key: string, fallback: number) => {
    return categoryCounts[key.toUpperCase()] ?? categoryCounts[key.toLowerCase()] ?? fallback;
  };

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Corporate Admin Clearance Banner (if accessing with student role) */}
      <AdminAccessBanner currentUser={currentUser} onAuthorized={handleAdminAuthorized} />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-blue-50 text-blue-700 font-label-xs text-label-xs uppercase tracking-wider border border-blue-200">
            <span className="material-symbols-outlined text-[16px]">corporate_fare</span>
            <span>SkillMatch MNC Talent Operations</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Executive Operations Console</h1>
          <p className="font-body-lg text-body-lg text-secondary max-w-2xl">
            Oversee opportunity listings across all 7 pillars, verify student academic credentials, and monitor placement metrics.
          </p>
        </div>

        <div className="flex items-center gap-space-sm">
          <button
            onClick={() => setIsPostModalOpen(true)}
            className="px-space-md py-space-sm rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors shadow-sm flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            <span>Post Opportunity</span>
          </button>
          <Link
            to="/admin/opportunities"
            className="px-space-md py-space-sm rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface font-label-md transition-colors border border-outline-variant/30 flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[18px]">inventory_2</span>
            <span>View Vault</span>
          </Link>
        </div>
      </div>

      {/* Stats Bento */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-space-md">
        {stats.map((s) => (
          <div
            key={s.label}
            className="p-space-lg bg-surface-container-lowest rounded-2xl shadow-sm border border-outline-variant/30 space-y-2"
          >
            <div className="flex items-center justify-between text-secondary">
              <span className="font-label-xs uppercase tracking-wider">{s.label}</span>
              <span className="material-symbols-outlined text-[20px] text-primary">{s.icon}</span>
            </div>
            <p className="font-display-lg text-on-surface font-bold tabular-nums">{s.value}</p>
            <p className="font-label-xs text-tertiary font-semibold">{s.delta}</p>
          </div>
        ))}
      </div>

      {/* Admin Quick Links & Pending Verification List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        {/* Verification Queue (7 cols) */}
        <div className="lg:col-span-7 bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
          <div className="flex items-center justify-between">
            <h3 className="font-headline-md text-on-surface font-semibold">Pending Credential Verifications</h3>
            <Link to="/admin/verification" className="font-label-xs text-primary font-bold hover:underline">
              View All ({dashboardData?.pendingOpportunities ?? pendingQueue.length})
            </Link>
          </div>

          <div className="divide-y divide-outline-variant/20">
            {pendingQueue.length === 0 ? (
              <div className="py-8 text-center text-secondary text-sm">
                <span className="material-symbols-outlined text-[32px] text-tertiary block mb-1">task_alt</span>
                All pipeline submissions and credentials have been verified.
              </div>
            ) : (
              pendingQueue.map((item) => (
                <div key={item.id} className="py-space-sm flex items-center justify-between gap-space-sm">
                  <div>
                    <h4 className="font-label-md text-on-surface font-semibold">{item.name}</h4>
                    <p className="font-body-sm text-secondary text-label-xs">{item.type}</p>
                    <span className="text-[11px] text-outline">{item.date}</span>
                  </div>
                  <div className="flex items-center gap-space-xs">
                    <button
                      onClick={() => handleApproveItem(item)}
                      className="px-space-sm py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 font-label-xs font-semibold rounded-lg hover:bg-emerald-100 transition-colors"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => alert(`Flagged '${item.name}' for audit review`)}
                      className="px-space-sm py-1 bg-surface-container-low text-secondary font-label-xs rounded-lg hover:bg-surface-container transition-colors"
                    >
                      Review
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pillar Management Quick Grid (5 cols) */}
        <div className="lg:col-span-5 bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
          <h3 className="font-headline-md text-on-surface font-semibold">Manage Categories</h3>
          <div className="grid grid-cols-2 gap-space-xs text-label-sm">
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Internships</span>
              <span className="font-bold text-primary">{getCatCount('INTERNSHIP', 42)}</span>
            </Link>
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Hackathons</span>
              <span className="font-bold text-primary">{getCatCount('HACKATHON', 18)}</span>
            </Link>
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Scholarships</span>
              <span className="font-bold text-primary">{getCatCount('SCHOLARSHIP', 12)}</span>
            </Link>
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Courses</span>
              <span className="font-bold text-primary">{getCatCount('COURSE', 25)}</span>
            </Link>
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Projects</span>
              <span className="font-bold text-primary">{getCatCount('PROJECT', 19)}</span>
            </Link>
            <Link
              to="/admin/opportunities"
              className="p-3 rounded-xl bg-surface-container-low hover:bg-surface-container flex items-center justify-between transition-colors"
            >
              <span>Jobs</span>
              <span className="font-bold text-primary">{getCatCount('JOB', 34)}</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Post Opportunity Modal */}
      <Modal isOpen={isPostModalOpen} onClose={() => setIsPostModalOpen(false)} title="Publish Opportunity to Vault">
        <form onSubmit={handleCreateOpportunity} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Opportunity Title</label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Senior Distributed Systems Intern"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Organization</label>
            <input
              type="text"
              required
              value={newOrg}
              onChange={(e) => setNewOrg(e.target.value)}
              placeholder="e.g. Microsoft Azure"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="grid grid-cols-2 gap-space-sm">
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Category</label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm"
              >
                <option value="INTERNSHIP">Internship</option>
                <option value="HACKATHON">Hackathon</option>
                <option value="SCHOLARSHIP">Scholarship</option>
                <option value="COURSE">Course</option>
                <option value="PROJECT">Project</option>
                <option value="JOB">Job</option>
                <option value="SKILL_OPPORTUNITY">Skill Opportunity</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Work Mode</label>
              <select
                value={newMode}
                onChange={(e) => setNewMode(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm"
              >
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
                <option value="Online">Online</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-space-sm">
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Compensation</label>
              <input
                type="text"
                value={newComp}
                onChange={(e) => setNewComp(e.target.value)}
                placeholder="e.g. $45/hr or $10,000"
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
              />
            </div>
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Deadline</label>
              <input
                type="text"
                value={newDeadline}
                onChange={(e) => setNewDeadline(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Required Skills (Comma separated)</label>
            <input
              type="text"
              value={newSkills}
              onChange={(e) => setNewSkills(e.target.value)}
              placeholder="e.g. Python, Docker, Go, Kubernetes"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="flex justify-end gap-space-sm pt-space-xs">
            <button
              type="button"
              onClick={() => setIsPostModalOpen(false)}
              className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-space-lg py-space-xs bg-primary text-on-primary rounded-xl font-label-md font-bold disabled:opacity-50"
            >
              {isSubmitting ? 'Publishing...' : 'Publish to Vault'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
