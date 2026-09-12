import { apiFetch } from './apiClient';
import { Opportunity } from '../types';

export interface AdminDashboardStats {
  totalStudents: number;
  totalOpportunities: number;
  opportunitiesByCategory: Record<string, number>;
  verifiedOpportunities: number;
  pendingOpportunities: number;
  applicationCounts: number;
  applicationsByStatus: Record<string, number>;
  activeUsers: number;
  recentActivity: Array<{
    id: string;
    type: string;
    title: string;
    description: string;
    timestamp: string;
  }>;
  verificationRate: number;
  avgMatchFit: number;
}

export interface AdminStudentSummary {
  id: string;
  userId: string;
  name: string;
  email: string;
  university?: string;
  degree?: string;
  major?: string;
  gpa?: number;
  targetRole?: string;
  verifiedSkillsCount: number;
  profileStrength: number;
  verifiedProfilePercent: number;
  isActive: boolean;
  applicationsCount: number;
  status: string;
}

export interface AdminAnalyticsData {
  opportunityDistribution: Record<string, number>;
  modeDistribution: Record<string, number>;
  categoryPopularity: Array<{
    category: string;
    label: string;
    opportunitiesCount: number;
    applicationsCount: number;
    opportunityShare: number;
    applicationShare: number;
  }>;
  applicationsTotal: number;
  applicationsByStatus: Record<string, number>;
  applicationOutcomes: {
    acceptanceRate: number;
    interviewConversionRate: number;
    shortlistedRate: number;
    totalApplications: number;
  };
  studentSkillTrends: {
    topStudentSkills: Array<{ skill: string; studentCount: number }>;
    topDemandedSkills: Array<{ skill: string; demandCount: number }>;
    mostDemandedMissingSkill: string;
  };
  matchPrecision: {
    avgMatchFit: number;
    precisionIndex: number;
    highFitCohortShare: number;
  };
}

export const adminService = {
  getDashboard: async (): Promise<AdminDashboardStats> => {
    return apiFetch<AdminDashboardStats>('/admin/dashboard');
  },

  getOpportunities: async (params?: {
    verified?: boolean;
    category?: string;
    search?: string;
  }): Promise<Opportunity[]> => {
    const queryParts: string[] = [];
    if (params?.verified !== undefined) queryParts.push(`verified=${params.verified}`);
    if (params?.category) queryParts.push(`category=${encodeURIComponent(params.category)}`);
    if (params?.search) queryParts.push(`search=${encodeURIComponent(params.search)}`);
    const qs = queryParts.length ? `?${queryParts.join('&')}` : '';
    return apiFetch<Opportunity[]>(`/admin/opportunities${qs}`);
  },

  createOpportunity: async (opp: any): Promise<Opportunity> => {
    return apiFetch<Opportunity>('/admin/opportunities', {
      method: 'POST',
      body: JSON.stringify(opp),
    });
  },

  updateOpportunity: async (id: string, opp: any): Promise<Opportunity> => {
    return apiFetch<Opportunity>(`/admin/opportunities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(opp),
    });
  },

  deleteOpportunity: async (id: string): Promise<void> => {
    await apiFetch(`/admin/opportunities/${id}`, {
      method: 'DELETE',
    });
  },

  verifyOpportunity: async (id: string): Promise<Opportunity> => {
    return apiFetch<Opportunity>(`/admin/opportunities/${id}/verify`, {
      method: 'PATCH',
    });
  },

  rejectOpportunity: async (id: string, reason?: string): Promise<Opportunity> => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return apiFetch<Opportunity>(`/admin/opportunities/${id}/reject${qs}`, {
      method: 'PATCH',
    });
  },

  getStudents: async (params?: {
    search?: string;
    is_active?: boolean;
    target_role?: string;
  }): Promise<AdminStudentSummary[]> => {
    const queryParts: string[] = [];
    if (params?.search) queryParts.push(`search=${encodeURIComponent(params.search)}`);
    if (params?.is_active !== undefined) queryParts.push(`is_active=${params.is_active}`);
    if (params?.target_role) queryParts.push(`target_role=${encodeURIComponent(params.target_role)}`);
    const qs = queryParts.length ? `?${queryParts.join('&')}` : '';
    return apiFetch<AdminStudentSummary[]>(`/admin/students${qs}`);
  },

  getStudentDetail: async (id: string): Promise<any> => {
    return apiFetch<any>(`/admin/students/${id}`);
  },

  toggleStudentStatus: async (id: string, isActive: boolean): Promise<any> => {
    return apiFetch<any>(`/admin/students/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ isActive }),
    });
  },

  getAnalytics: async (): Promise<AdminAnalyticsData> => {
    return apiFetch<AdminAnalyticsData>('/admin/analytics');
  },
};
