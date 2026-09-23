import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Opportunity } from '../../types';
import { opportunityService } from '../../services/opportunityService';
import { applicationService } from '../../services/applicationService';
import { RadialScoreRing } from '../../components/common/RadialScoreRing';
import { Modal } from '../../components/common/Modal';

export const OpportunityDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [statusSuccessMsg, setStatusSuccessMsg] = useState<string | null>(null);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [applying, setApplying] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);
  const [coverNote, setCoverNote] = useState('');
  const [explanation, setExplanation] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      setLoading(true);
      Promise.all([
        opportunityService.getOpportunityById(id),
        opportunityService.getOpportunityMatchExplanation(id).catch(() => null),
        applicationService.getApplications().catch(() => []),
      ]).then(([data, explData, apps]) => {
        if (data) {
          setOpportunity(data);
          setSaved(opportunityService.isSaved(data.id));
          const existingApp = (apps as any[]).find((a) => a.opportunityId === data.id);
          if (existingApp) {
            setCurrentStatus(existingApp.status);
          }
        }
        if (explData) {
          setExplanation(explData);
        }
        setLoading(false);
      });
    }
  }, [id]);

  const handleToggleSave = () => {
    if (opportunity) {
      const newStatus = opportunityService.toggleSave(opportunity.id);
      setSaved(newStatus);
    }
  };

  const handleTrackStatus = async (status: string) => {
    if (!opportunity) return;
    setShowStatusMenu(false);
    try {
      await applicationService.trackOpportunityStatus(opportunity.id, status);
      setCurrentStatus(status);
      setStatusSuccessMsg(`Marked as ${status.replace('_', ' ')}!`);
      setTimeout(() => setStatusSuccessMsg(null), 3000);
    } catch {
      setCurrentStatus(status);
    }
  };

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!opportunity) return;
    setApplying(true);
    await applicationService.submitApplication(
      opportunity.id,
      opportunity.title,
      opportunity.organization,
      opportunity.category,
      coverNote
    );
    setApplying(false);
    setAppliedSuccess(true);
  };

  if (loading) {
    return (
      <div className="py-32 flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="font-body-md text-secondary mt-4">Loading opportunity details & match vectors...</p>
      </div>
    );
  }

  if (!opportunity) {
    return (
      <div className="py-20 text-center">
        <h2 className="font-headline-lg text-on-surface">Opportunity Not Found</h2>
        <p className="font-body-md text-secondary mt-2">The requested listing may have closed.</p>
        <Link to="/discover" className="mt-4 inline-block px-4 py-2 bg-primary text-on-primary rounded-xl">
          Return to Discover
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full">
      {/* Top Breadcrumb & Quick Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-space-sm mb-space-lg">
        <nav className="flex items-center gap-space-xs font-label-sm text-label-sm text-outline">
          <Link to="/discover" className="hover:text-primary transition-colors">
            Opportunities
          </Link>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <Link to={`/${opportunity.category}`} className="hover:text-primary transition-colors capitalize">
            {opportunity.categoryLabel}
          </Link>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <span className="text-on-surface-variant font-medium">{opportunity.organization}</span>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          <span className="text-primary font-medium truncate max-w-xs">{opportunity.title}</span>
        </nav>

        <div className="flex items-center gap-space-xs">
          <button
            onClick={() => {
              if (navigator.clipboard) {
                navigator.clipboard.writeText(window.location.href);
                alert('Opportunity link copied to clipboard!');
              }
            }}
            className="inline-flex items-center gap-space-xs px-space-sm py-space-2xs rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface-variant text-label-sm font-label-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">share</span>
            <span>Share</span>
          </button>
          <button
            onClick={() => alert('Report submitted to SkillMatch Trust & Safety.')}
            className="inline-flex items-center gap-space-xs px-space-sm py-space-2xs rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface-variant text-label-sm font-label-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">flag</span>
            <span>Report</span>
          </button>
        </div>
      </div>

      {/* Header Section Hero Card */}
      <div className="relative overflow-hidden rounded-xl bg-surface-container-lowest shadow-sm mb-space-2xl p-space-xl border border-outline-variant/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-xl">
          <div className="flex items-start gap-space-lg min-w-0">
            {/* Company Logo */}
            <div className="w-16 h-16 rounded-xl bg-surface-container flex items-center justify-center flex-shrink-0 shadow-sm text-primary font-display-lg text-display-lg leading-none select-none font-bold">
              {opportunity.organizationLogoText}
            </div>

            <div className="space-y-space-xs min-w-0">
              <div className="flex flex-wrap items-center gap-space-sm">
                <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight truncate">
                  {opportunity.title}
                </h1>
                <span className="inline-flex items-center gap-space-2xs px-space-sm py-space-2xs rounded-xl bg-surface-container-high text-primary font-label-xs text-label-xs uppercase tracking-wider font-semibold">
                  {opportunity.categoryLabel}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-x-space-md gap-y-space-xs font-body-sm text-body-sm text-on-surface-variant">
                <span className="font-medium text-on-surface">{opportunity.organization}</span>
                <span className="inline-block w-1 h-1 rounded-full bg-outline-variant"></span>
                <span className="inline-flex items-center gap-space-2xs">
                  <span className="material-symbols-outlined text-[16px] text-outline">location_on</span>
                  {opportunity.location}
                </span>
                <span className="inline-block w-1 h-1 rounded-full bg-outline-variant"></span>
                <span className="inline-flex items-center gap-space-2xs">
                  <span className="material-symbols-outlined text-[16px] text-outline">schedule</span>
                  {opportunity.postedAgo}
                </span>
              </div>
            </div>
          </div>

          {/* Match Pill Highlight */}
          <div className="flex items-center self-start lg:self-center">
            <div className="inline-flex items-center gap-space-sm px-space-md py-space-xs rounded-full bg-surface-container-low shadow-sm border border-outline-variant/30">
              <span className="w-2.5 h-2.5 rounded-full bg-tertiary animate-pulse"></span>
              <span className="font-headline-sm text-label-md text-primary font-semibold tabular-nums">
                {opportunity.matchScore}% Match
              </span>
              <span className="font-body-sm text-label-xs text-on-surface-variant">for your profile</span>
            </div>
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-base mt-space-xl pt-space-lg bg-surface-container-low rounded-xl p-space-base">
          <div className="space-y-space-2xs">
            <span className="font-label-xs text-label-xs text-outline uppercase tracking-wider block">Duration</span>
            <div className="flex items-center gap-space-2xs font-headline-sm text-body-md text-on-surface">
              <span className="material-symbols-outlined text-[18px] text-primary">calendar_month</span>
              <span>{opportunity.duration || 'Flexible Timeline'}</span>
            </div>
          </div>

          <div className="space-y-space-2xs">
            <span className="font-label-xs text-label-xs text-outline uppercase tracking-wider block">Stipend / Value</span>
            <div className="flex items-center gap-space-2xs font-headline-sm text-body-md text-on-surface">
              <span className="material-symbols-outlined text-[18px] text-tertiary">payments</span>
              <span className="font-semibold text-tertiary">{opportunity.compensation || 'Disclosed upon match'}</span>
            </div>
          </div>

          <div className="space-y-space-2xs">
            <span className="font-label-xs text-label-xs text-outline uppercase tracking-wider block">
              Application Deadline
            </span>
            <div className="flex items-center gap-space-2xs font-headline-sm text-body-md text-on-surface">
              <span className="material-symbols-outlined text-[18px] text-error">event_busy</span>
              <span className="font-medium text-error">{opportunity.deadline}</span>
            </div>
          </div>

          <div className="space-y-space-2xs">
            <span className="font-label-xs text-label-xs text-outline uppercase tracking-wider block">Cohort Size</span>
            <div className="flex items-center gap-space-2xs font-headline-sm text-body-md text-on-surface">
              <span className="material-symbols-outlined text-[18px] text-secondary">group</span>
              <span>{opportunity.cohortSize || 'Multiple Positions'}</span>
            </div>
          </div>
        </div>

        {/* CTA & Action Bar with Platform Tracking Controls */}
        <div className="flex flex-wrap items-center justify-between gap-space-md mt-space-lg pt-space-md border-t border-outline-variant/20">
          <div className="flex flex-wrap items-center gap-space-sm w-full sm:w-auto">
            <button
              onClick={() => setIsApplyModalOpen(true)}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-space-xs px-space-xl py-space-sm rounded-xl bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md transition-all shadow-sm"
            >
              <span>Apply Now</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>

            {/* Mark / Unmark Button */}
            <button
              onClick={handleToggleSave}
              className={`inline-flex items-center justify-center gap-space-xs px-space-base py-space-sm rounded-xl font-label-md text-label-md transition-colors shadow-sm border ${
                saved
                  ? 'bg-primary/10 text-primary border-primary/30 font-semibold'
                  : 'bg-surface-container-lowest hover:bg-surface-container-low text-on-surface border-outline-variant/30'
              }`}
              title={saved ? 'Marked in Saved List' : 'Click to Mark (Bookmark)'}
            >
              <span
                className={`material-symbols-outlined text-[18px] ${
                  saved ? 'text-primary' : 'text-outline'
                }`}
              >
                {saved ? 'bookmark_added' : 'bookmark_border'}
              </span>
              <span>{saved ? 'Marked' : 'Mark (Save)'}</span>
            </button>

            {/* Quick Status Dropdown Menu */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowStatusMenu(!showStatusMenu)}
                className="inline-flex items-center justify-center gap-space-xs px-space-base py-space-sm rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors shadow-sm border border-outline-variant/30"
              >
                <span className="material-symbols-outlined text-[18px] text-primary">
                  {currentStatus === 'DOING'
                    ? 'play_arrow'
                    : currentStatus === 'COMPLETED'
                    ? 'check_circle'
                    : currentStatus === 'PENDING'
                    ? 'pending'
                    : currentStatus === 'ISSUED'
                    ? 'verified'
                    : currentStatus === 'NOT_COMPLETED'
                    ? 'cancel'
                    : 'playlist_add_check'}
                </span>
                <span>
                  {currentStatus ? `Status: ${currentStatus.replace('_', ' ')}` : 'Set Status'}
                </span>
                <span className="material-symbols-outlined text-[16px]">expand_more</span>
              </button>

              {showStatusMenu && (
                <div
                  className="absolute left-0 top-full mt-2 z-50 w-56 py-1.5 rounded-xl bg-surface-container-lowest shadow-2xl border border-outline-variant/30 divide-y divide-outline-variant/10 text-left"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="px-3.5 py-1.5 text-[11px] font-bold text-secondary uppercase tracking-wider">
                    Platform Status Actions
                  </div>
                  <div className="py-1">
                    <button
                      onClick={() => handleTrackStatus('DOING')}
                      className="w-full px-3.5 py-2 flex items-center gap-2.5 text-label-sm text-left hover:bg-blue-50 text-blue-900 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[18px] text-blue-600">play_arrow</span>
                      <div>
                        <div className="font-semibold">Do It (In Progress)</div>
                        <div className="text-[11px] text-blue-700/70">Working on this task now</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleTrackStatus('PENDING')}
                      className="w-full px-3.5 py-2 flex items-center gap-2.5 text-label-sm text-left hover:bg-amber-50 text-amber-900 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[18px] text-amber-600">pending</span>
                      <div>
                        <div className="font-semibold">Pending</div>
                        <div className="text-[11px] text-amber-700/70">Awaiting review or prerequisite</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleTrackStatus('COMPLETED')}
                      className="w-full px-3.5 py-2 flex items-center gap-2.5 text-label-sm text-left hover:bg-emerald-50 text-emerald-900 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>
                      <div>
                        <div className="font-semibold">Completed</div>
                        <div className="text-[11px] text-emerald-700/70">Finished all deliverables</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleTrackStatus('ISSUED')}
                      className="w-full px-3.5 py-2 flex items-center gap-2.5 text-label-sm text-left hover:bg-purple-50 text-purple-900 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[18px] text-purple-600">verified</span>
                      <div>
                        <div className="font-semibold">Issued / Certified</div>
                        <div className="text-[11px] text-purple-700/70">Credential/Certificate verified</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleTrackStatus('NOT_COMPLETED')}
                      className="w-full px-3.5 py-2 flex items-center gap-2.5 text-label-sm text-left hover:bg-rose-50 text-rose-900 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[18px] text-rose-600">cancel</span>
                      <div>
                        <div className="font-semibold">Not Completed</div>
                        <div className="text-[11px] text-rose-700/70">Dropped or expired</div>
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {statusSuccessMsg && (
              <span className="inline-flex items-center gap-1 text-label-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded-lg border border-emerald-200 animate-fade-in">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                {statusSuccessMsg}
              </span>
            )}
          </div>

          <button
            onClick={() => navigate('/ai-assistant')}
            className="inline-flex items-center gap-space-xs px-space-base py-space-sm rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-label-md text-label-md transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">smart_toy</span>
            <span>Ask SkillMatch AI about this role</span>
          </button>
        </div>
      </div>

      {/* TWO-COLUMN WORKSPACE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        {/* LEFT COLUMN: Content, Role Details & Stages (col-span-7) */}
        <div className="lg:col-span-7 space-y-space-xl">
          {/* Visual Atmosphere & Team Snapshot */}
          {opportunity.imageBanner && (
            <div className="rounded-xl overflow-hidden shadow-sm bg-surface-container-lowest border border-outline-variant/30">
              <div className="relative h-52 w-full">
                <img
                  className="w-full h-full object-cover"
                  src={opportunity.imageBanner}
                  alt={opportunity.title}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-on-surface/80 via-on-surface/20 to-transparent"></div>
                <div className="absolute bottom-space-base left-space-lg right-space-lg flex items-center justify-between text-on-primary">
                  <div>
                    <p className="font-headline-sm text-body-lg font-semibold">Applied Research & Development</p>
                    <p className="font-body-sm text-label-sm text-outline-variant">
                      {opportunity.organization} • Innovation Core
                    </p>
                  </div>
                  <span className="inline-flex items-center gap-space-2xs px-space-sm py-space-2xs rounded-xl bg-on-surface/60 backdrop-blur font-label-xs text-label-xs">
                    <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
                    Mentorship Track
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Role Narrative */}
          <div className="rounded-xl bg-surface-container-lowest p-space-xl shadow-sm space-y-space-lg border border-outline-variant/30">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface mb-space-xs">About the Role</h2>
              <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
                {opportunity.description}
              </p>
            </div>

            {opportunity.keyResponsibilities && opportunity.keyResponsibilities.length > 0 && (
              <div className="space-y-space-sm">
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Key Responsibilities</h3>
                <ul className="space-y-space-xs font-body-md text-body-md text-on-surface-variant">
                  {opportunity.keyResponsibilities.map((resp, idx) => (
                    <li key={idx} className="flex items-start gap-space-sm">
                      <span className="material-symbols-outlined text-primary text-[18px] mt-0.5 flex-shrink-0">
                        check_circle
                      </span>
                      <span>{resp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Tech Stack & Requirements */}
          <div className="rounded-xl bg-surface-container-lowest p-space-xl shadow-sm space-y-space-lg border border-outline-variant/30">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface mb-space-2xs">
                Requirements & Tech Stack
              </h2>
              <p className="font-body-sm text-body-sm text-outline">
                Technologies utilized day-to-day in this position
              </p>
            </div>

            <div className="space-y-space-base">
              {(opportunity.requirements?.technicalSkills?.length || (opportunity.requiredSkills && opportunity.requiredSkills.length > 0)) ? (
                <div>
                  <span className="font-label-xs text-label-xs uppercase tracking-wider text-outline block mb-space-xs">
                    Technical Proficiency
                  </span>
                  <div className="flex flex-wrap gap-space-xs">
                    {(opportunity.requirements?.technicalSkills?.length
                      ? opportunity.requirements.technicalSkills
                      : (opportunity.requiredSkills || []).map((s: string) => ({
                          name: s,
                          level: 'Intermediate',
                          matched: (opportunity.matchedSkills || []).includes(s),
                        }))
                    ).map((skill: any) => (
                      <span
                        key={skill.name}
                        className={`inline-flex items-center gap-space-2xs px-space-sm py-space-2xs rounded-xl font-label-md text-label-sm font-medium ${
                          skill.matched
                            ? 'bg-surface-container-low text-primary'
                            : 'bg-surface-container text-on-surface-variant'
                        }`}
                      >
                        <span
                          className={`material-symbols-outlined text-[16px] ${
                            skill.matched ? 'text-tertiary' : 'text-outline'
                          }`}
                        >
                          {skill.matched ? 'check' : 'info'}
                        </span>
                        {skill.name} ({skill.level})
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}

              {(opportunity.requirements?.academicCriteria?.length || opportunity.eligibilityRequirements || (opportunity.degreeRequirements && opportunity.degreeRequirements.length > 0)) ? (
                <div className="pt-space-base border-t border-outline-variant/20">
                  <span className="font-label-xs text-label-xs uppercase tracking-wider text-outline block mb-space-sm">
                    Academic Eligibility Criteria
                  </span>
                  <div className="space-y-space-xs font-body-md text-body-md text-on-surface-variant">
                    {(opportunity.requirements?.academicCriteria?.length
                      ? opportunity.requirements.academicCriteria
                      : [
                          opportunity.eligibilityRequirements,
                          ...(opportunity.degreeRequirements || []).map((d: string) => `Degree: ${d}`),
                          ...(opportunity.branchRequirements || []).map((b: string) => `Branch: ${b}`),
                          ...(opportunity.academicYearRequirements || []).map((y: string) => `Year: ${y}`),
                        ].filter(Boolean) as string[]
                    ).map((crit: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-space-sm p-space-sm rounded-xl bg-surface-container-low">
                        <span className="material-symbols-outlined text-tertiary text-[18px] mt-0.5 flex-shrink-0">
                          verified
                        </span>
                        <span>{crit}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          {/* Application Process & Stages Timeline */}
          {opportunity.stages && opportunity.stages.length > 0 && (
            <div className="rounded-xl bg-surface-container-lowest p-space-xl shadow-sm space-y-space-lg border border-outline-variant/30">
              <div>
                <h2 className="font-headline-md text-headline-md text-on-surface mb-space-2xs">
                  Application Process & Stages
                </h2>
                <p className="font-body-sm text-body-sm text-outline">Estimated hiring pipeline duration: 3-4 weeks</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-space-md relative">
                {opportunity.stages.map((stage) => (
                  <div
                    key={stage.step}
                    className="p-space-base rounded-xl bg-surface-container-low space-y-space-xs relative"
                  >
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-label-xs text-label-xs font-bold ${
                        stage.completed
                          ? 'bg-tertiary text-on-tertiary'
                          : stage.active
                          ? 'bg-primary text-on-primary ring-2 ring-primary-container'
                          : 'bg-surface-container-highest text-primary'
                      }`}
                    >
                      {stage.step}
                    </span>
                    <h4 className="font-headline-sm text-label-md text-on-surface font-semibold">{stage.name}</h4>
                    <p className="font-body-sm text-label-xs text-on-surface-variant leading-snug">
                      {stage.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Transparent AI Match Breakdown (col-span-5) */}
        <div className="lg:col-span-5 space-y-space-xl">
          {/* Dedicated Card: "Why This Matches You" */}
          <div className="rounded-xl bg-surface-container-lowest p-space-xl shadow-sm space-y-space-lg border border-outline-variant/30">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-label-xs text-label-xs uppercase tracking-wider text-primary font-bold">
                  Explainable AI
                </span>
                <h2 className="font-headline-md text-headline-md text-on-surface">Why This Matches You</h2>
              </div>
              <span className="material-symbols-outlined text-primary text-[24px]">verified_user</span>
            </div>

            {/* Circular Score Ring & Summary */}
            <div className="flex items-center gap-space-lg p-space-base rounded-xl bg-surface-container-low">
              <RadialScoreRing score={opportunity.matchScore} size={80} />
              <div>
                <div className="font-headline-sm text-body-md text-on-surface font-semibold">
                  {explanation?.compatibilityLabel || (opportunity.matchScore >= 80 ? 'Exceptional Compatibility' : opportunity.matchScore >= 65 ? 'Strong Fit' : 'Moderate Match')}
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
                  {explanation?.summary || 'Your background satisfies key qualification benchmarks with verified confidence.'}
                </p>
              </div>
            </div>

            {/* Metric Breakdown Progress Bars */}
            <div className="space-y-space-md">
              <span className="font-label-xs text-label-xs uppercase tracking-wider text-outline block">
                Criteria Weight Breakdown
              </span>

              {/* Technical Skills */}
              <div className="space-y-space-2xs">
                <div className="flex justify-between font-label-sm text-label-sm">
                  <span className="text-on-surface font-medium">Technical Skills</span>
                  <span className="text-primary font-semibold tabular-nums">
                    {opportunity.matchBreakdown?.skillsScore ?? 35} / {opportunity.matchBreakdown?.skillsTotal ?? 40} ({Math.min(100, Math.round(((opportunity.matchBreakdown?.skillsScore ?? 35) / (opportunity.matchBreakdown?.skillsTotal || 40)) * 100))}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.round(((opportunity.matchBreakdown?.skillsScore ?? 35) / (opportunity.matchBreakdown?.skillsTotal || 40)) * 100))}%` }}
                  ></div>
                </div>
              </div>

              {/* Education & Major */}
              <div className="space-y-space-2xs">
                <div className="flex justify-between font-label-sm text-label-sm">
                  <span className="text-on-surface font-medium">Education & Major</span>
                  <span className="text-primary font-semibold tabular-nums">
                    {opportunity.matchBreakdown?.educationScore ?? 18} / {opportunity.matchBreakdown?.educationTotal ?? 20} ({Math.min(100, Math.round(((opportunity.matchBreakdown?.educationScore ?? 18) / (opportunity.matchBreakdown?.educationTotal || 20)) * 100))}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.round(((opportunity.matchBreakdown?.educationScore ?? 18) / (opportunity.matchBreakdown?.educationTotal || 20)) * 100))}%` }}
                  ></div>
                </div>
              </div>

              {/* Domain Interests */}
              <div className="space-y-space-2xs">
                <div className="flex justify-between font-label-sm text-label-sm">
                  <span className="text-on-surface font-medium">Domain Interests</span>
                  <span className="text-secondary font-semibold tabular-nums">
                    {opportunity.matchBreakdown?.interestsScore ?? 18} / {opportunity.matchBreakdown?.interestsTotal ?? 20} ({Math.min(100, Math.round(((opportunity.matchBreakdown?.interestsScore ?? 18) / (opportunity.matchBreakdown?.interestsTotal || 20)) * 100))}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.round(((opportunity.matchBreakdown?.interestsScore ?? 18) / (opportunity.matchBreakdown?.interestsTotal || 20)) * 100))}%` }}
                  ></div>
                </div>
              </div>

              {/* Practical Experience */}
              <div className="space-y-space-2xs">
                <div className="flex justify-between font-label-sm text-label-sm">
                  <span className="text-on-surface font-medium">Project / Practical Experience</span>
                  <span className="text-secondary font-semibold tabular-nums">
                    {opportunity.matchBreakdown?.experienceScore ?? 16} / {opportunity.matchBreakdown?.experienceTotal ?? 20} ({Math.min(100, Math.round(((opportunity.matchBreakdown?.experienceScore ?? 16) / (opportunity.matchBreakdown?.experienceTotal || 20)) * 100))}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.round(((opportunity.matchBreakdown?.experienceScore ?? 16) / (opportunity.matchBreakdown?.experienceTotal || 20)) * 100))}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Strong Matches in Your Profile */}
            <div className="space-y-space-xs pt-space-sm border-t border-outline-variant/20">
              <span className="font-label-xs text-label-xs uppercase tracking-wider text-tertiary font-semibold block">
                Strong Matches Detected
              </span>
              <div className="space-y-space-xs font-body-sm text-body-sm">
                {(explanation?.strongMatches && explanation.strongMatches.length > 0
                  ? explanation.strongMatches
                  : (opportunity.matchedSkills || ['Python', 'SQL']).map((s) => ({ skill: s, verificationNote: 'Verified candidate record' }))
                ).slice(0, 3).map((item: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-space-xs p-space-xs rounded-xl bg-surface-container-low">
                    <span className="material-symbols-outlined text-tertiary text-[16px] mt-0.5">check_circle</span>
                    <span className="text-on-surface">
                      <strong>{item.skill || item.name}</strong>{' '}
                      <span className="text-on-surface-variant">• {item.verificationNote || item.verification_note || 'Verified in verified assessment record'}</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Identified Skill Gap */}
            {(opportunity.missingSkills?.length > 0 || explanation?.missingSkills?.length > 0) && (
              <div className="space-y-space-xs pt-space-sm border-t border-outline-variant/20">
                <span className="font-label-xs text-label-xs uppercase tracking-wider text-error font-semibold block">
                  Identified Skill Gap
                </span>
                <div className="flex items-start gap-space-xs p-space-sm rounded-xl bg-surface-container-low text-body-sm">
                  <span className="material-symbols-outlined text-error text-[18px] mt-0.5">cancel</span>
                  <div>
                    <p className="font-medium text-on-surface">
                      {(explanation?.missingSkills || opportunity.missingSkills).join(', ')}
                    </p>
                    <p className="text-on-surface-variant font-body-sm text-label-xs mt-0.5">
                      Required for {opportunity.organization} position; not yet verified on your candidate profile.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Gap Closing Recommendation Card */}
            <div className="p-space-base rounded-xl bg-surface-container-high space-y-space-sm">
              <div className="flex items-center gap-space-xs text-primary">
                <span className="material-symbols-outlined text-[18px]">upgrade</span>
                <span className="font-label-md text-label-sm font-semibold uppercase tracking-wide">
                  Recommended Action
                </span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface leading-snug">
                {explanation?.recommendedAction?.description || (
                  (opportunity.missingSkills?.length || 0) > 0
                    ? `Take a recommended module in ${(explanation?.missingSkills || opportunity.missingSkills)[0]} to gain an estimated +8-12% match boost.`
                    : 'Your verified profile closely satisfies all stated criteria for this listing.'
                )}
              </p>
              <div className="pt-space-2xs">
                <Link
                  to="/skill-gap-analysis"
                  className="w-full inline-flex items-center justify-center gap-space-xs px-space-base py-space-xs rounded-xl bg-surface-container-lowest hover:bg-surface-container text-primary font-label-md text-label-sm font-semibold transition-colors shadow-sm"
                >
                  <span>See How to Close This Gap</span>
                  <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </Link>
              </div>
            </div>
          </div>

          {/* Recruiter & Verified Badge Panel */}
          <div className="rounded-xl bg-surface-container-lowest p-space-base shadow-sm flex items-center gap-space-base border border-outline-variant/30">
            <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-tertiary flex-shrink-0">
              <span className="material-symbols-outlined text-[22px]">verified</span>
            </div>
            <div className="min-w-0">
              <p className="font-headline-sm text-label-md text-on-surface font-semibold truncate">
                {opportunity.verifiedBy || 'Verified by SkillMatch Trust Team'}
              </p>
              <p className="font-body-sm text-label-xs text-on-surface-variant">
                Official university partner listing • Direct recruiter inbox routing
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Apply Modal */}
      <Modal
        isOpen={isApplyModalOpen}
        onClose={() => {
          setIsApplyModalOpen(false);
          setAppliedSuccess(false);
        }}
        title={`Apply to ${opportunity.title}`}
      >
        {appliedSuccess ? (
          <div className="py-space-lg text-center space-y-space-md">
            <div className="w-12 h-12 bg-surface-container-low text-tertiary rounded-full flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-[32px]">check_circle</span>
            </div>
            <h4 className="font-headline-md text-on-surface">Application Submitted!</h4>
            <p className="font-body-sm text-secondary">
              Your verified profile, GPA transcript (3.82), and project portfolio have been securely sent to{' '}
              <strong>{opportunity.organization}</strong>.
            </p>
            <div className="pt-space-sm flex justify-center gap-space-sm">
              <button
                onClick={() => {
                  setIsApplyModalOpen(false);
                  navigate('/applications');
                }}
                className="px-space-lg py-space-xs bg-primary text-on-primary rounded-xl font-label-md"
              >
                Track in Applications
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleApplySubmit} className="space-y-space-md">
            <div className="p-space-sm bg-surface-container-low rounded-xl">
              <p className="font-label-sm text-on-surface font-semibold">Verified Credentials Attached:</p>
              <ul className="text-label-xs text-secondary list-disc pl-4 mt-1 space-y-0.5">
                <li>B.Tech CS (3rd Year, NIT) • Verified GPA 3.82</li>
                <li>GitHub: NeuralClassifier (Python, PyTorch)</li>
                <li>Proctored SQL Assessment (Top 5%)</li>
              </ul>
            </div>

            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Candidate Note (Optional):</label>
              <textarea
                rows={3}
                value={coverNote}
                onChange={(e) => setCoverNote(e.target.value)}
                placeholder="Share any additional context for the hiring committee..."
                className="w-full p-2.5 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div className="flex justify-end gap-space-sm pt-space-xs">
              <button
                type="button"
                onClick={() => setIsApplyModalOpen(false)}
                className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={applying}
                className="px-space-lg py-space-xs bg-primary hover:bg-primary-container text-on-primary rounded-xl font-label-md flex items-center gap-1"
              >
                {applying ? 'Submitting...' : 'Confirm & Apply'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
