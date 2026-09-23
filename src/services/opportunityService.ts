import { Opportunity } from '../types';
import { apiFetch } from './apiClient';
import { mockOpportunities } from './mockData';

export interface SearchParams {
  query?: string;
  q?: string;
  category?: string;
  domain?: string;
  location?: string;
  work_mode?: string;
  workMode?: string;
  skills?: string;
  minMatchScore?: number;
  eligibleOnly?: boolean;
  sortBy?: 'match-desc' | 'deadline-asc' | 'newest' | 'compensation';
  page?: number;
  pageSize?: number;
}

export interface PaginatedOpportunities {
  items: Opportunity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const SAVED_STORAGE_KEY = 'skillmatch_saved_opps';

function getStoredSavedIds(): Set<string> {
  try {
    const raw = localStorage.getItem(SAVED_STORAGE_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveStoredSavedIds(ids: Set<string>): void {
  try {
    localStorage.setItem(SAVED_STORAGE_KEY, JSON.stringify(Array.from(ids)));
  } catch {}
}

function normalizeOpportunity(opp: any): Opportunity {
  if (!opp) return opp;
  const reqs = opp.requirements || {};
  const technicalSkills = Array.isArray(reqs.technicalSkills) && reqs.technicalSkills.length > 0
    ? reqs.technicalSkills
    : (opp.requiredSkills || opp.required_skills || []).map((s: string) => ({
        name: s,
        level: 'Intermediate',
        matched: Array.isArray(opp.matchedSkills) && opp.matchedSkills.includes(s),
      }));

  const academicCriteria = Array.isArray(reqs.academicCriteria) && reqs.academicCriteria.length > 0
    ? reqs.academicCriteria
    : [
        opp.eligibilityRequirements || opp.eligibility_requirements,
        ...(Array.isArray(opp.degreeRequirements) ? opp.degreeRequirements : Array.isArray(opp.degree_requirements) ? opp.degree_requirements : []).map((d: string) => `Degree: ${d}`),
        ...(Array.isArray(opp.branchRequirements) ? opp.branchRequirements : Array.isArray(opp.branch_requirements) ? opp.branch_requirements : []).map((b: string) => `Branch: ${b}`),
        ...(Array.isArray(opp.academicYearRequirements) ? opp.academicYearRequirements : Array.isArray(opp.academic_year_requirements) ? opp.academic_year_requirements : []).map((y: string) => `Year: ${y}`),
      ].filter(Boolean);

  return {
    ...opp,
    keyResponsibilities: Array.isArray(opp.keyResponsibilities)
      ? opp.keyResponsibilities
      : Array.isArray(opp.key_responsibilities)
      ? opp.key_responsibilities
      : [],
    requirements: {
      technicalSkills,
      academicCriteria,
      experienceCriteria: reqs.experienceCriteria || [],
    },
    stages: Array.isArray(opp.stages) ? opp.stages : [],
    matchedSkills: Array.isArray(opp.matchedSkills) ? opp.matchedSkills : Array.isArray(opp.matched_skills) ? opp.matched_skills : [],
    missingSkills: Array.isArray(opp.missingSkills) ? opp.missingSkills : Array.isArray(opp.missing_skills) ? opp.missing_skills : [],
    requiredSkills: Array.isArray(opp.requiredSkills) ? opp.requiredSkills : Array.isArray(opp.required_skills) ? opp.required_skills : [],
  };
}

export const opportunityService = {
  async getAllOpportunities(params?: SearchParams): Promise<Opportunity[]> {
    try {
      const query = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            query.append(key, String(value));
          }
        });
      }
      const qs = query.toString() ? `?${query.toString()}` : '';
      const data = await apiFetch<PaginatedOpportunities | Opportunity[]>(`/opportunities${qs}`);
      if (Array.isArray(data)) {
        if (data.length > 0) return data.map(normalizeOpportunity);
      } else if (data && Array.isArray(data.items)) {
        return data.items.map(normalizeOpportunity);
      }
    } catch {
      // Fallback gracefully to mock data
    }
    return mockOpportunities.map(normalizeOpportunity);
  },

  async getOpportunityById(id: string): Promise<Opportunity | undefined> {
    try {
      const opp = await apiFetch<Opportunity>(`/opportunities/${id}`);
      if (opp && opp.id) {
        return normalizeOpportunity(opp);
      }
    } catch {
      // Fallback
    }
    const found = mockOpportunities.find((opp) => opp.id === id);
    return found ? normalizeOpportunity(found) : undefined;
  },

  async getOpportunitiesByCategory(category: string): Promise<Opportunity[]> {
    try {
      const data = await apiFetch<PaginatedOpportunities | Opportunity[]>(
        `/opportunities?category=${encodeURIComponent(category)}&page_size=50`
      );
      const items = Array.isArray(data) ? data : data?.items;
      if (Array.isArray(items) && items.length > 0) {
        return items.map(normalizeOpportunity);
      }
    } catch {}

    // Fallback
    return mockOpportunities
      .filter((opp) => opp.category.toLowerCase() === category.toLowerCase())
      .map(normalizeOpportunity);
  },

  async getCategories(): Promise<Array<{ id: string; label: string; count: number }>> {
    try {
      const data = await apiFetch<Array<{ id: string; label: string; count: number }>>('/opportunities/categories');
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    } catch {}
    return [
      { id: 'all', label: 'All Opportunities', count: 148 },
      { id: 'internships', label: 'Internships', count: 42 },
      { id: 'hackathons', label: 'Hackathons', count: 18 },
      { id: 'scholarships', label: 'Scholarships', count: 12 },
      { id: 'courses', label: 'Courses', count: 25 },
      { id: 'projects', label: 'Projects', count: 19 },
      { id: 'jobs', label: 'Jobs', count: 34 },
      { id: 'skill-opportunities', label: 'Skill Opportunities', count: 15 },
    ];
  },

  async searchOpportunities(params: SearchParams): Promise<Opportunity[]> {
    try {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          // Normalize query param name
          const mappedKey = key === 'query' ? 'q' : key;
          query.append(mappedKey, String(value));
        }
      });
      // Request adequate page size for browse streams
      if (!query.has('page_size')) {
        query.append('page_size', '50');
      }
      const data = await apiFetch<PaginatedOpportunities | Opportunity[]>(
        `/opportunities?${query.toString()}`
      );
      const items = Array.isArray(data) ? data : data?.items;
      if (Array.isArray(items)) {
        return items.map(normalizeOpportunity);
      }
    } catch {}

    // Fallback filtering if backend unreachable
    let results = mockOpportunities.slice();
    if (params.category && params.category !== 'all') {
      results = results.filter(
        (o) => o.category.toLowerCase() === params.category!.toLowerCase()
      );
    }
    const q = (params.query || params.q || '').toLowerCase();
    if (q) {
      results = results.filter(
        (o) =>
          o.title.toLowerCase().includes(q) ||
          o.organization.toLowerCase().includes(q) ||
          (o.matchedSkills && o.matchedSkills.some((s) => s.toLowerCase().includes(q)))
      );
    }
    return results.map(normalizeOpportunity);
  },

  // Admin Operations
  async createOpportunity(oppData: any): Promise<Opportunity> {
    return apiFetch<Opportunity>('/opportunities', {
      method: 'POST',
      body: JSON.stringify(oppData),
    });
  },

  async updateOpportunity(id: string, oppData: any): Promise<Opportunity> {
    return apiFetch<Opportunity>(`/opportunities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(oppData),
    });
  },

  async deleteOpportunity(id: string): Promise<void> {
    await apiFetch(`/opportunities/${id}`, {
      method: 'DELETE',
    });
  },

  async verifyOpportunity(id: string): Promise<Opportunity> {
    return apiFetch<Opportunity>(`/opportunities/${id}/verify`, {
      method: 'PATCH',
    });
  },

  async rejectOpportunity(id: string, reason?: string): Promise<Opportunity> {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return apiFetch<Opportunity>(`/opportunities/${id}/reject${qs}`, {
      method: 'PATCH',
    });
  },

  // Saved Opportunities Helpers
  isSaved(id: string): boolean {
    return getStoredSavedIds().has(id);
  },

  toggleSave(id: string): boolean {
    const saved = getStoredSavedIds();
    let newStatus = false;
    if (saved.has(id)) {
      saved.delete(id);
      newStatus = false;
      apiFetch(`/saved/${id}`, { method: 'DELETE' }).catch(() => {});
    } else {
      saved.add(id);
      newStatus = true;
      apiFetch(`/saved/${id}`, { method: 'POST' }).catch(() => {});
    }
    saveStoredSavedIds(saved);
    return newStatus;
  },

  async saveOpportunity(id: string): Promise<void> {
    const saved = getStoredSavedIds();
    saved.add(id);
    saveStoredSavedIds(saved);
    await apiFetch(`/saved/${id}`, { method: 'POST' });
  },

  async unsaveOpportunity(id: string): Promise<void> {
    const saved = getStoredSavedIds();
    saved.delete(id);
    saveStoredSavedIds(saved);
    await apiFetch(`/saved/${id}`, { method: 'DELETE' });
  },

  async getSavedOpportunities(): Promise<Opportunity[]> {
    try {
      const data = await apiFetch<Opportunity[]>('/saved');
      if (Array.isArray(data)) {
        const remoteIds = new Set(data.map((o) => o.id));
        saveStoredSavedIds(remoteIds);
        return data;
      }
    } catch {}

    const savedIds = getStoredSavedIds();
    const all = await this.getAllOpportunities();
    return all.filter((opp) => savedIds.has(opp.id));
  },

  // AIML Match & Skill Gap APIs
  async getOpportunityMatch(id: string): Promise<any> {
    return apiFetch<any>(`/opportunities/${id}/match`);
  },

  async getOpportunityMatchExplanation(id: string): Promise<any> {
    return apiFetch<any>(`/opportunities/${id}/match-explanation`);
  },

  async getOpportunitySkillGap(id: string): Promise<any> {
    return apiFetch<any>(`/skill-gap/${id}`);
  },

  async getOpportunityLearning(id: string): Promise<any> {
    return apiFetch<any>(`/skill-gap/${id}/learning`);
  },
};
