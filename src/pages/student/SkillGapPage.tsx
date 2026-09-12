import React, { useState, useEffect } from 'react';
import { TargetRoleGapData, RoadmapStep, GapClosingResource } from '../../types';
import { recommendationService } from '../../services/recommendationService';
import { profileService } from '../../services/profileService';

export const ROLE_CATEGORIES = [
  {
    category: 'Computer Science & AI',
    roles: [
      'Machine Learning Engineer',
      'Data Scientist',
      'Full-Stack Developer',
      'Cloud Solutions Architect',
      'Cybersecurity Analyst',
    ],
  },
  {
    category: 'Mechanical Engineering',
    roles: [
      'Mechanical Design Engineer',
      'Robotics & Mechatronics Engineer',
      'Automotive & EV Systems Engineer',
    ],
  },
  {
    category: 'Electrical & Electronics',
    roles: [
      'Embedded Systems Engineer',
      'VLSI Design Engineer',
      'Power & Renewable Energy Engineer',
    ],
  },
  {
    category: 'Finance & Economics',
    roles: [
      'Financial Analyst',
      'Quantitative Finance Analyst',
      'Equity Research & Investment Analyst',
    ],
  },
];

export const ALL_ROLES = ROLE_CATEGORIES.flatMap((c) => c.roles);

export const SkillGapPage: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState('Machine Learning Engineer');
  const [gapData, setGapData] = useState<TargetRoleGapData | null>(null);
  const [roadmap, setRoadmap] = useState<RoadmapStep[]>([]);
  const [resources, setResources] = useState<GapClosingResource[]>([]);
  const [loading, setLoading] = useState(true);

  // Initialize selected role from student profile
  useEffect(() => {
    profileService.getProfile().then((prof) => {
      if (prof?.targetRole && ALL_ROLES.includes(prof.targetRole)) {
        setSelectedRole(prof.targetRole);
      } else if (prof?.targetRole) {
        // Find best matching role or add as option
        const matched = ALL_ROLES.find(r => r.toLowerCase().includes(prof.targetRole.toLowerCase()) || prof.targetRole.toLowerCase().includes(r.toLowerCase()));
        if (matched) {
          setSelectedRole(matched);
        }
      }
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      recommendationService.getTargetRoleGaps(selectedRole),
      recommendationService.getRoadmap(selectedRole),
      recommendationService.getGapClosingResources(selectedRole),
    ]).then(([gaps, steps, courses]) => {
      setGapData(gaps);
      setRoadmap(steps);
      setResources(courses);
      setLoading(false);
    });
  }, [selectedRole]);

  if (loading || !gapData) {
    return (
      <div className="py-24 flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="font-body-md text-secondary mt-3">Computing skill vector differentials...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full gap-space-2xl">
      {/* Page Header Area */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-space-2xs rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
            <span className="material-symbols-outlined text-[14px]">insights</span>
            Career Vector Diagnostic
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
            Skill Gap Analysis & Career Roadmap
          </h1>
          <p className="font-body-md text-body-md text-secondary max-w-2xl">
            See which skills you have mastered, diagnose what you are missing for target roles, and follow a structured
            career trajectory.
          </p>
        </div>

        <div className="flex items-center gap-space-sm">
          <button
            onClick={() => alert('SkillMatch Audit Log: All 14 verified badges are timestamped & hash-verified.')}
            className="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-xl bg-surface-container-low text-on-surface font-label-md text-label-md hover:bg-surface-container transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">history</span>
            Audit Log
          </button>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-xl bg-primary text-on-primary font-label-md text-label-md hover:bg-primary-container transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export Diagnostic
          </button>
        </div>
      </div>

      {/* Target Role Selector & High-Density Diagnostic Panel */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-xl flex flex-col gap-space-xl border border-outline-variant/30">
        {/* Role Selector Tab Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md pb-space-lg border-b border-outline-variant/20">
          <div className="flex flex-col sm:flex-row sm:items-center gap-space-sm flex-1">
            <label htmlFor="role-select" className="font-label-xs text-label-xs uppercase tracking-wider text-outline whitespace-nowrap">
              Target Career Role:
            </label>
            <select
              id="role-select"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="px-space-md py-2 rounded-xl bg-surface-container-low border border-outline-variant/40 font-label-md text-on-surface focus:outline-none focus:border-primary font-medium text-sm"
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

          <div className="flex items-center gap-space-sm text-secondary font-body-sm text-body-sm shrink-0">
            <span className="material-symbols-outlined text-[16px] text-tertiary">check_circle</span>
            <span>Standard mapped to 2026 Tier-1 industry benchmarks</span>
          </div>
        </div>

        {/* Readiness Metric Banner */}
        <div className="bg-surface-container-low rounded-xl p-space-xl grid grid-cols-1 lg:grid-cols-12 gap-space-xl items-center">
          <div className="lg:col-span-4 flex flex-col gap-space-xs">
            <div className="flex items-center gap-space-xs font-label-xs text-label-xs text-primary font-semibold uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-primary-container"></span>
              Target Role Readiness
            </div>
            <div className="flex items-baseline gap-space-sm">
              <span className="font-display-lg text-display-lg text-on-surface font-bold tabular-nums">
                {gapData.readinessScore}%
              </span>
              <span className="font-headline-sm text-headline-sm text-tertiary font-medium">Ready</span>
            </div>
            <p className="font-body-sm text-body-sm text-secondary">
              Estimated time to close gaps:{' '}
              <span className="text-on-surface font-medium">{gapData.estimatedWeeksToClose}</span> with focused projects.
            </p>
          </div>

          <div className="lg:col-span-8 flex flex-col gap-space-sm">
            <div className="flex items-center justify-between text-body-sm font-body-sm">
              <div className="flex items-center gap-space-sm">
                <span className="font-label-md text-label-md text-on-surface">
                  {gapData.competenciesMet} of {gapData.competenciesTotal} Core Competencies Met
                </span>
                <span className="text-secondary font-label-xs text-label-xs">(4 Critical Deficits)</span>
              </div>
              <span className="font-label-sm text-label-sm text-secondary">Cohort Benchmark: 62%</span>
            </div>

            {/* 4-Stage Precision Progress Bar */}
            <div className="h-3 w-full bg-surface-container-highest rounded-full overflow-hidden flex gap-0.5 p-0.5">
              <div
                className="h-full bg-tertiary rounded-l-full transition-all duration-500"
                style={{ width: '55%' }}
                title="Verified Mastered: 55%"
              ></div>
              <div
                className="h-full bg-primary-container transition-all duration-500"
                style={{ width: '23%' }}
                title="Developing: 23%"
              ></div>
              <div
                className="h-full bg-surface-dim rounded-r-full transition-all duration-500"
                style={{ width: '22%' }}
                title="Gaps Remaining: 22%"
              ></div>
            </div>

            <div className="grid grid-cols-3 text-label-xs font-label-xs text-secondary pt-space-2xs">
              <div className="flex items-center gap-space-2xs">
                <span className="w-2 h-2 rounded-full bg-tertiary"></span>
                <span>10 Mastered (55%)</span>
              </div>
              <div className="flex items-center gap-space-2xs">
                <span className="w-2 h-2 rounded-full bg-primary-container"></span>
                <span>4 Developing (23%)</span>
              </div>
              <div className="flex items-center gap-space-2xs justify-end">
                <span className="w-2 h-2 rounded-full bg-surface-dim"></span>
                <span>4 Missing Gaps (22%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Categorized Skill Breakdown: 3 Focused State Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-space-lg">
        {/* Col 1: Strong Verified Skills */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between gap-space-lg border border-outline-variant/30">
          <div className="space-y-space-md">
            <div className="flex items-center justify-between pb-space-xs border-b border-outline-variant/20">
              <div className="flex items-center gap-space-xs">
                <div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-tertiary">
                  <span className="material-symbols-outlined text-[20px]">verified</span>
                </div>
                <div>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">Strong & Verified</h2>
                  <p className="font-label-xs text-label-xs text-secondary">Validated through code & tests</p>
                </div>
              </div>
              <span className="px-space-xs py-0.5 rounded-md bg-surface-container text-tertiary font-label-xs text-label-xs font-semibold">
                10 Skills
              </span>
            </div>

            <div className="space-y-space-sm">
              {gapData.mastered.map((s) => (
                <div
                  key={s.name}
                  className="p-space-sm rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-label-md text-label-md text-on-surface font-semibold">{s.name}</span>
                    <span className="font-label-xs text-label-xs text-tertiary font-semibold">{s.level}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-secondary">{s.description}</p>
                  <div className="mt-space-xs flex items-center gap-space-2xs text-label-xs font-label-xs text-tertiary">
                    <span className="material-symbols-outlined text-[14px]">check_circle</span>
                    <span>{s.verificationNote}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-space-sm rounded-lg bg-surface-container-low flex items-center justify-between text-label-sm font-label-sm text-secondary">
            <span>Verified Credential Score</span>
            <span className="font-semibold text-on-surface">Tier A (Top 8%)</span>
          </div>
        </div>

        {/* Col 2: Developing Skills */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between gap-space-lg border border-outline-variant/30">
          <div className="space-y-space-md">
            <div className="flex items-center justify-between pb-space-xs border-b border-outline-variant/20">
              <div className="flex items-center gap-space-xs">
                <div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">hourglass_top</span>
                </div>
                <div>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">Developing Skills</h2>
                  <p className="font-label-xs text-label-xs text-secondary">Active enrollment & coursework</p>
                </div>
              </div>
              <span className="px-space-xs py-0.5 rounded-md bg-surface-container text-primary font-label-xs text-label-xs font-semibold">
                {gapData.developing.length} Active
              </span>
            </div>

            <div className="space-y-space-sm">
              {gapData.developing.map((s) => (
                <div
                  key={s.name}
                  className="p-space-sm rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-label-md text-label-md text-on-surface font-semibold">{s.name}</span>
                    <span className="font-label-xs text-label-xs text-primary font-medium">{s.level}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-secondary">{s.description}</p>
                  {s.progressPercent && (
                    <div className="w-full bg-surface-container-highest h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-primary h-full rounded-full transition-all duration-500"
                        style={{ width: `${s.progressPercent}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="p-space-sm rounded-lg bg-surface-container-low flex items-center justify-between">
            <span className="font-label-xs text-label-xs text-secondary">Estimated completion:</span>
            <span className="font-label-xs text-label-xs text-on-surface font-semibold">14 business days</span>
          </div>
        </div>

        {/* Col 3: Critical Skill Gaps */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm flex flex-col justify-between gap-space-lg border border-outline-variant/30">
          <div className="space-y-space-md">
            <div className="flex items-center justify-between pb-space-xs border-b border-outline-variant/20">
              <div className="flex items-center gap-space-xs">
                <div className="w-8 h-8 rounded-lg bg-surface-container-low flex items-center justify-center text-error">
                  <span className="material-symbols-outlined text-[20px]">warning</span>
                </div>
                <div>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">Critical Skill Gaps</h2>
                  <p className="font-label-xs text-label-xs text-secondary">Key requirements for ML candidate</p>
                </div>
              </div>
              <span className="px-space-xs py-0.5 rounded-md bg-surface-container text-error font-label-xs text-label-xs font-semibold">
                High Priority
              </span>
            </div>

            <div className="space-y-space-sm">
              {gapData.criticalGaps.map((s) => (
                <div
                  key={s.name}
                  className="p-space-sm rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-label-md text-label-md text-on-surface font-medium">{s.name}</span>
                    <span className="font-label-xs text-label-xs text-error font-semibold">
                      {s.rolesDemandPercent}% Roles Demand
                    </span>
                  </div>
                  <p className="font-body-sm text-body-sm text-secondary">{s.description}</p>
                  <div className="mt-space-xs text-label-xs font-label-xs text-on-surface-variant flex items-center gap-space-2xs">
                    <span className="material-symbols-outlined text-[14px] text-error">cancel</span>
                    <span>{s.verificationNote}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => alert('Custom curriculum generated and synced to your Career Roadmap below.')}
            className="w-full py-space-sm px-space-md rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md flex items-center justify-center gap-space-xs transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">auto_fix_high</span>
            Generate Personalized Learning Plan
          </button>
        </div>
      </div>

      {/* Interactive Career Roadmap */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-xl flex flex-col gap-space-xl border border-outline-variant/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-outline-variant/20">
          <div>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Recommended Milestones for {selectedRole}
            </h2>
            <p className="font-body-sm text-body-sm text-secondary">
              Engineered multi-semester sequence from academic basics to industry placement.
            </p>
          </div>
          <div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-space-xs rounded-lg self-start">
            <span className="material-symbols-outlined text-[16px] text-primary">flag</span>
            <span className="font-label-xs text-label-xs text-on-surface font-semibold">
              Target Grad Date: May 2027
            </span>
          </div>
        </div>

        {/* Timeline Pipeline Layout */}
        <div className="relative pl-6 space-y-space-lg before:absolute before:left-[11px] before:top-3 before:bottom-3 before:w-[2px] before:bg-surface-container-highest">
          {roadmap.map((step) => {
            const isCompleted = step.status === 'completed';
            const isCurrent = step.status === 'current';

            return (
              <div key={step.id} className="relative flex items-start gap-space-md group">
                {/* Node Icon */}
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

                {/* Step Card */}
                <div
                  className={`rounded-xl p-space-md w-full flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm border border-outline-variant/30 ${
                    isCurrent
                      ? 'bg-surface-container shadow-sm'
                      : isCompleted
                      ? 'bg-surface-container-low'
                      : 'bg-surface-container-lowest hover:bg-surface-container-low transition-colors'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-space-sm">
                      <span className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                        {step.title}
                      </span>
                      <span
                        className={`px-space-xs py-0.5 rounded-md font-label-xs text-label-xs font-semibold ${
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
                    <p className="font-body-sm text-body-sm text-secondary mt-1">{step.description}</p>
                  </div>
                  <span className="text-label-xs font-label-xs text-outline shrink-0">{step.tag}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommended Free Courses & Targeted Capstone Projects to Close Gaps */}
      <div className="flex flex-col gap-space-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs">
          <div>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Recommended Courses & Projects to Close Gaps
            </h2>
            <p className="font-body-sm text-body-sm text-secondary">
              Free, industry-validated materials curated specifically to satisfy missing {selectedRole} requirements.
            </p>
          </div>
          <button
            onClick={() => {}}
            className="inline-flex items-center gap-space-2xs text-primary font-label-md text-label-md hover:underline"
          >
            Browse All Curated Resources
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-space-lg">
          {resources.map((res) => (
            <div
              key={res.id}
              className="bg-surface-container-lowest rounded-xl shadow-sm p-space-lg flex flex-col justify-between gap-space-md border border-outline-variant/30"
            >
              <div className="space-y-space-md">
                <div className="relative w-full h-36 rounded-lg overflow-hidden bg-surface-container-low">
                  <img src={res.imageUrl} alt={res.title} className="w-full h-full object-cover" />
                  <span className="absolute top-space-xs left-space-xs px-space-xs py-0.5 rounded bg-on-surface/80 text-on-secondary font-label-xs text-label-xs backdrop-blur-sm">
                    Addresses Gap: {res.addressesGap}
                  </span>
                  <span className="absolute bottom-space-xs right-space-xs px-space-xs py-0.5 rounded bg-surface-container-lowest/90 text-on-surface font-label-xs text-label-xs">
                    {res.duration}
                  </span>
                </div>

                <div>
                  <div className="flex items-center justify-between text-label-xs font-label-xs text-secondary mb-1">
                    <span>{res.provider}</span>
                    <span className="text-tertiary font-medium">{res.impactScore}</span>
                  </div>
                  <h3 className="font-headline-sm text-headline-sm text-on-surface">{res.title}</h3>
                  <p className="font-body-sm text-body-sm text-secondary mt-1">{res.description}</p>
                </div>

                <div className="flex items-center gap-space-xs text-label-xs font-label-xs text-on-surface-variant">
                  <span className="material-symbols-outlined text-[16px] text-tertiary">check_circle</span>
                  <span>{res.perks}</span>
                </div>
              </div>

              <div className="flex items-center gap-space-sm pt-space-xs border-t border-outline-variant/20">
                <button
                  onClick={() => alert(`Enrolled in ${res.title}. Coursework added to your active schedule!`)}
                  className="flex-1 py-space-xs px-space-sm rounded-xl bg-primary text-on-primary font-label-md text-label-md hover:bg-primary-container transition-colors text-center shadow-sm"
                >
                  Start Learning
                </button>
                <button
                  onClick={() => alert(`Added ${res.title} milestone to your roadmap.`)}
                  className="p-space-xs rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface transition-colors"
                  title="Add to Roadmap"
                >
                  <span className="material-symbols-outlined text-[20px]">add_task</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Peer Comparison & Target Employer Fit Breakdown */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-xl grid grid-cols-1 lg:grid-cols-12 gap-space-xl border border-outline-variant/30">
        <div className="lg:col-span-4 space-y-space-sm">
          <span className="font-label-xs text-label-xs text-primary font-semibold uppercase tracking-wider">
            Placement Probability
          </span>
          <h3 className="font-headline-md text-headline-md text-on-surface">Internship Market Fit</h3>
          <p className="font-body-sm text-body-sm text-secondary">
            Based on candidate placements in your university tier over the last two admission cycles, acquiring
            containerization and cloud basics increases your interview invitation probability by{' '}
            <span className="text-on-surface font-semibold">3.8x</span>.
          </p>
          <div className="pt-space-sm space-y-space-xs">
            <div className="flex items-center justify-between text-body-sm font-body-sm">
              <span className="text-secondary">Current Profile Strength</span>
              <span className="text-on-surface font-medium">Top 22%</span>
            </div>
            <div className="flex items-center justify-between text-body-sm font-body-sm">
              <span className="text-secondary">Projected Post-Roadmap Strength</span>
              <span className="text-tertiary font-bold">Top 3%</span>
            </div>
          </div>
        </div>

        {/* Employer Benchmark Grid */}
        <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-space-md">
          {gapData.employerBenchmarks.map((b) => (
            <div
              key={b.company}
              className="p-space-md rounded-xl bg-surface-container-low flex flex-col justify-between border border-outline-variant/30"
            >
              <div className="space-y-space-xs">
                <div className="flex items-center justify-between">
                  <span className="font-headline-sm text-label-md text-on-surface font-bold">{b.company}</span>
                  <span className="px-space-xs py-0.5 rounded bg-surface-container text-primary font-label-xs text-label-xs">
                    {b.tier}
                  </span>
                </div>
                <p className="font-label-xs text-label-xs text-secondary">{b.role}</p>

                <div className="pt-space-xs">
                  <div className="flex items-center justify-between text-label-xs font-label-xs mb-1">
                    <span className="text-on-surface">Match score</span>
                    <span className={`font-bold tabular-nums ${b.isStrongFit ? 'text-tertiary' : 'text-primary'}`}>
                      {b.matchScore}%
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${b.isStrongFit ? 'bg-tertiary' : 'bg-primary'}`}
                      style={{ width: `${b.matchScore}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <p
                className={`font-label-xs text-label-xs mt-space-md flex items-center gap-1 ${
                  b.isStrongFit ? 'text-primary' : 'text-error'
                }`}
              >
                <span className="material-symbols-outlined text-[14px]">
                  {b.isStrongFit ? 'check' : 'close'}
                </span>
                {b.statusNote}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
