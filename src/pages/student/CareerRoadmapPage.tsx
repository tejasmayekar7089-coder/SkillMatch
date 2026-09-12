import React, { useState, useEffect } from 'react';
import { RoadmapStep } from '../../types';
import { recommendationService } from '../../services/recommendationService';
import { profileService } from '../../services/profileService';
import { ROLE_CATEGORIES, ALL_ROLES } from './SkillGapPage';

export const CareerRoadmapPage: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState('Machine Learning Engineer');
  const [steps, setSteps] = useState<RoadmapStep[]>([]);
  const [loading, setLoading] = useState(true);

  // Initialize selected role from student profile
  useEffect(() => {
    profileService.getProfile().then((prof) => {
      if (prof?.targetRole && ALL_ROLES.includes(prof.targetRole)) {
        setSelectedRole(prof.targetRole);
      } else if (prof?.targetRole) {
        const matched = ALL_ROLES.find(
          (r) =>
            r.toLowerCase().includes(prof.targetRole.toLowerCase()) ||
            prof.targetRole.toLowerCase().includes(r.toLowerCase())
        );
        if (matched) {
          setSelectedRole(matched);
        }
      }
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    recommendationService.getRoadmap(selectedRole).then((data) => {
      setSteps(data);
      setLoading(false);
    });
  }, [selectedRole]);

  const completedSteps = steps.filter((s) => s.status === 'completed');
  const currentStep = steps.find((s) => s.status === 'current') || steps.find((s) => s.status === 'upcoming') || steps[0];
  const lastStep = steps[steps.length - 1];

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
            <span className="material-symbols-outlined text-[16px]">route</span>
            <span>Career Path</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">
            Personalized Career Roadmap
          </h1>
          <p className="font-body-lg text-body-lg text-secondary max-w-2xl">
            A verified sequence of academic milestones, capstone builds, and industry certifications tailored to your
            target role of <strong className="text-on-surface">{selectedRole}</strong>.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-space-sm">
          <div className="flex items-center gap-2">
            <label htmlFor="roadmap-role-select" className="font-label-xs text-outline uppercase tracking-wider text-[11px] whitespace-nowrap">
              Target Track:
            </label>
            <select
              id="roadmap-role-select"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-surface-container-lowest border border-outline-variant/40 font-label-md text-on-surface text-xs focus:outline-none focus:border-primary shadow-sm"
            >
              {ROLE_CATEGORIES.map((cat) => (
                <optgroup key={cat.category} label={cat.category}>
                  {cat.roles.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            <span>Export Roadmap PDF</span>
          </button>
        </div>
      </div>

      {/* Overview Progress Card */}
      <div className="p-space-xl bg-surface-container-lowest rounded-2xl shadow-sm border border-outline-variant/30 grid grid-cols-1 md:grid-cols-3 gap-space-lg">
        <div className="p-space-md bg-surface-container-low rounded-xl">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Completed Milestones</span>
          <span className="font-display-lg text-tertiary font-bold tabular-nums">
            {completedSteps.length} of {steps.length || 6}
          </span>
          <p className="font-body-sm text-secondary mt-1">
            {completedSteps.length > 0
              ? `${completedSteps[completedSteps.length - 1]?.title} verified`
              : 'Foundational prerequisites verified'}
          </p>
        </div>

        <div className="p-space-md bg-surface-container-low rounded-xl">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Active Milestone</span>
          <span className="font-headline-lg text-primary font-bold line-clamp-1">
            {currentStep?.title || 'In Progress'}
          </span>
          <p className="font-body-sm text-secondary mt-1 line-clamp-1">
            {currentStep?.description || 'Active core competency development'}
          </p>
        </div>

        <div className="p-space-md bg-surface-container-low rounded-xl">
          <span className="font-label-xs text-secondary uppercase tracking-wider block">Target Placement</span>
          <span className="font-headline-lg text-on-surface font-bold line-clamp-1">
            {lastStep?.meta || 'Graduation'}
          </span>
          <p className="font-body-sm text-secondary mt-1 line-clamp-1">
            {lastStep?.title || `${selectedRole} Placement`}
          </p>
        </div>
      </div>

      {/* Roadmap Timeline */}
      <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30">
        <h2 className="font-headline-md text-on-surface mb-space-lg">Milestone Timeline</h2>

        {loading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="relative pl-6 space-y-space-lg before:absolute before:left-[11px] before:top-3 before:bottom-3 before:w-[2px] before:bg-surface-container-highest">
            {steps.map((step) => {
              const isCompleted = step.status === 'completed';
              const isCurrent = step.status === 'current';

              return (
                <div key={step.id} className="relative flex items-start gap-space-md">
                  <div
                    className={`absolute -left-6 top-1 w-6 h-6 rounded-full flex items-center justify-center shadow-sm ${
                      isCompleted
                        ? 'bg-tertiary text-on-tertiary'
                        : isCurrent
                        ? 'bg-primary text-on-primary ring-4 ring-primary-fixed/50'
                        : 'bg-surface-container-highest text-outline'
                    }`}
                  >
                    <span className="material-symbols-outlined text-[14px]">
                      {isCompleted ? 'done' : isCurrent ? 'sync' : 'circle'}
                    </span>
                  </div>

                  <div
                    className={`rounded-xl p-space-lg w-full flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm border border-outline-variant/30 ${
                      isCurrent
                        ? 'bg-surface-container shadow-sm'
                        : isCompleted
                        ? 'bg-surface-container-low'
                        : 'bg-surface-container-lowest hover:bg-surface-container-low transition-colors'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-space-sm">
                        <span className="font-headline-sm text-on-surface font-semibold">{step.title}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-label-xs font-semibold ${
                            isCompleted
                              ? 'bg-surface-container text-tertiary'
                              : isCurrent
                              ? 'bg-primary text-on-primary'
                              : 'bg-surface-container-low text-secondary'
                          }`}
                        >
                          {step.statusLabel}
                        </span>
                      </div>
                      <p className="font-body-sm text-secondary">{step.description}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-label-xs font-semibold text-primary block">{step.meta}</span>
                      <span className="text-label-xs text-outline">{step.tag}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
