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
        if (data.length > 0) return data;
      } else if (data && Array.isArray(data.items)) {
        return data.items;
      }
    } catch {
      // Fallback gracefully to mock data
    }
    return mockOpportunities;
  },

  async getOpportunityById(id: string): Promise<Opportunity | undefined> {
    try {
      const opp = await apiFetch<Opportunity>(`/opportunities/${id}`);
      if (opp && opp.id) {
        return opp;
      }
    } catch {
      // Fallback
    }
    return mockOpportunities.find((opp) => opp.id === id);
  },

  async getOpportunitiesByCategory(category: string): Promise<Opportunity[]> {
    try {
      const data = await apiFetch<PaginatedOpportunities | Opportunity[]>(
        `/opportunities?category=${encodeURIComponent(category)}&page_size=50`
      );
      const items = Array.isArray(data) ? data : data?.items;
      if (Array.isArray(items) && items.length > 0) {
        return items;
      }
    } catch {}

    // Fallback
    return mockOpportunities.filter(
      (opp) => opp.category.toLowerCase() === category.toLowerCase()
    );
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
        return items;
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
    return results;
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
