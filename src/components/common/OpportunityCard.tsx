import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Opportunity } from '../../types';
import { MatchScoreBadge } from './MatchScoreBadge';
import { SkillBadge } from './SkillBadge';
import { opportunityService } from '../../services/opportunityService';
import { applicationService, getStatusBadgeColor } from '../../services/applicationService';

interface OpportunityCardProps {
  opportunity: Opportunity;
  variant?: 'feed' | 'grid';
  onBookmarkChange?: () => void;
  onStatusChange?: (newStatus: string) => void;
}

const STATUS_OPTIONS = [
  { value: 'DOING', label: 'Do It (In Progress)', icon: 'play_arrow', color: 'text-blue-700 bg-blue-50' },
  { value: 'PENDING', label: 'Pending', icon: 'pending', color: 'text-amber-700 bg-amber-50' },
  { value: 'COMPLETED', label: 'Completed', icon: 'check_circle', color: 'text-emerald-700 bg-emerald-50' },
  { value: 'NOT_COMPLETED', label: 'Not Completed', icon: 'cancel', color: 'text-rose-700 bg-rose-50' },
  { value: 'ISSUED', label: 'Issued / Certified', icon: 'verified', color: 'text-purple-700 bg-purple-50' },
  { value: 'APPLIED', label: 'Applied', icon: 'send', color: 'text-indigo-700 bg-indigo-50' },
];

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
  opportunity,
  variant = 'feed',
  onBookmarkChange,
  onStatusChange,
}) => {
  const [saved, setSaved] = useState(opportunityService.isSaved(opportunity.id));
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const navigate = useNavigate();

  const handleToggleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const newStatus = opportunityService.toggleSave(opportunity.id);
    setSaved(newStatus);
    if (onBookmarkChange) onBookmarkChange();
  };

  const handleSelectStatus = async (status: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowStatusMenu(false);
    try {
      await applicationService.trackOpportunityStatus(opportunity.id, status);
      setCurrentStatus(status);
      if (onStatusChange) onStatusChange(status);
    } catch {
      setCurrentStatus(status);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'internships':
        return 'work';
      case 'hackathons':
        return 'code_blocks';
      case 'scholarships':
        return 'school';
      case 'courses':
        return 'menu_book';
      case 'projects':
        return 'terminal';
      case 'jobs':
        return 'business_center';
      case 'skill-opportunities':
        return 'bolt';
      default:
        return 'work';
    }
  };

  if (variant === 'grid') {
    // Grid card layout
    return (
      <article className="group relative flex flex-col justify-between bg-surface-container-lowest rounded-2xl p-space-lg shadow-sm hover:shadow-md transition-all border border-outline-variant/30">
        <div>
          {/* Header Row */}
          <div className="flex items-start justify-between gap-space-sm mb-space-md">
            <div className="flex items-center gap-space-sm">
              <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center font-headline-sm text-headline-sm text-primary font-bold overflow-hidden shadow-inner">
                {opportunity.organizationLogoText}
              </div>
              <div>
                <div className="flex items-center gap-space-2xs">
                  <span className="font-label-xs text-label-xs uppercase tracking-wider text-secondary">
                    {opportunity.categoryLabel}
                  </span>
                  <span className="w-1 h-1 rounded-full bg-outline-variant"></span>
                  <span className="font-label-xs text-label-xs text-primary font-medium">
                    {opportunity.organization}
                  </span>
                </div>
                <h2 className="font-headline-sm text-headline-sm text-on-surface group-hover:text-primary transition-colors leading-tight">
                  <Link to={`/opportunity/${opportunity.id}`}>{opportunity.title}</Link>
                </h2>
              </div>
            </div>

            {/* Match Badge with Tooltip Popover */}
            <div className="relative group/pop">
              <MatchScoreBadge score={opportunity.matchScore} size="sm" />

              {/* Match Breakdown Hover Overlay */}
              <div className="absolute right-0 top-8 z-30 hidden group-hover/pop:flex flex-col w-52 p-space-sm rounded-xl bg-inverse-surface text-inverse-on-surface shadow-xl space-y-space-xs pointer-events-none">
                <p className="font-label-xs text-label-xs text-inverse-primary font-medium">
                  Match Breakdown
                </p>
                <div className="space-y-1 text-label-xs">
                  <div className="flex justify-between">
                    <span>Skills Fit</span>
                    <span className="text-tertiary-fixed font-bold">
                      {opportunity.matchBreakdown.skillsFitPercent || 95}%
                    </span>
                  </div>
                  <div className="w-full h-1 bg-surface-container-highest/20 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-tertiary-fixed rounded-full"
                      style={{ width: `${opportunity.matchBreakdown.skillsFitPercent || 95}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between">
                    <span>Academic Criteria</span>
                    <span className="text-tertiary-fixed font-bold">100%</span>
                  </div>
                  <div className="w-full h-1 bg-surface-container-highest/20 rounded-full overflow-hidden">
                    <div className="h-full bg-tertiary-fixed rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Meta Details */}
          <div className="flex flex-wrap items-center gap-y-1 gap-x-space-md text-secondary font-body-sm text-body-sm mb-space-base">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px] text-outline">language</span>
              {opportunity.mode}
            </span>
            {opportunity.compensation && (
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px] text-outline">payments</span>
                {opportunity.compensation}
              </span>
            )}
            <span className="flex items-center gap-1 text-error">
              <span className="material-symbols-outlined text-[16px]">schedule</span>
              {opportunity.deadline}
            </span>
          </div>

          {/* Skill Chips */}
          <div className="flex flex-wrap gap-1.5 mb-space-base">
            {opportunity.matchedSkills.map((skill) => (
              <SkillBadge key={skill} name={skill} matched={true} />
            ))}
            {opportunity.missingSkills.map((skill) => (
              <SkillBadge key={skill} name={skill} gap={true} />
            ))}
          </div>
        </div>

        {/* Action and Status Row */}
        <div className="pt-space-md bg-surface-container-low/50 -mx-space-lg -mb-space-lg px-space-lg pb-space-lg rounded-b-2xl flex flex-col gap-space-xs border-t border-outline-variant/20">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-tertiary-fixed text-on-tertiary-fixed font-label-xs text-label-xs font-semibold">
              <span className="material-symbols-outlined text-[14px]">verified</span>
              {opportunity.eligibilityStatus === 'Eligible' ? 'Verified Eligible' : 'Partially Eligible'}
            </span>

            {/* Quick Status Pill / Menu Button */}
            <div className="relative">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowStatusMenu(!showStatusMenu);
                }}
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg font-label-xs text-label-xs font-medium transition-all shadow-xs border ${
                  currentStatus
                    ? getStatusBadgeColor(currentStatus)
                    : 'bg-surface-container-lowest text-secondary hover:text-primary hover:bg-surface-container border-outline-variant/40'
                }`}
                title="Update activity status on this listing"
              >
                <span className="material-symbols-outlined text-[14px]">
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
                    : 'tune'}
                </span>
                <span>{currentStatus ? currentStatus.replace('_', ' ') : 'Track Status'}</span>
                <span className="material-symbols-outlined text-[12px]">expand_more</span>
              </button>

              {/* Status Dropdown Popover */}
              {showStatusMenu && (
                <div
                  className="absolute right-0 bottom-full mb-1 z-40 w-48 py-1 rounded-xl bg-surface-container-lowest shadow-xl border border-outline-variant/30 divide-y divide-outline-variant/10 text-left"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="px-3 py-1.5 text-[11px] font-semibold text-secondary uppercase tracking-wider">
                    Set Platform Status
                  </div>
                  <div className="py-1">
                    {STATUS_OPTIONS.map((opt) => (
                      <button
                        key={opt.value}
                        onClick={(e) => handleSelectStatus(opt.value, e)}
                        className={`w-full px-3 py-1.5 flex items-center gap-2 text-label-xs text-left transition-colors hover:bg-surface-container-low ${
                          currentStatus === opt.value ? 'font-bold text-primary bg-surface-container' : 'text-on-surface'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[16px] text-primary">{opt.icon}</span>
                        <span>{opt.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-1">
            <button
              onClick={handleToggleSave}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-label-xs transition-colors ${
                saved
                  ? 'bg-primary/10 text-primary font-bold'
                  : 'bg-surface-container-lowest text-secondary hover:text-primary'
              }`}
              title={saved ? 'Marked / Saved to Profile' : 'Unmarked (Click to Mark)'}
            >
              <span className="material-symbols-outlined text-[16px]">
                {saved ? 'bookmark_added' : 'bookmark_border'}
              </span>
              <span>{saved ? 'Marked' : 'Mark'}</span>
            </button>
            <button
              onClick={() => navigate(`/opportunity/${opportunity.id}`)}
              className="h-8 px-space-md rounded-lg bg-primary hover:bg-primary-container text-on-primary font-label-sm text-label-sm font-medium transition-colors shadow-sm"
            >
              View Details
            </button>
          </div>
        </div>
      </article>
    );
  }

  // Feed card layout (as seen in Dashboard screen)
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-lg flex flex-col gap-space-md hover:shadow-md transition-shadow border border-outline-variant/30">
      {/* Top Details */}
      <div className="flex items-start justify-between gap-space-md">
        <div className="flex items-start gap-space-md">
          <div className="w-12 h-12 rounded-xl bg-surface-container-low flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-[28px] text-primary">
              {getCategoryIcon(opportunity.category)}
            </span>
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-space-xs mb-1">
              <span className="px-2 py-0.5 rounded font-label-xs bg-surface-container text-primary font-medium">
                {opportunity.categoryLabel}
              </span>
              <span className="font-label-xs text-secondary">• Mode: {opportunity.mode}</span>
              <span className="font-label-xs text-secondary">• Deadline: {opportunity.deadline}</span>
              {currentStatus && (
                <span className={`px-2 py-0.5 rounded-full font-label-xs font-semibold ${getStatusBadgeColor(currentStatus)}`}>
                  Status: {currentStatus.replace('_', ' ')}
                </span>
              )}
            </div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface leading-tight">
              <Link to={`/opportunity/${opportunity.id}`} className="hover:text-primary transition-colors">
                {opportunity.title}
              </Link>
            </h3>
            <p className="font-body-sm text-secondary">
              {opportunity.organization} — {opportunity.location}
            </p>
          </div>
        </div>

        {/* Match Score Badge */}
        <div className="flex flex-col items-end shrink-0">
          <MatchScoreBadge score={opportunity.matchScore} size="md" />
        </div>
      </div>

      {/* AI Match Breakdown Bar */}
      <div className="bg-surface-container-low rounded-lg p-space-sm space-y-1.5">
        <div className="flex items-center justify-between font-label-xs text-secondary">
          <span className="font-medium text-on-surface flex items-center gap-1">
            <span className="material-symbols-outlined text-[15px] text-primary">auto_awesome</span>
            Skill Match Breakdown
          </span>
          <span className="tabular-nums">
            Skills: {opportunity.matchBreakdown.skillsScore}/{opportunity.matchBreakdown.skillsTotal} • Edu:{' '}
            {opportunity.matchBreakdown.educationScore}/{opportunity.matchBreakdown.educationTotal} •
            Interests: {opportunity.matchBreakdown.interestsScore}/{opportunity.matchBreakdown.interestsTotal} •
            Exp: {opportunity.matchBreakdown.experienceScore}/{opportunity.matchBreakdown.experienceTotal}
          </span>
        </div>
        <div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden flex gap-0.5">
          <div
            className="bg-primary h-full"
            style={{ width: `${(opportunity.matchBreakdown.skillsScore / 40) * 40}%` }}
          ></div>
          <div
            className="bg-primary-container h-full"
            style={{ width: `${(opportunity.matchBreakdown.educationScore / 20) * 20}%` }}
          ></div>
          <div
            className="bg-tertiary h-full"
            style={{ width: `${(opportunity.matchBreakdown.interestsScore / 20) * 18}%` }}
          ></div>
          <div
            className="bg-tertiary-container h-full"
            style={{ width: `${(opportunity.matchBreakdown.experienceScore / 20) * 16}%` }}
          ></div>
        </div>
      </div>

      {/* Skill Tokens & Eligibility */}
      <div className="flex flex-wrap items-center gap-space-xs">
        {opportunity.matchedSkills.map((skill) => (
          <SkillBadge key={skill} name={skill} matched={true} />
        ))}
        {opportunity.missingSkills.map((skill) => (
          <SkillBadge key={skill} name={skill} gap={true} />
        ))}
      </div>

      {/* Footer Meta, Status Pill and CTAs */}
      <div className="pt-space-sm flex flex-wrap items-center justify-between gap-space-sm border-t border-outline-variant/20">
        <div className="flex items-center gap-1.5 text-tertiary font-label-xs font-semibold">
          <span className="material-symbols-outlined text-[16px]">verified</span>
          {opportunity.eligibilityNote}
        </div>
        
        <div className="flex items-center gap-space-xs flex-wrap">
          {/* Quick Platform Status Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowStatusMenu(!showStatusMenu)}
              className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg font-label-xs text-label-xs font-medium transition-all border ${
                currentStatus
                  ? getStatusBadgeColor(currentStatus)
                  : 'bg-surface-container-low hover:bg-surface-container text-secondary hover:text-primary border-outline-variant/30'
              }`}
              title="Set application or progress status"
            >
              <span className="material-symbols-outlined text-[16px]">
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
              <span>{currentStatus ? currentStatus.replace('_', ' ') : 'Track Status'}</span>
              <span className="material-symbols-outlined text-[14px]">arrow_drop_down</span>
            </button>

            {showStatusMenu && (
              <div className="absolute right-0 bottom-full mb-1 z-40 w-48 py-1 rounded-xl bg-surface-container-lowest shadow-xl border border-outline-variant/30 divide-y divide-outline-variant/10 text-left">
                <div className="px-3 py-1.5 text-[11px] font-semibold text-secondary uppercase tracking-wider">
                  Update Activity Status
                </div>
                <div className="py-1">
                  {STATUS_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={(e) => handleSelectStatus(opt.value, e)}
                      className={`w-full px-3 py-1.5 flex items-center gap-2 text-label-xs text-left transition-colors hover:bg-surface-container-low ${
                        currentStatus === opt.value ? 'font-bold text-primary bg-surface-container' : 'text-on-surface'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[16px] text-primary">{opt.icon}</span>
                      <span>{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Mark / Unmark Toggle */}
          <button
            onClick={handleToggleSave}
            aria-label="Bookmark"
            className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-colors border ${
              saved
                ? 'text-primary bg-primary/10 border-primary/20 font-semibold'
                : 'text-secondary hover:text-on-surface hover:bg-surface-container-low border-outline-variant/30'
            }`}
            title={saved ? 'Marked in Saved Opportunities' : 'Click to Mark / Bookmark'}
          >
            <span className="material-symbols-outlined text-[18px]">
              {saved ? 'bookmark_added' : 'bookmark_border'}
            </span>
            <span className="text-label-xs">{saved ? 'Marked' : 'Mark'}</span>
          </button>

          <button
            onClick={() => navigate(`/opportunity/${opportunity.id}`)}
            className="h-9 px-space-lg rounded-xl bg-primary text-on-primary hover:bg-primary-container font-label-sm font-semibold transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};
