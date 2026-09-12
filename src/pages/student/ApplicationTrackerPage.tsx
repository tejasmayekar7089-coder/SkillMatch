import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Application } from '../../types';
import { applicationService, getStatusBadgeColor } from '../../services/applicationService';
import { Modal } from '../../components/common/Modal';

const FILTER_TABS = [
  { id: 'ALL', label: 'All Tracked' },
  { id: 'DOING', label: 'In Progress (Doing)' },
  { id: 'PENDING', label: 'Pending' },
  { id: 'COMPLETED', label: 'Completed' },
  { id: 'ISSUED', label: 'Issued / Certified' },
  { id: 'APPLIED', label: 'Applications' },
  { id: 'NOT_COMPLETED', label: 'Not Completed' },
];

const QUICK_STATUS_OPTIONS = [
  { value: 'DOING', label: 'Do It (In Progress)' },
  { value: 'PENDING', label: 'Pending' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'ISSUED', label: 'Issued / Certified' },
  { value: 'NOT_COMPLETED', label: 'Not Completed' },
  { value: 'APPLIED', label: 'Applied' },
];

export const ApplicationTrackerPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAppForHistory, setSelectedAppForHistory] = useState<Application | null>(null);
  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadApps = () => {
    setLoading(true);
    applicationService.getApplications().then((data) => {
      setApplications(data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadApps();
  }, []);

  const handleQuickStatusChange = async (app: Application, newStatus: string) => {
    setUpdatingId(app.id);
    // Optimistically update status in UI immediately
    setApplications((prev) =>
      prev.map((item) =>
        item.id === app.id
          ? {
              ...item,
              status: newStatus as any,
              statusColor: getStatusBadgeColor(newStatus),
              currentStage: `Status changed to ${newStatus}`,
            }
          : item
      )
    );

    try {
      await applicationService.trackOpportunityStatus(app.opportunityId, newStatus, `Updated via Tracker to ${newStatus}`);
      await loadApps();
    } catch {
      // fallback
    } finally {
      setUpdatingId(null);
    }
  };

  // Filter applications by active tab
  const filteredApps = applications.filter((app) => {
    if (activeTab === 'ALL') return true;
    const s = app.status?.toUpperCase();
    if (activeTab === 'DOING') return s === 'DOING' || s === 'IN PROGRESS';
    if (activeTab === 'PENDING') return s === 'PENDING' || s === 'IN REVIEW' || s === 'PLANNING';
    if (activeTab === 'COMPLETED') return s === 'COMPLETED' || s === 'DONE';
    if (activeTab === 'ISSUED') return s === 'ISSUED' || s === 'CERTIFIED';
    if (activeTab === 'NOT_COMPLETED') return s === 'NOT_COMPLETED' || s === 'NOT COMPLETED' || s === 'DROPPED';
    if (activeTab === 'APPLIED') return ['APPLIED', 'SHORTLISTED', 'INTERVIEW', 'INTERVIEWING', 'TECHNICAL ASSESSMENT', 'SELECTED', 'OFFERED', 'REJECTED'].includes(s);
    return true;
  });

  // Dynamically calculate pipeline overview numbers
  const totalTracked = applications.length;
  const doingCount = applications.filter((a) => ['DOING', 'IN PROGRESS'].includes(a.status?.toUpperCase())).length;
  const pendingCount = applications.filter((a) => ['PENDING', 'APPLIED', 'PLANNING', 'IN REVIEW', 'SAVED'].includes(a.status?.toUpperCase())).length;
  const completedOrIssued = applications.filter((a) => ['COMPLETED', 'ISSUED', 'CERTIFIED', 'SELECTED', 'OFFERED'].includes(a.status?.toUpperCase())).length;

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
            <span className="material-symbols-outlined text-[16px]">fact_check</span>
            <span>Opportunity & Application Tracker</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">
            Activity & Pipeline Tracker
          </h1>
          <p className="font-body-lg text-body-lg text-secondary max-w-2xl">
            Track your tasks, internships, hackathons, certifications, and active submissions in real-time. Update status as you progress.
          </p>
        </div>

        <Link
          to="/discover"
          className="inline-flex items-center gap-space-xs px-space-lg py-space-sm rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors shadow-sm"
        >
          <span>Find New Opportunities</span>
          <span className="material-symbols-outlined text-[18px]">add</span>
        </Link>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-md">
        <div className="p-space-lg bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Total Items Tracked</span>
          <span className="font-headline-lg text-on-surface font-bold tabular-nums">{totalTracked}</span>
        </div>
        <div className="p-space-lg bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">In Progress (Doing)</span>
          <span className="font-headline-lg text-blue-600 font-bold tabular-nums">{doingCount}</span>
        </div>
        <div className="p-space-lg bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Pending / Under Review</span>
          <span className="font-headline-lg text-amber-600 font-bold tabular-nums">{pendingCount}</span>
        </div>
        <div className="p-space-lg bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Completed & Issued</span>
          <span className="font-headline-lg text-emerald-600 font-bold tabular-nums">{completedOrIssued}</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-xl font-label-sm text-label-sm font-medium whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-primary text-on-primary shadow-sm'
                : 'bg-surface-container-lowest text-secondary hover:text-on-surface hover:bg-surface-container-low border border-outline-variant/30'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Applications & Activities Table / Cards List */}
      <div className="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden border border-outline-variant/30">
        <div className="p-space-lg border-b border-outline-variant/20 flex items-center justify-between">
          <h3 className="font-headline-sm text-on-surface font-semibold">Tracked Activities & Listings</h3>
          <span className="font-label-xs text-secondary">
            {filteredApps.length > 0 ? `${filteredApps.length} listing${filteredApps.length > 1 ? 's' : ''}` : '0 listings'}
          </span>
        </div>

        {loading ? (
          <div className="py-16 flex justify-center">
            <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredApps.length === 0 ? (
          <div className="py-20 text-center px-4">
            <span className="material-symbols-outlined text-[48px] text-outline mb-2">assignment_turned_in</span>
            <h4 className="font-headline-sm text-on-surface font-semibold">No items in "{FILTER_TABS.find(t => t.id === activeTab)?.label}"</h4>
            <p className="font-body-sm text-secondary mt-1 max-w-md mx-auto">
              You haven't marked or tracked items in this status yet. Browse opportunities to start tracking.
            </p>
            <Link
              to="/discover"
              className="mt-4 inline-block px-space-lg py-space-xs bg-primary text-on-primary rounded-xl font-label-md"
            >
              Explore Opportunities
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-outline-variant/20">
            {filteredApps.map((app) => (
              <div
                key={app.id}
                className="p-space-lg flex flex-col md:flex-row md:items-center justify-between gap-space-md hover:bg-surface-container-low/40 transition-colors"
              >
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center gap-space-sm flex-wrap">
                    <span className="font-headline-sm text-on-surface font-semibold">
                      <Link to={`/opportunity/${app.opportunityId}`} className="hover:text-primary transition-colors">
                        {app.opportunityTitle}
                      </Link>
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-label-xs font-semibold ${getStatusBadgeColor(app.status)}`}>
                      {app.status}
                    </span>
                  </div>
                  <p className="font-body-sm text-secondary">
                    {app.organization} • Updated: {app.appliedDate}
                  </p>
                  <p className="font-body-sm text-on-surface-variant flex items-center gap-1 text-label-xs">
                    <span className="material-symbols-outlined text-[16px] text-primary">arrow_forward</span>
                    <strong>Stage:</strong> {app.currentStage}
                  </p>
                  {app.statusHistory && app.statusHistory.length > 0 && (
                    <button
                      onClick={() => setSelectedAppForHistory(app)}
                      className="inline-flex items-center gap-1 font-label-xs text-primary hover:underline mt-0.5"
                    >
                      <span className="material-symbols-outlined text-[14px]">history</span>
                      <span>Timeline ({app.statusHistory.length} event{app.statusHistory.length > 1 ? 's' : ''})</span>
                    </button>
                  )}
                </div>

                <div className="flex flex-wrap items-center justify-between md:flex-col md:items-end gap-space-xs shrink-0">
                  <div className="text-right">
                    <span className="font-label-xs text-error font-semibold block">{app.nextDeadline}</span>
                    <span className="font-label-xs text-primary font-bold">{app.matchScore}% Match Index</span>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Inline Quick Status Selector */}
                    <select
                      value={app.status}
                      disabled={updatingId === app.id}
                      onChange={(e) => handleQuickStatusChange(app, e.target.value)}
                      className="px-2.5 py-1.5 rounded-xl bg-surface-container border border-outline-variant/40 text-on-surface font-label-xs font-medium focus:outline-none focus:border-primary"
                    >
                      {QUICK_STATUS_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>

                    <button
                      onClick={() => setSelectedAppForHistory(app)}
                      className="px-space-md py-1.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-label-sm font-semibold transition-colors"
                    >
                      History
                    </button>
                    <Link
                      to={`/opportunity/${app.opportunityId}`}
                      className="px-space-md py-1.5 rounded-xl bg-surface-container-low hover:bg-surface-container text-secondary font-label-sm transition-colors"
                    >
                      View
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Application Progress History Modal */}
      {selectedAppForHistory && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedAppForHistory(null)}
          title={`Progress History: ${selectedAppForHistory.opportunityTitle}`}
        >
          <div className="space-y-space-md">
            <div className="p-space-sm bg-surface-container-low rounded-xl flex items-center justify-between">
              <div>
                <p className="font-label-sm text-on-surface font-semibold">{selectedAppForHistory.organization}</p>
                <p className="font-label-xs text-secondary">Initial Submission: {selectedAppForHistory.appliedDate}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-label-xs font-semibold ${getStatusBadgeColor(
                  selectedAppForHistory.status
                )}`}
              >
                {selectedAppForHistory.status}
              </span>
            </div>

            <div>
              <h5 className="font-label-md text-on-surface font-semibold mb-space-sm flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[18px] text-primary">timeline</span>
                Status Transition Timeline
              </h5>

              {(!selectedAppForHistory.statusHistory || selectedAppForHistory.statusHistory.length === 0) ? (
                <div className="p-space-md bg-surface-container-lowest border border-outline-variant/30 rounded-xl text-center">
                  <p className="font-body-sm text-secondary">Application submitted and currently in initial queue.</p>
                </div>
              ) : (
                <div className="relative pl-6 space-y-space-md before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-outline-variant/40">
                  {selectedAppForHistory.statusHistory.map((entry, idx) => (
                    <div key={idx} className="relative space-y-0.5">
                      <div className="absolute -left-6 top-1 w-3.5 h-3.5 rounded-full bg-primary ring-4 ring-surface-container-lowest"></div>
                      <div className="flex items-center justify-between gap-space-sm">
                        <span className="font-label-sm font-semibold text-on-surface">
                          {entry.status}
                        </span>
                        <span className="font-label-xs text-secondary">
                          {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'Recently'}
                        </span>
                      </div>
                      {entry.stage && (
                        <p className="font-body-sm text-label-xs text-on-surface-variant">
                          <strong>Stage:</strong> {entry.stage}
                        </p>
                      )}
                      {entry.notes && (
                        <p className="font-body-sm text-label-xs text-secondary italic">
                          "{entry.notes}"
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-space-xs flex justify-end">
              <button
                onClick={() => setSelectedAppForHistory(null)}
                className="px-space-md py-space-xs bg-surface-container hover:bg-surface-container-high rounded-xl font-label-md text-on-surface"
              >
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
