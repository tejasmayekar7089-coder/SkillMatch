import { API_BASE_URL, apiFetch, tokenStorage } from './apiClient';

export interface ResumeExtractedData {
  name?: string;
  email?: string;
  phone?: string;
  college?: string;
  degree?: string;
  branch?: string;
  academic_year?: string;
  graduation_year?: string;
  gpa?: number;
  summary?: string;
  skills: string[];
  projects: Array<{
    title: string;
    description: string;
    technologies: string[];
  }>;
  experience: Array<{
    role: string;
    organization: string;
    duration: string;
    description: string;
  }>;
  certifications: Array<{
    name: string;
    issuing_organization: string;
    issue_date: string;
  }>;
}

export interface ResumeUploadResponse {
  success: boolean;
  filename: string;
  extracted_data: ResumeExtractedData;
  raw_text_preview: string;
}

export interface ResumeConfirmRequest {
  name?: string;
  college?: string;
  degree?: string;
  branch?: string;
  academic_year?: string;
  graduation_year?: string;
  gpa?: number;
  summary?: string;
  experience?: string;
  skills?: string[];
  projects?: Array<{
    title: string;
    description: string;
    technologies: string[];
  }>;
  certifications?: Array<{
    name: string;
    issuing_organization: string;
    issue_date: string;
  }>;
}

export interface ResumeConfirmResponse {
  success: boolean;
  message: string;
  updated_fields: string[];
  skills_added: number;
  projects_added: number;
  certifications_added: number;
}

export const resumeService = {
  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const token = tokenStorage.get();
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/resume/upload`, {
      method: 'POST',
      body: formData,
      headers,
    });

    if (!response.ok) {
      let errorMsg = `Upload failed (${response.status})`;
      try {
        const errorJson = await response.json();
        errorMsg = errorJson.detail || errorJson.message || errorMsg;
      } catch {}
      throw new Error(errorMsg);
    }

    return response.json();
  },

  async confirmResume(data: ResumeConfirmRequest): Promise<ResumeConfirmResponse> {
    return apiFetch<ResumeConfirmResponse>('/resume/confirm', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
