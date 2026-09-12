import { apiFetch } from './apiClient';

export interface AIChatSource {
  title: string;
  type: string;
  link?: string;
  detail?: string;
}

export interface AIChatResponse {
  reply: string;
  sources: AIChatSource[];
  recommendedActions: Array<{ label: string; link: string }>;
  timestamp?: string;
}

class AIAssistantService {
  async sendMessage(message: string, opportunityId?: string): Promise<AIChatResponse> {
    try {
      const data = await apiFetch<AIChatResponse>('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          message,
          opportunityId,
        }),
      });
      if (data && data.reply) {
        return data;
      }
    } catch (err: any) {
      console.warn('AI chat error:', err);
    }

    return {
      reply:
        "I'm temporarily unable to reach the SkillMatch AI Advisor service. Please check your network connection.",
      sources: [],
      recommendedActions: [],
    };
  }
}

export const aiAssistantService = new AIAssistantService();
