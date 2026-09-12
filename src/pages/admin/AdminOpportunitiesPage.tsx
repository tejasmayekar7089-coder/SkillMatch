import React, { useState, useEffect } from 'react';
import { Opportunity } from '../../types';
import { adminService } from '../../services/adminService';
import { authService, AuthUser } from '../../services/authService';
import { Modal } from '../../components/common/Modal';
import { AdminAccessBanner } from '../../components/admin/AdminAccessBanner';

export const AdminOpportunitiesPage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filterTab, setFilterTab] = useState<'ALL' | 'VERIFIED' | 'PENDING'>('ALL');
  const [title, setTitle] = useState('');
  const [org, setOrg] = useState('');
  const [category, setCategory] = useState('INTERNSHIP');
  const [mode, setMode] = useState('Remote');
  const [deadline, setDeadline] = useState('15 Nov 2026');

  const loadOpportunities = () => {
    adminService.getOpportunities().then(setOpportunities).catch(() => {});
  };

  useEffect(() => {
    authService.fetchCurrentUser().then((u) => {
      if (u) {
        setCurrentUser(u);
        if (u.role === 'admin') loadOpportunities();
      }
    });
    if (currentUser?.role === 'admin') {
      loadOpportunities();
    }
  }, []);

  const handleAdminAuthorized = () => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
    loadOpportunities();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await adminService.createOpportunity({
        title,
        organization: org,
        organizationLogoText: org.slice(0, 2).toUpperCase(),
        category: category as any,
        categoryLabel: category.charAt(0).toUpperCase() + category.slice(1).toLowerCase(),
        domain: 'AI / Machine Learning',
        location: mode,
        mode: mode as any,
        workMode: mode,
        deadline,
        postedAgo: 'Just now',
        description: `Newly published ${title} at ${org}. Verified and routed to high-confidence student profiles.`,
        requiredSkills: ['Python'],
        preferredSkills: ['FastAPI', 'Docker'],
        keyResponsibilities: ['Participate in core development workflows', 'Deliver verified sprint goals'],
        requirements: {
          technicalSkills: [{ name: 'Python', level: 'Intermediate', matched: true }],
          academicCriteria: ['Enrolled university student'],
        },
        matchScore: 92,
        matchBreakdown: {
          skillsScore: 36,
          skillsTotal: 40,
          educationScore: 20,
          educationTotal: 20,
          interestsScore: 18,
          interestsTotal: 20,
          experienceScore: 18,
          experienceTotal: 20,
        },
        matchedSkills: ['Python'],
        missingSkills: [],
        verified: true,
        eligibilityStatus: 'Eligible',
        eligibilityNote: 'Open for Verified Student Applications',
        verifiedBy: 'SkillMatch Admin Team',
      });

      setOpportunities([created, ...opportunities]);
      setIsModalOpen(false);
      setTitle('');
      setOrg('');
    } catch (err: any) {
      alert(err.message || 'Failed to create opportunity');
    }
  };

  const handleVerify = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const updated = await adminService.verifyOpportunity(id);
      setOpportunities((prev) => prev.map((o) => (o.id === id ? { ...o, verified: true } : o)));
      alert(`Verified and published '${updated.title}' to student feeds.`);
    } catch (err: any) {
      alert(err.message || 'Failed to verify opportunity');
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this opportunity?')) return;
    try {
      await adminService.deleteOpportunity(id);
      setOpportunities((prev) => prev.filter((o) => o.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete opportunity');
    }
  };

  const filteredList = opportunities.filter((opp) => {
    if (filterTab === 'VERIFIED') return opp.verified;
    if (filterTab === 'PENDING') return !opp.verified;
    return true;
  });

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      <AdminAccessBanner currentUser={currentUser} onAuthorized={handleAdminAuthorized} />

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div>
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-blue-50 text-blue-700 font-label-xs text-label-xs uppercase tracking-wider border border-blue-200 mb-2">
            <span className="material-symbols-outlined text-[16px]">work</span>
            <span>Opportunity Vault Operations</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Opportunity Management</h1>
          <p className="font-body-lg text-secondary">Manage and verify listings across all 7 opportunity pillars.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-space-lg py-space-sm rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors shadow-sm flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          <span>Create Listing</span>
        </button>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden border border-outline-variant/30">
        <div className="p-space-lg border-b border-outline-variant/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <span className="font-headline-sm text-on-surface font-semibold">Active Listings ({filteredList.length})</span>
          
          <div className="flex items-center gap-1 bg-surface-container-low p-1 rounded-xl">
            <button
              onClick={() => setFilterTab('ALL')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                filterTab === 'ALL' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-secondary'
              }`}
            >
              All ({opportunities.length})
            </button>
            <button
              onClick={() => setFilterTab('VERIFIED')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                filterTab === 'VERIFIED' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-secondary'
              }`}
            >
              Verified ({opportunities.filter((o) => o.verified).length})
            </button>
            <button
              onClick={() => setFilterTab('PENDING')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                filterTab === 'PENDING' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-secondary'
              }`}
            >
              Pending ({opportunities.filter((o) => !o.verified).length})
            </button>
          </div>
        </div>

        <div className="divide-y divide-outline-variant/20">
          {filteredList.length === 0 ? (
            <div className="p-8 text-center text-secondary text-sm">
              No opportunities found matching the selected filter.
            </div>
          ) : (
            filteredList.map((opp) => (
              <div key={opp.id} className="p-space-lg flex items-center justify-between gap-space-md hover:bg-surface-container-low/40">
                <div>
                  <div className="flex items-center gap-space-xs">
                    <span className="px-2 py-0.5 rounded font-label-xs bg-surface-container text-primary font-semibold">
                      {opp.categoryLabel || opp.category}
                    </span>
                    <span className="font-headline-sm text-on-surface font-semibold">{opp.title}</span>
                    {!opp.verified ? (
                      <span className="px-2 py-0.5 rounded font-label-xs bg-[#FEF3C7] text-[#92400E] font-semibold">
                        Pending
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded font-label-xs bg-[#ECFDF5] text-[#065F46] font-semibold flex items-center gap-0.5">
                        <span className="material-symbols-outlined text-[13px]">check_circle</span>
                        Verified
                      </span>
                    )}
                  </div>
                  <p className="font-body-sm text-secondary mt-0.5">
                    {opp.organization} • {opp.location} • Deadline: {opp.deadline}
                  </p>
                </div>
                <div className="flex items-center gap-space-xs">
                  <span className="px-2.5 py-1 rounded-full bg-surface-container-low text-primary font-bold text-label-xs">
                    {opp.matchScore}% Match Rate
                  </span>
                  {!opp.verified && (
                    <button
                      onClick={(e) => handleVerify(opp.id, e)}
                      className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-label-xs font-semibold shadow-sm transition-colors flex items-center gap-1"
                      title="Verify and publish"
                    >
                      <span className="material-symbols-outlined text-[15px]">verified</span>
                      <span>Approve</span>
                    </button>
                  )}
                  <button
                    onClick={(e) => handleDelete(opp.id, e)}
                    className="p-1.5 rounded-lg hover:bg-error/10 text-error hover:text-error transition-colors"
                    title="Delete Opportunity"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Publish New Opportunity">
        <form onSubmit={handleCreate} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Opportunity Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. AI Research Intern"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Organization</label>
            <input
              type="text"
              required
              value={org}
              onChange={(e) => setOrg(e.target.value)}
              placeholder="e.g. Google DeepMind"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="grid grid-cols-2 gap-space-sm">
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
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
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm"
              >
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
                <option value="Online">Online</option>
              </select>
            </div>
          </div>
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Application Deadline</label>
            <input
              type="text"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>
          <div className="flex justify-end gap-space-sm pt-space-xs">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-space-lg py-space-xs bg-primary text-on-primary rounded-xl font-label-md font-bold"
            >
              Publish Opportunity
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
