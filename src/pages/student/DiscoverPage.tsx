import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Opportunity } from '../../types';
import { opportunityService } from '../../services/opportunityService';
import { OpportunityCard } from '../../components/common/OpportunityCard';

export const DiscoverPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get('category') || 'all';
  const initialQuery = searchParams.get('q') || '';

  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery);
  const [selectedDomain, setSelectedDomain] = useState<string>('Domain: All');
  const [selectedLocation, setSelectedLocation] = useState<string>('Location: Any');
  const [selectedMatchScore, setSelectedMatchScore] = useState<string>('Match: All Ratings');
  const [eligibleOnly, setEligibleOnly] = useState<boolean>(false);
  const [sortBy, setSortBy] = useState<'match-desc' | 'deadline-asc' | 'newest' | 'compensation'>('match-desc');
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    let minScore: number | undefined;
    if (selectedMatchScore.includes('90%')) minScore = 90;
    else if (selectedMatchScore.includes('80%')) minScore = 80;

    opportunityService
      .searchOpportunities({
        query: searchQuery,
        category: selectedCategory,
        domain: selectedDomain,
        location: selectedLocation,
        minMatchScore: minScore,
        eligibleOnly: eligibleOnly,
        sortBy: sortBy,
      })
      .then((data) => {
        setOpportunities(data);
        setLoading(false);
      });
  }, [selectedCategory, searchQuery, selectedDomain, selectedLocation, selectedMatchScore, eligibleOnly, sortBy]);

  const [categories, setCategories] = useState<Array<{ id: string; label: string; count: number }>>([
    { id: 'all', label: 'All Opportunities', count: 148 },
    { id: 'internships', label: 'Internships', count: 42 },
    { id: 'hackathons', label: 'Hackathons', count: 18 },
    { id: 'scholarships', label: 'Scholarships', count: 12 },
    { id: 'courses', label: 'Courses', count: 25 },
    { id: 'projects', label: 'Projects', count: 19 },
    { id: 'jobs', label: 'Jobs', count: 34 },
    { id: 'skill-opportunities', label: 'Skill Opportunities', count: 15 },
  ]);

  useEffect(() => {
    opportunityService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const handleCategorySelect = (id: string) => {
    setSelectedCategory(id);
    if (id === 'all') {
      searchParams.delete('category');
    } else {
      searchParams.set('category', id);
    }
    setSearchParams(searchParams);
  };

  return (
    <div className="flex flex-col w-full">
      {/* Hero / Header Block */}
      <section className="mb-space-2xl">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-lg">
          <div className="space-y-space-xs">
            <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs tracking-wider uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
              Tailored Stream Active
            </div>
            <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">
              Discover Opportunities
            </h1>
            <p className="font-body-lg text-body-lg text-secondary max-w-2xl">
              Explore curated internships, hackathons, scholarships, and projects matched to your verified
              credentials and skill benchmarks.
            </p>
          </div>

          {/* Quick Metrics Pill Bento */}
          <div className="flex items-center gap-space-sm bg-surface-container-lowest p-space-xs rounded-full shadow-sm border border-outline-variant/30">
            <div className="px-space-md py-1.5 rounded-full bg-surface-container-low flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-[16px] text-tertiary">check_circle</span>
              <span className="font-label-sm text-label-sm text-on-surface">148 Matches</span>
            </div>
            <div className="px-space-md py-1.5 rounded-full flex items-center gap-space-xs text-secondary">
              <span className="material-symbols-outlined text-[16px] text-primary">auto_graph</span>
              <span className="font-label-sm text-label-sm">
                Profile Fit: <strong className="text-on-surface font-semibold">94%</strong>
              </span>
            </div>
          </div>
        </div>

        {/* Search Input Command Box */}
        <div className="relative bg-surface-container-lowest rounded-2xl shadow-sm p-space-sm space-y-space-md border border-outline-variant/30">
          <div className="relative flex items-center">
            <span className="material-symbols-outlined absolute left-space-md text-outline text-[22px]">
              search
            </span>
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-12 pl-12 pr-28 rounded-xl bg-surface-container-low font-body-md text-body-md text-on-surface placeholder:text-outline focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 transition-all"
              placeholder="Search internships, hackathons, scholarships, courses, companies..."
              type="text"
            />
            <div className="absolute right-space-sm flex items-center gap-space-2xs">
              <kbd className="hidden sm:inline-flex items-center h-6 px-space-xs rounded bg-surface-container text-on-surface-variant font-label-xs text-[11px]">
                ⌘K
              </kbd>
              <button
                onClick={() => {}}
                className="h-9 px-space-md bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md rounded-lg flex items-center gap-space-xs transition-colors"
              >
                <span>Filter</span>
                <span className="material-symbols-outlined text-[18px]">tune</span>
              </button>
            </div>
          </div>

          {/* Category Filter Pills Bar (Horizontal Scroll) */}
          <div className="flex items-center gap-space-xs overflow-x-auto pb-space-2xs scrollbar-none" id="categoryPillList">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => handleCategorySelect(cat.id)}
                className={`px-space-md py-1.5 rounded-full font-label-sm text-label-sm whitespace-nowrap transition-colors ${
                  selectedCategory === cat.id
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'bg-surface-container-low hover:bg-surface-container text-on-surface-variant'
                }`}
              >
                {cat.label} {cat.id !== 'all' && `(${cat.count})`}
              </button>
            ))}
          </div>

          {/* Micro Filter Controls Dropdowns */}
          <div className="pt-space-xs flex flex-wrap items-center justify-between gap-space-sm border-t border-outline-variant/20">
            <div className="flex flex-wrap items-center gap-space-xs">
              {/* Domain */}
              <div className="relative">
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="appearance-none h-8 pl-space-sm pr-7 rounded-lg bg-surface-container-low hover:bg-surface-container font-label-sm text-label-sm text-on-surface focus:outline-none cursor-pointer"
                >
                  <option>Domain: All</option>
                  <option>AI / Machine Learning</option>
                  <option>Full-Stack Web</option>
                  <option>Cloud & DevOps</option>
                  <option>Computer Science</option>
                  <option>Mechanical Engineering</option>
                  <option>Electrical & Embedded</option>
                  <option>Finance & Economics</option>
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-1.5 top-2 text-[16px] text-secondary">
                  expand_more
                </span>
              </div>

              {/* Location */}
              <div className="relative">
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="appearance-none h-8 pl-space-sm pr-7 rounded-lg bg-surface-container-low hover:bg-surface-container font-label-sm text-label-sm text-on-surface focus:outline-none cursor-pointer"
                >
                  <option>Location: Any</option>
                  <option>Remote Only</option>
                  <option>Hybrid</option>
                  <option>On-site</option>
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-1.5 top-2 text-[16px] text-secondary">
                  expand_more
                </span>
              </div>

              {/* Match Score */}
              <div className="relative">
                <select
                  value={selectedMatchScore}
                  onChange={(e) => setSelectedMatchScore(e.target.value)}
                  className="appearance-none h-8 pl-space-sm pr-7 rounded-lg bg-surface-container-low hover:bg-surface-container font-label-sm text-label-sm text-on-surface focus:outline-none cursor-pointer"
                >
                  <option>Match: All Ratings</option>
                  <option>Match: 80%+ (High)</option>
                  <option>Match: 90%+ (Optimal)</option>
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-1.5 top-2 text-[16px] text-secondary">
                  expand_more
                </span>
              </div>

              {/* Eligibility Pill Toggle */}
              <label className="inline-flex items-center gap-1.5 px-space-sm h-8 rounded-lg bg-surface-container-low hover:bg-surface-container cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={eligibleOnly}
                  onChange={(e) => setEligibleOnly(e.target.checked)}
                  className="w-3.5 h-3.5 rounded accent-primary cursor-pointer"
                />
                <span className="font-label-sm text-label-sm text-on-surface font-medium flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px] text-tertiary">verified</span>
                  Eligible Only
                </span>
              </label>
            </div>

            {/* Sort by */}
            <div className="flex items-center gap-space-xs text-secondary font-label-sm text-label-sm">
              <span className="font-normal">Sort:</span>
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="appearance-none h-8 pl-2 pr-6 rounded-lg bg-surface-container-lowest font-label-sm text-label-sm font-semibold text-primary focus:outline-none cursor-pointer"
                >
                  <option value="match-desc">Best Match (Default)</option>
                  <option value="deadline-asc">Nearest Deadline</option>
                  <option value="newest">Newest Added</option>
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-1 top-2 text-[16px] text-primary">
                  expand_more
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Opportunity Grid (3-column utilitarian bento flow) */}
      <section className="mb-space-3xl">
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center">
            <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="font-body-sm text-secondary mt-3">Loading matched opportunities...</p>
          </div>
        ) : opportunities.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-12 text-center border border-outline-variant/30">
            <span className="material-symbols-outlined text-[48px] text-outline mb-2">filter_alt_off</span>
            <h3 className="font-headline-sm text-on-surface font-semibold">No matching opportunities found</h3>
            <p className="font-body-sm text-secondary mt-1">Try relaxing your search terms or filters.</p>
            <button
              onClick={() => {
                setSelectedCategory('all');
                setSearchQuery('');
                setSelectedDomain('Domain: All');
                setSelectedLocation('Location: Any');
                setSelectedMatchScore('Match: All Ratings');
                setEligibleOnly(false);
              }}
              className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-xl font-label-sm font-medium"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
            {opportunities.map((opp) => (
              <OpportunityCard key={opp.id} opportunity={opp} variant="grid" />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
