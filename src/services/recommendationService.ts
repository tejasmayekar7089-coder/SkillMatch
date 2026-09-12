import {
  TargetRoleGapData,
  RoadmapStep,
  GapClosingResource,
  Opportunity,
} from '../types';
import { apiFetch } from './apiClient';
import {
  mockTargetRoleData,
  mockRoadmapSteps,
  mockGapClosingResources,
  mockOpportunities,
} from './mockData';

class RecommendationService {
  async getTargetRoleGaps(roleTitle?: string): Promise<TargetRoleGapData> {
    try {
      const qs = roleTitle ? `?role=${encodeURIComponent(roleTitle)}` : '';
      const data = await apiFetch<TargetRoleGapData>(`/skill-gap${qs}`);
      if (data && data.roleTitle) {
        return data;
      }
    } catch {
      // Fallback
    }
    if (roleTitle && roleTitle !== mockTargetRoleData.roleTitle) {
      return {
        ...mockTargetRoleData,
        roleTitle,
        readinessScore: roleTitle === 'Data Scientist' ? 84 : roleTitle === 'Full-Stack Developer' ? 71 : 68,
      };
    }
    return { ...mockTargetRoleData };
  }

  async getRoadmap(roleTitle?: string): Promise<RoadmapStep[]> {
    try {
      const qs = roleTitle ? `?role=${encodeURIComponent(roleTitle)}` : '';
      const data = await apiFetch<RoadmapStep[]>(`/career-roadmap${qs}`);
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    } catch {
      // Fallback
    }
    return [...mockRoadmapSteps];
  }

  async getGapClosingResources(roleTitle?: string): Promise<GapClosingResource[]> {
    try {
      const qs = roleTitle ? `?role=${encodeURIComponent(roleTitle)}` : '';
      const data = await apiFetch<GapClosingResource[]>(`/skill-gap/learning${qs}`);
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    } catch {
      // Fallback
    }
    return [...mockGapClosingResources];
  }

  async getRecommendedOpportunities(): Promise<Opportunity[]> {
    try {
      const data = await apiFetch<Opportunity[]>('/recommendations');
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    } catch {
      // Fallback
    }
    return mockOpportunities;
  }
}

export const recommendationService = new RecommendationService();
