import { Application } from '../types';
import { apiFetch, tokenStorage } from './apiClient';
import { mockApplications, mockNotifications } from './mockData';

export interface NotificationItem {
  id: string;
  userId?: string;
  title: string;
  description: string;
  type: string;
  read: boolean;
  link?: string;
  timeAgo: string;
  createdAt?: string;
}

export function getStatusBadgeColor(status: string): string {
  switch (status?.toUpperCase()) {
    case 'DOING':
    case 'IN PROGRESS':
      return 'bg-blue-50 text-blue-700 border border-blue-200';
    case 'PENDING':
      return 'bg-amber-50 text-amber-700 border border-amber-200';
    case 'COMPLETED':
    case 'DONE':
      return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    case 'NOT_COMPLETED':
    case 'NOT COMPLETED':
    case 'DROPPED':
      return 'bg-rose-50 text-rose-700 border border-rose-200';
    case 'ISSUED':
    case 'CERTIFIED':
      return 'bg-purple-50 text-purple-700 border border-purple-200';
    case 'SAVED':
      return 'bg-surface-container text-secondary';
    case 'PLANNING':
      return 'bg-surface-container-high text-primary';
    case 'APPLIED':
      return 'bg-surface-container text-on-surface-variant';
    case 'SHORTLISTED':
      return 'bg-surface-container-high text-primary';
    case 'INTERVIEW':
    case 'INTERVIEWING':
      return 'bg-tertiary text-on-tertiary';
    case 'SELECTED':
    case 'OFFERED':
      return 'bg-tertiary-fixed text-on-tertiary-fixed';
    case 'REJECTED':
      return 'bg-error-container text-on-error-container';
    default:
      return 'bg-surface-container-low text-secondary';
  }
}

class ApplicationService {
  async getApplications(): Promise<Application[]> {
    if (!tokenStorage.get()) {
      return mockApplications;
    }
    try {
      const data = await apiFetch<any[]>('/applications');
      if (Array.isArray(data)) {
        return data.map((item) => ({
          id: item.id,
          opportunityId: item.opportunityId,
          opportunityTitle: item.opportunityTitle || 'Opportunity',
          organization: item.organization || 'Organization',
          category: item.category || 'internships',
          appliedDate: item.appliedDate || 'Recently',
          status: item.status,
          statusColor: getStatusBadgeColor(item.status),
          currentStage: item.currentStage || 'Application Submitted',
          nextDeadline: item.nextDeadline || 'Pending review',
          matchScore: item.matchScore || 90,
          notes: item.notes,
          statusHistory: item.statusHistory || [],
        }));
      }
    } catch {
      // Graceful fallback to mock data for offline/mock dev
    }
    return mockApplications;
  }

  async getApplicationById(id: string): Promise<Application | null> {
    try {
      const item = await apiFetch<any>(`/applications/${id}`);
      if (item && item.id) {
        return {
          id: item.id,
          opportunityId: item.opportunityId,
          opportunityTitle: item.opportunityTitle || 'Opportunity',
          organization: item.organization || 'Organization',
          category: item.category || 'internships',
          appliedDate: item.appliedDate || 'Recently',
          status: item.status,
          statusColor: getStatusBadgeColor(item.status),
          currentStage: item.currentStage || 'Application Submitted',
          nextDeadline: item.nextDeadline || 'Pending review',
          matchScore: item.matchScore || 90,
          notes: item.notes,
          statusHistory: item.statusHistory || [],
        };
      }
    } catch {}
    return mockApplications.find((a) => a.id === id) || null;
  }

  async submitApplication(
    opportunityId: string,
    opportunityTitle: string,
    organization: string,
    category: any,
    notes?: string,
    status: string = 'APPLIED'
  ): Promise<Application> {
    try {
      const data = await apiFetch<any>('/applications', {
        method: 'POST',
        body: JSON.stringify({
          opportunityId,
          status,
          appliedDate: new Date().toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          }),
          currentStage: 'Application Submitted & Profile Queued for Verification',
          notes: notes || '',
        }),
      });

      return {
        id: data.id,
        opportunityId: data.opportunityId,
        opportunityTitle: data.opportunityTitle || opportunityTitle,
        organization: data.organization || organization,
        category: data.category || category,
        appliedDate: data.appliedDate || 'Just now',
        status: data.status,
        statusColor: getStatusBadgeColor(data.status),
        currentStage: data.currentStage,
        nextDeadline: data.nextDeadline || 'Expected update within 5 business days',
        matchScore: data.matchScore || 94,
        notes: data.notes,
        statusHistory: data.statusHistory || [],
      };
    } catch {
      // Local fallback
      const fallbackApp: Application = {
        id: `app-${Date.now()}`,
        opportunityId,
        opportunityTitle,
        organization,
        category,
        appliedDate: 'Just now',
        status: 'APPLIED',
        statusColor: getStatusBadgeColor('APPLIED'),
        currentStage: 'Application Submitted & Profile Queued for Verification',
        nextDeadline: 'Expected update within 5 business days',
        matchScore: 94,
        notes,
      };
      return fallbackApp;
    }
  }

  async updateApplicationStatus(
    id: string,
    newStatus: string,
    stage?: string,
    notes?: string
  ): Promise<Application | null> {
    try {
      const data = await apiFetch<any>(`/applications/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
          status: newStatus,
          currentStage: stage,
          notes,
        }),
      });
      return {
        id: data.id,
        opportunityId: data.opportunityId,
        opportunityTitle: data.opportunityTitle,
        organization: data.organization,
        category: data.category,
        appliedDate: data.appliedDate,
        status: data.status,
        statusColor: getStatusBadgeColor(data.status),
        currentStage: data.currentStage,
        nextDeadline: data.nextDeadline,
        matchScore: data.matchScore,
        notes: data.notes,
        statusHistory: data.statusHistory || [],
      };
    } catch {
      return null;
    }
  }

  async trackOpportunityStatus(
    opportunityId: string,
    status: string,
    notes?: string,
    stage?: string
  ): Promise<Application> {
    try {
      const data = await apiFetch<any>('/applications/track', {
        method: 'POST',
        body: JSON.stringify({
          opportunityId,
          status,
          notes,
          stage,
        }),
      });
      return {
        id: data.id,
        opportunityId: data.opportunityId,
        opportunityTitle: data.opportunityTitle || 'Opportunity',
        organization: data.organization || 'Organization',
        category: data.category || 'internships',
        appliedDate: data.appliedDate || 'Today',
        status: data.status,
        statusColor: getStatusBadgeColor(data.status),
        currentStage: data.currentStage || `Marked as ${status}`,
        nextDeadline: data.nextDeadline || 'Active tracking',
        matchScore: data.matchScore || 90,
        notes: data.notes,
        statusHistory: data.statusHistory || [],
      };
    } catch {
      const fallbackApp: Application = {
        id: `app-${opportunityId}-${Date.now()}`,
        opportunityId,
        opportunityTitle: 'Opportunity',
        organization: 'Organization',
        category: 'internships',
        appliedDate: 'Today',
        status: status as any,
        statusColor: getStatusBadgeColor(status),
        currentStage: stage || `Marked as ${status}`,
        matchScore: 90,
        notes,
      };
      return fallbackApp;
    }
  }

  async deleteApplication(id: string): Promise<void> {
    await apiFetch(`/applications/${id}`, {
      method: 'DELETE',
    });
  }

  async getNotifications(): Promise<NotificationItem[]> {
    if (!tokenStorage.get()) {
      return [];
    }
    try {
      const data = await apiFetch<NotificationItem[]>('/notifications');
      if (Array.isArray(data)) {
        return data;
      }
    } catch {
      // Fallback
    }
    return mockNotifications;
  }

  async markNotificationRead(id: string): Promise<void> {
    try {
      await apiFetch(`/notifications/${id}/read`, {
        method: 'PUT',
      });
    } catch {
      // Fallback
    }
  }

  async markAllNotificationsRead(): Promise<void> {
    try {
      await apiFetch('/notifications/read-all', {
        method: 'PUT',
      });
    } catch {
      // Fallback
    }
  }
}

export const applicationService = new ApplicationService();
