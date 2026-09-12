import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Opportunity } from '../../types';
import { opportunityService } from '../../services/opportunityService';
import { OpportunityCard } from '../../components/common/OpportunityCard';

export const SavedOpportunitiesPage: React.FC = () => {
  const [savedOpportunities, setSavedOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSaved = () => {
    setLoading(true);
    opportunityService.getSavedOpportunities().then((data) => {
      setSavedOpportunities(data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadSaved();
  }, []);

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-base pb-space-xs">
        <div className="space-y-space-2xs">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
            <span className="material-symbols-outlined text-[16px]">bookmark</span>
            <span>Saved & Bookmarked</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Saved Opportunities</h1>
          <p className="font-body-lg text-body-lg text-secondary max-w-2xl">
            Keep track of high-confidence matches and upcoming deadlines you have bookmarked for future review.
          </p>
        </div>

        <Link
          to="/discover"
          className="inline-flex items-center gap-space-xs px-space-lg py-space-sm rounded-xl bg-primary text-on-primary font-label-md hover:bg-primary-container transition-colors shadow-sm"
        >
          <span>Find More Matches</span>
          <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
        </Link>
      </div>

      {/* Grid of Saved */}
      {loading ? (
        <div className="py-20 flex justify-center">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : savedOpportunities.length === 0 ? (
        <div className="bg-surface-container-lowest rounded-2xl p-16 text-center border border-outline-variant/30">
          <span className="material-symbols-outlined text-[48px] text-outline mb-2">bookmark_border</span>
          <h3 className="font-headline-sm text-on-surface font-semibold">No saved opportunities yet</h3>
          <p className="font-body-sm text-secondary mt-1 max-w-md mx-auto">
            Click the bookmark icon on any opportunity card in your dashboard or discover feed to save it here.
          </p>
          <Link
            to="/discover"
            className="mt-4 inline-block px-space-lg py-space-xs bg-primary text-on-primary rounded-xl font-label-md"
          >
            Explore Opportunities
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
          {savedOpportunities.map((opp) => (
            <OpportunityCard
              key={opp.id}
              opportunity={opp}
              variant="grid"
              onBookmarkChange={loadSaved}
            />
          ))}
        </div>
      )}
    </div>
  );
};
