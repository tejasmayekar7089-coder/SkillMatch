import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Opportunity, StudentProfile } from '../../types';
import { opportunityService } from '../../services/opportunityService';
import { profileService } from '../../services/profileService';
import { authService } from '../../services/authService';
import { dashboardService, DashboardData } from '../../services/dashboardService';
import { ProfileStrengthBar } from '../../components/common/ProfileStrengthBar';
import { OpportunityCard } from '../../components/common/OpportunityCard';
import { Modal } from '../../components/common/Modal';

export const DashboardPage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [sortBy, setSortBy] = useState<'match' | 'deadline'>('match');
  const [isDiagnosticOpen, setIsDiagnosticOpen] = useState(false);
  const [diagnosticRunning, setDiagnosticRunning] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // 1. Fetch real student profile
    profileService.getProfile().then((p) => {
      if (p) setProfile(p);
    });

    // 2. Fetch real aggregated dashboard data
    dashboardService.getDashboard().then((data) => {
      if (data) {
        setDashboardData(data);
        if (data.recommendedOpportunities && data.recommendedOpportunities.length > 0) {
          setOpportunities(data.recommendedOpportunities.map((r) => r.opportunity));
        }
      }
    });

    // Fallback or full list fetch
    opportunityService.getAllOpportunities().then((data) => {
      setOpportunities((prev) => (prev.length > 0 ? prev : data));
    });
  }, []);

  const handleRunDiagnostic = async () => {
    setIsDiagnosticOpen(true);
    setDiagnosticRunning(true);
    setDiagnosticResult(null);
    const res = await profileService.runDiagnostic();
    setDiagnosticRunning(false);
    setDiagnosticResult(res);
  };

  const sortedOpportunities = [...opportunities].sort((a, b) => {
    if (sortBy === 'deadline') {
      return (a.deadlineDaysRemaining || 99) - (b.deadlineDaysRemaining || 99);
    }
    return b.matchScore - a.matchScore;
  });

  const catCounts = dashboardData?.categoryCounts || {};
  const categories = [
    { label: 'Internships', count: catCounts['internships'] ?? 24, icon: 'work', path: '/internships' },
    { label: 'Hackathons', count: catCounts['hackathons'] ?? 12, icon: 'code_blocks', path: '/hackathons' },
    { label: 'Scholarships', count: catCounts['scholarships'] ?? 8, icon: 'school', path: '/scholarships' },
    { label: 'Courses', count: catCounts['courses'] ?? 19, icon: 'menu_book', path: '/courses' },
    { label: 'Projects', count: catCounts['projects'] ?? 15, icon: 'terminal', path: '/projects' },
    { label: 'Jobs', count: catCounts['jobs'] ?? 31, icon: 'business_center', path: '/jobs' },
    { label: 'Skill Sets', count: catCounts['skill-opportunities'] ?? 10, icon: 'bolt', path: '/skill-opportunities' },
  ];

  const currentUser = authService.getCurrentUser();
  const rawName =
    profile?.name ||
    currentUser?.name ||
    (dashboardData?.studentName && dashboardData.studentName !== 'Alex' && dashboardData.studentName !== 'Alex Morgan' ? dashboardData.studentName : '') ||
    'Tony Stark';
  const studentName = rawName;
  const totalApps = dashboardData?.totalApplications ?? 5;
  const upcomingDeadlinesList = dashboardData?.upcomingDeadlines || [];
  const deadlinesCount = upcomingDeadlinesList.length > 0 ? upcomingDeadlinesList.length : 3;
  const newMatchesCount = dashboardData?.recommendedOpportunities?.length || 14;

  const targetRole =
    profile?.targetRole ||
    (dashboardData?.skillGaps?.targetRole && dashboardData.skillGaps.targetRole !== 'Machine Learning Engineer' ? dashboardData.skillGaps.targetRole : '') ||
    (profile?.major?.toLowerCase().includes('elec')
      ? 'Embedded Systems Engineer'
      : profile?.major?.toLowerCase().includes('mech')
      ? 'Mechanical Design Engineer'
      : profile?.major?.toLowerCase().includes('finan')
      ? 'Financial Analyst'
      : 'Embedded Systems Engineer');
  const readiness = dashboardData?.skillGaps?.readinessScore ?? 82;
  const criticalGaps = (dashboardData?.skillGaps?.criticalGaps && dashboardData.skillGaps.criticalGaps.length > 0)
    ? dashboardData.skillGaps.criticalGaps
    : (profile?.major?.toLowerCase().includes('elec')
        ? [
            { name: 'RTOS / Embedded C', level: 'Intermediate', priority: 'High', rolesDemandPercent: 92 },
            { name: 'ARM Cortex-M Firmware', level: 'Intermediate', priority: 'High', rolesDemandPercent: 88 },
          ]
        : []);

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header Block with Greeting and Dynamic Stats */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-space-md">
        <div className="space-y-space-2xs">
          <div className="flex items-center gap-space-xs text-secondary">
            <span className="font-label-xs uppercase tracking-wider text-outline">Student Portal</span>
            <span className="text-outline">/</span>
            <span className="font-label-xs font-semibold text-primary">{studentName}</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Good morning, {studentName.split(' ')[0]}</h1>
          <p className="font-body-md text-secondary">
            Here are opportunities selected for your profile based on your verified skills and academic track.
          </p>
        </div>

        {/* Status Ticker Badges */}
        <div className="flex flex-wrap items-center gap-space-sm">
          <Link
            to="/discover"
            className="flex items-center gap-space-xs px-space-md py-1.5 bg-surface-container-lowest shadow-sm rounded-xl hover:bg-surface-container-low transition-colors"
          >
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span className="font-label-sm text-secondary">{newMatchesCount} New Matches</span>
          </Link>
          <Link
            to="/discover?sort=deadline"
            className="flex items-center gap-space-xs px-space-md py-1.5 bg-surface-container-lowest shadow-sm rounded-xl hover:bg-surface-container-low transition-colors"
          >
            <span className="w-2 h-2 rounded-full bg-error"></span>
            <span className="font-label-sm text-secondary">{deadlinesCount} Approaching Deadlines</span>
          </Link>
          <Link
            to="/applications"
            className="flex items-center gap-space-xs px-space-md py-1.5 bg-surface-container-lowest shadow-sm rounded-xl hover:bg-surface-container-low transition-colors"
          >
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            <span className="font-label-sm text-secondary">{totalApps} Active Applications</span>
          </Link>
        </div>
      </div>

      {/* Top Banner: Profile Strength Card */}
      <ProfileStrengthBar onRunDiagnostic={handleRunDiagnostic} />

      {/* Category Shortcut Hub */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-space-sm">
        {categories.map((cat) => (
          <Link
            key={cat.label}
            to={cat.path}
            className="group p-space-md bg-surface-container-lowest hover:bg-surface-container-low transition-all rounded-xl shadow-sm flex flex-col justify-between h-24 border border-outline-variant/30"
          >
            <div className="flex items-center justify-between text-secondary group-hover:text-primary">
              <span className="material-symbols-outlined text-[20px]">{cat.icon}</span>
              <span className="font-label-xs px-1.5 py-0.5 rounded bg-surface-container-high text-primary font-semibold tabular-nums">
                {cat.count}
              </span>
            </div>
            <span className="font-label-sm text-on-surface font-medium">{cat.label}</span>
          </Link>
        ))}
      </div>

      {/* Primary Working Area: Matches Feed (8 Cols) + Side Diagnostic Panel (4 Cols) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-space-xl">
        {/* Feed Section (8 Cols) */}
        <div className="xl:col-span-8 space-y-space-base">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs pb-space-xs">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface">Top Matches For You</h2>
              <p className="font-body-sm text-secondary">
                Opportunities ranked based on your skills and preferences. Showing match breakdown.
              </p>
            </div>
            <div className="flex items-center gap-space-xs">
              <span className="font-label-xs text-outline uppercase tracking-wider">Sort:</span>
              <button
                onClick={() => setSortBy(sortBy === 'match' ? 'deadline' : 'match')}
                className="font-label-sm text-primary flex items-center gap-1 font-semibold hover:underline"
              >
                {sortBy === 'match' ? 'Match Score (High to Low)' : 'Nearest Deadline'}
                <span className="material-symbols-outlined text-[16px]">swap_vert</span>
              </button>
            </div>
          </div>

          {/* Opportunity Cards List */}
          {sortedOpportunities.slice(0, 4).map((opp) => (
            <OpportunityCard key={opp.id} opportunity={opp} variant="feed" />
          ))}

          <div className="pt-space-sm text-center">
            <Link
              to="/discover"
              className="inline-flex items-center justify-center gap-space-xs px-space-xl py-space-sm rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-label-md font-semibold transition-colors"
            >
              <span>Explore All Verified Opportunities</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </Link>
          </div>
        </div>

        {/* Side Diagnostic Widgets (4 Cols) */}
        <div className="xl:col-span-4 space-y-space-base">
          {/* Skill Gap Spotlight Widget */}
          <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-lg space-y-space-md border border-outline-variant/30">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Skill Gap Spotlight</h3>
              <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface font-label-xs font-semibold">
                Target Track
              </span>
            </div>

            {/* Target Track Readiness */}
            <div className="p-space-sm bg-surface-container-low rounded-xl space-y-space-xs">
              <div className="flex items-center justify-between">
                <span className="font-label-sm font-semibold text-on-surface">{targetRole}</span>
                <span className="font-label-sm text-primary font-bold">{readiness}% Ready</span>
              </div>
              <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                <div className="bg-primary h-full rounded-full" style={{ width: `${readiness}%` }}></div>
              </div>
            </div>

            {/* Missing Skills Breakdown */}
            <div className="space-y-space-sm">
              <span className="font-label-xs uppercase tracking-wider text-outline block">
                Missing High-Impact Skills
              </span>

              {criticalGaps.length > 0 ? (
                criticalGaps.slice(0, 2).map((gap) => (
                  <div key={gap.name} className="flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="material-symbols-outlined text-[18px] text-error shrink-0">cloud_off</span>
                      <div className="min-w-0">
                        <p className="font-label-sm font-medium text-on-surface truncate">{gap.name}</p>
                        <p className="font-label-xs text-secondary truncate">
                          {gap.rolesDemandPercent ? `Found in ${gap.rolesDemandPercent}% of target roles` : 'Critical requirement'}
                        </p>
                      </div>
                    </div>
                    <Link to="/skill-gap-analysis" className="font-label-xs text-primary hover:underline font-semibold shrink-0 ml-2">
                      Learn
                    </Link>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px] text-tertiary">check_circle</span>
                    <div>
                      <p className="font-label-sm font-medium text-on-surface">Core Competencies Met</p>
                      <p className="font-label-xs text-secondary">Verified profile satisfies target baseline</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <Link
              to="/career-roadmap"
              className="w-full py-2 rounded-xl bg-surface-container text-primary font-label-sm font-semibold text-center flex items-center justify-center gap-1 hover:bg-surface-container-high transition-colors"
            >
              <span>View Career Learning Path</span>
              <span className="material-symbols-outlined text-[16px]">chevron_right</span>
            </Link>
          </div>

          {/* Upcoming Deadlines Card */}
          <div className="bg-surface-container-lowest rounded-xl shadow-sm p-space-lg space-y-space-md border border-outline-variant/30">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Upcoming Deadlines</h3>
              <span className="material-symbols-outlined text-[18px] text-outline">alarm</span>
            </div>

            <div className="space-y-space-sm">
              {upcomingDeadlinesList.length > 0 ? (
                upcomingDeadlinesList.slice(0, 3).map((item) => (
                  <div key={item.id} className="flex items-start gap-space-sm p-space-sm rounded-xl bg-surface-container-low">
                    <div className="p-2 rounded-lg bg-error-container text-on-error-container flex flex-col items-center justify-center shrink-0 w-10">
                      <span className="font-label-xs font-bold leading-none">
                        {item.deadlineDaysRemaining !== undefined ? item.deadlineDaysRemaining : 5}
                      </span>
                      <span className="text-[9px] uppercase tracking-wider font-semibold">Days</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-label-sm font-semibold text-on-surface truncate">{item.title}</h4>
                      <p className="font-label-xs text-secondary truncate">{item.organization} • {item.deadline}</p>
                    </div>
                    <Link to={item.link} className="p-1 text-secondary hover:text-on-surface">
                      <span className="material-symbols-outlined text-[18px]">open_in_new</span>
                    </Link>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-secondary text-label-xs">
                  No approaching deadlines in your active pipeline.
                </div>
              )}
            </div>

            <div className="pt-space-xs text-center">
              <Link to="/applications" className="font-label-xs text-secondary hover:text-on-surface">
                View All Application Deadlines ({totalApps})
              </Link>
            </div>
          </div>

          {/* Quick AI Mentor Diagnostic Banner */}
          <div className="p-space-lg rounded-xl bg-surface-container-high space-y-space-sm">
            <div className="flex items-center gap-space-xs text-primary font-label-xs font-semibold uppercase tracking-wider">
              <span className="material-symbols-outlined text-[16px]">smart_toy</span>
              SkillMatch AI Assistant
            </div>
            <p className="font-body-sm text-on-surface">
              "Based on your profile and skills, you rank among the <strong>top candidates</strong> for high-affinity roles."
            </p>
            <Link
              to="/ai-assistant"
              className="font-label-sm text-primary font-semibold flex items-center gap-1 hover:underline"
            >
              Ask AI Advisor about interview prep & gaps
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Diagnostic Modal */}
      <Modal
        isOpen={isDiagnosticOpen}
        onClose={() => setIsDiagnosticOpen(false)}
        title="SkillMatch Profile Diagnostic"
      >
        {diagnosticRunning ? (
          <div className="py-space-xl flex flex-col items-center justify-center space-y-space-md">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="font-body-md text-secondary">Scanning verified credentials, GitHub repositories, and transcripts...</p>
          </div>
        ) : (
          <div className="space-y-space-md">
            <div className="p-space-md bg-surface-container-low rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="font-label-md text-on-surface font-semibold">Diagnostic Confidence</span>
                <span className="text-primary font-bold font-headline-sm">{diagnosticResult?.score}%</span>
              </div>
              <p className="font-body-sm text-secondary">{diagnosticResult?.recommendation}</p>
            </div>
            <div className="flex justify-end gap-space-sm pt-space-sm">
              <button
                onClick={() => setIsDiagnosticOpen(false)}
                className="px-space-md py-space-xs rounded-xl bg-surface-container-low font-label-md hover:bg-surface-container transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setIsDiagnosticOpen(false);
                  navigate('/skill-gap-analysis');
                }}
                className="px-space-lg py-space-xs rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors"
              >
                View Action Plan
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
