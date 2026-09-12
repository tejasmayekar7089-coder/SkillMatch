import React from 'react';
import { Link } from 'react-router-dom';

export const LandingPage: React.FC = () => {
  const categories = [
    { label: 'Internships', count: '42+ Active', icon: 'work', desc: 'Summer & semester technical placements' },
    { label: 'Hackathons', count: '18+ Open', icon: 'code_blocks', desc: 'Global coding challenges & prize tracks' },
    { label: 'Scholarships', count: '$120k+ Pool', icon: 'school', desc: 'Merit-based undergraduate tuition grants' },
    { label: 'Courses', count: '25+ Tracks', icon: 'menu_book', desc: 'Free industry-validated curriculums' },
    { label: 'Projects', count: '19+ Cohorts', icon: 'terminal', desc: 'Open-source collaborative team builds' },
    { label: 'Jobs', count: '34+ Roles', icon: 'business_center', desc: 'Graduate campus intake & early-career' },
    { label: 'Skill Opportunities', count: '15+ Programs', icon: 'bolt', desc: 'Sponsored cloud apprentice certificates' },
  ];

  return (
    <div className="min-h-screen bg-background text-on-surface">
      {/* Public Navbar */}
      <nav className="h-16 px-space-md lg:px-space-xl flex items-center justify-between border-b border-outline-variant/30 bg-surface-container-lowest sticky top-0 z-50">
        <Link to="/" className="flex items-center gap-space-sm">
          <img src="/assets/logo.svg" alt="SkillMatch Logo" className="h-8 w-auto" />
        </Link>

        <div className="flex items-center gap-space-sm">
          <Link
            to="/login"
            className="px-space-md py-1.5 rounded-xl text-secondary hover:text-on-surface font-label-md transition-colors"
          >
            Log In
          </Link>
          <Link
            to="/register"
            className="px-space-lg py-1.5 rounded-xl bg-primary text-on-primary hover:bg-primary-container font-label-md font-semibold transition-colors shadow-sm"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-space-3xl px-space-lg lg:px-space-xl max-w-6xl mx-auto text-center space-y-space-lg">
        <div className="inline-flex items-center gap-space-xs px-space-md py-1 rounded-full bg-surface-container text-primary font-label-sm font-semibold tracking-wide">
          <span className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
          Intelligent Student Opportunity Engine
        </div>

        <h1 className="font-display-lg text-[38px] md:text-[54px] md:leading-[1.15] text-on-surface font-bold tracking-tight max-w-4xl mx-auto">
          Match your verified skills with top-tier student opportunities.
        </h1>

        <p className="font-body-lg text-body-lg text-secondary max-w-2xl mx-auto">
          Discover internships, hackathons, scholarships, courses, projects, jobs, and apprentice tracks mapped
          precisely to your coursework, GPA, and GitHub repositories.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-space-sm pt-space-sm">
          <Link
            to="/onboarding"
            className="h-12 px-space-2xl rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md font-bold flex items-center gap-space-xs shadow-md transition-all"
          >
            <span>Run Student Diagnostic</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </Link>
          <Link
            to="/discover"
            className="h-12 px-space-xl rounded-xl bg-surface-container-lowest hover:bg-surface-container-low text-on-surface font-label-md font-semibold flex items-center gap-space-xs border border-outline-variant/40 shadow-sm transition-all"
          >
            <span>Explore Opportunities</span>
          </Link>
        </div>
      </section>

      {/* Category Grid Section */}
      <section className="py-space-2xl px-space-lg lg:px-space-xl max-w-6xl mx-auto">
        <div className="text-center space-y-space-2xs mb-space-xl">
          <h2 className="font-headline-lg text-on-surface font-bold">7 Pillars of Opportunity Discovery</h2>
          <p className="font-body-md text-secondary">
            Everything students need to launch an accelerated engineering and tech career.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md">
          {categories.map((c) => (
            <div
              key={c.label}
              className="p-space-lg rounded-2xl bg-surface-container-lowest border border-outline-variant/30 shadow-sm space-y-2 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between text-primary">
                <span className="material-symbols-outlined text-[28px]">{c.icon}</span>
                <span className="font-label-xs px-2 py-0.5 rounded bg-surface-container font-semibold">
                  {c.count}
                </span>
              </div>
              <h3 className="font-headline-sm text-on-surface font-bold">{c.label}</h3>
              <p className="font-body-sm text-secondary text-label-xs">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AI Explainability Feature Section */}
      <section className="py-space-2xl px-space-lg lg:px-space-xl max-w-5xl mx-auto bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-sm my-space-2xl p-space-xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl items-center">
          <div className="lg:col-span-6 space-y-space-md">
            <span className="font-label-xs uppercase tracking-wider text-primary font-bold">Explainable AI</span>
            <h2 className="font-headline-lg text-on-surface font-bold">
              Transparent match scores with actionable gap roadmaps.
            </h2>
            <p className="font-body-md text-secondary leading-relaxed">
              No black-box recommendations. See exactly how your skills, education, and projects contribute to your score,
              and receive personalized learning plans to close the remaining gaps.
            </p>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1 font-label-md text-primary font-bold hover:underline"
            >
              <span>Explore Student Dashboard</span>
              <span className="material-symbols-outlined text-[16px]">chevron_right</span>
            </Link>
          </div>

          <div className="lg:col-span-6 bg-surface-container-low p-space-lg rounded-2xl border border-outline-variant/30 space-y-space-sm">
            <div className="flex items-center justify-between">
              <span className="font-label-sm font-semibold text-on-surface">TechNova Machine Learning Intern</span>
              <span className="px-2 py-0.5 rounded-full bg-surface-container text-primary font-bold text-label-sm">
                94% Match
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-label-xs text-secondary">
                <span>Technical Skills Fit</span>
                <span className="text-tertiary font-bold">40/40 (100%)</span>
              </div>
              <div className="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
            <div className="p-space-sm bg-surface-container-lowest rounded-xl text-label-xs text-secondary">
              <span className="text-error font-semibold block">Missing: Docker Containerization (+6% Boost)</span>
              <span>Recommended: 3h Free Micro-Course</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-space-xl px-space-lg border-t border-outline-variant/30 text-center font-body-sm text-secondary">
        <p>© 2026 SkillMatch Platform. Engineered with precision for university students worldwide.</p>
      </footer>
    </div>
  );
};
