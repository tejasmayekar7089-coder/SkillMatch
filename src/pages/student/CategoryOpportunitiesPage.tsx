import React, { useState, useEffect } from 'react';
import { Opportunity, OpportunityCategory } from '../../types';
import { opportunityService } from '../../services/opportunityService';
import { OpportunityCard } from '../../components/common/OpportunityCard';

interface CategoryOpportunitiesPageProps {
  category: OpportunityCategory;
  title: string;
  subtitle: string;
  icon: string;
}

export const CategoryOpportunitiesPage: React.FC<CategoryOpportunitiesPageProps> = ({
  category,
  title,
  subtitle,
  icon,
}) => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    opportunityService.getOpportunitiesByCategory(category).then((data) => {
      setOpportunities(data);
      setLoading(false);
    });
  }, [category]);

  const filtered = opportunities.filter((o) =>
    searchQuery
      ? o.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        o.organization.toLowerCase().includes(searchQuery.toLowerCase()) ||
        o.matchedSkills.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase()))
      : true
  );

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
            <span className="material-symbols-outlined text-[16px]">{icon}</span>
            <span>Category Hub</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">{title}</h1>
          <p className="font-body-lg text-body-lg text-secondary max-w-2xl">{subtitle}</p>
        </div>

        {/* Search within category */}
        <div className="w-full md:w-72">
          <div className="relative flex items-center">
            <span className="material-symbols-outlined absolute left-space-sm text-outline text-[18px]">
              search
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search ${title.toLowerCase()}...`}
              className="w-full h-10 pl-9 pr-3 rounded-xl bg-surface-container-lowest border border-outline-variant/40 font-body-sm text-on-surface placeholder:text-outline focus:outline-none focus:border-primary"
            />
          </div>
        </div>
      </div>

      {/* Grid of Opportunities */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-surface-container-lowest rounded-2xl p-12 text-center border border-outline-variant/30">
          <span className="material-symbols-outlined text-[48px] text-outline mb-2">{icon}</span>
          <h3 className="font-headline-sm text-on-surface font-semibold">No {title.toLowerCase()} found</h3>
          <p className="font-body-sm text-secondary mt-1">Check back soon or explore our general Discover stream.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
          {filtered.map((opp) => (
            <OpportunityCard key={opp.id} opportunity={opp} variant="grid" />
          ))}
        </div>
      )}
    </div>
  );
};
