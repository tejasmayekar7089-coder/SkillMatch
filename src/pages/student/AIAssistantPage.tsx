import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { aiAssistantService, AIChatSource } from '../../services/aiAssistantService';
import { profileService as studentProfileService } from '../../services/profileService';
import { StudentProfile } from '../../types';

interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  time: string;
  sources?: AIChatSource[];
  recommendedActions?: Array<{ label: string; link: string }>;
  suggestedFollowups?: string[];
}

const CATEGORY_MODES = [
  { label: '🎯 Top Matches', prompt: 'Which opportunities match my profile?' },
  { label: '💼 Interview Prep', prompt: 'Give me an interview preparation guide for my top matching role.' },
  { label: '📝 Cover Letter Pitch', prompt: 'Draft a tailored cover letter pitch for my top internship.' },
  { label: '🚀 4-Week Roadmap', prompt: 'Create a detailed 4-week learning roadmap for my skill gaps.' },
  { label: '⚡ Skill Gap Diagnostic', prompt: 'What skills am I missing for my target role?' },
  { label: '📋 Application Pipeline', prompt: 'Show me my active applications and task status.' },
  { label: '📈 Boost Match Score', prompt: 'How can I improve my match score to 95%?' },
];

export const AIAssistantPage: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-1',
      sender: 'ai',
      text: "👋 Hello! I am your **SkillMatch AI Career Advisor**.\n\nI have real-time access to your verified student record, academic GPA, skill vectors, and official university platform listings.\n\nHow can I accelerate your career readiness today?",
      time: 'Just now',
      suggestedFollowups: [
        'Which opportunities match my profile?',
        'Give me an interview preparation plan',
        'Draft an elevator pitch for applications',
      ],
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    studentProfileService.getProfile().then((p) => {
      if (p) setProfile(p);
    });
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (e: React.FormEvent | null, customText?: string) => {
    if (e) e.preventDefault();
    const query = (customText || inputText).trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const response = await aiAssistantService.sendMessage(query);
      
      // Compute contextual dynamic follow-ups
      let followups: string[] = [];
      const qLower = query.toLowerCase();
      if (qLower.includes('match') || qLower.includes('opportunity')) {
        followups = ['What skills am I missing?', 'Give me an interview prep plan for this', 'Draft a cover letter pitch'];
      } else if (qLower.includes('interview') || qLower.includes('question')) {
        followups = ['Draft an application pitch', 'Create a 4-week roadmap to prepare', 'Show related internships'];
      } else if (qLower.includes('skill') || qLower.includes('gap') || qLower.includes('learn')) {
        followups = ['Create a 4-week study plan', 'Which courses should I take?', 'Show opportunities matching my current skills'];
      } else {
        followups = ['Which opportunities match my profile?', 'What should I learn next?', 'How to increase my match score?'];
      }

      const aiMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'ai',
        text: response.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: response.sources,
        recommendedActions: response.recommendedActions,
        suggestedFollowups: followups,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'ai',
        text: "I'm having trouble connecting to the advisory service. Please verify the backend service is running and try again.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (text: string, id: string) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2500);
    }
  };

  // Simple clean markdown text formatter
  const renderFormattedText = (content: string) => {
    return content.split('\n').map((line, idx) => {
      // Header 3
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="font-headline-sm text-base font-bold text-on-surface mt-3 mb-1">{line.replace('### ', '')}</h3>;
      }
      // Header 4
      if (line.startsWith('#### ')) {
        return <h4 key={idx} className="font-label-md text-sm font-semibold text-primary mt-2 mb-1">{line.replace('#### ', '')}</h4>;
      }
      // Horizontal rule
      if (line.trim() === '---') {
        return <hr key={idx} className="my-3 border-outline-variant/30" />;
      }
      // Bullet points
      if (line.startsWith('• ') || line.startsWith('- ')) {
        const text = line.substring(2);
        return (
          <div key={idx} className="flex items-start gap-1.5 ml-1 my-0.5">
            <span className="text-primary text-[15px]">•</span>
            <span className="flex-1">{formatInline(text)}</span>
          </div>
        );
      }
      // Numbered list
      if (/^\d+\.\s/.test(line)) {
        return <div key={idx} className="ml-1 my-0.5">{formatInline(line)}</div>;
      }
      // Empty line
      if (!line.trim()) {
        return <div key={idx} className="h-1.5" />;
      }
      return <p key={idx} className="my-0.5">{formatInline(line)}</p>;
    });
  };

  const formatInline = (str: string) => {
    // Bold matching
    const parts = str.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-on-surface">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={i} className="italic text-on-surface-variant">{part.slice(1, -1)}</em>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="px-1.5 py-0.5 rounded bg-surface-container font-mono text-[12px] text-primary">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <div className="flex flex-col w-full h-[calc(100vh-120px)] max-h-[920px] space-y-space-sm">
      {/* Header & Student Context Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm bg-surface-container-lowest p-space-md rounded-2xl border border-outline-variant/30 shadow-xs">
        <div className="flex items-center gap-space-sm">
          <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold">
            <span className="material-symbols-outlined text-[24px]">smart_toy</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-headline-sm text-base text-on-surface font-bold leading-tight">SkillMatch AI Career Advisor</h1>
              <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
                Grounded Engine
              </span>
            </div>
            {profile ? (
              <p className="font-label-xs text-secondary text-[12px]">
                Profile: <strong className="text-on-surface">{profile.name}</strong> • {profile.major || 'Computer Science'} • GPA: {profile.gpa || '3.82'} • Target: {profile.targetRole || 'Software Engineering'}
              </p>
            ) : (
              <p className="font-label-xs text-secondary text-[12px]">
                Grounded on verified student credentials and official database listings
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-center">
          <button
            onClick={() => setMessages([messages[0]])}
            className="px-2.5 py-1 text-label-xs text-secondary hover:text-primary rounded-lg hover:bg-surface-container transition-colors"
            title="Clear Chat History"
          >
            Clear Chat
          </button>
          <Link
            to="/profile"
            className="px-3 py-1 rounded-xl bg-surface-container-low hover:bg-surface-container text-primary font-label-xs font-semibold transition-colors"
          >
            Update Profile
          </Link>
        </div>
      </div>

      {/* Main Chat Workspace */}
      <div className="flex-1 bg-surface-container-lowest rounded-2xl shadow-sm border border-outline-variant/30 flex flex-col overflow-hidden">
        {/* Messages List */}
        <div className="flex-1 p-space-lg overflow-y-auto space-y-space-md">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start gap-space-sm ${
                m.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-label-xs font-bold ${
                  m.sender === 'user'
                    ? 'bg-primary text-on-primary'
                    : 'bg-surface-container text-primary'
                }`}
              >
                {m.sender === 'user' ? (
                  profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'ME'
                ) : (
                  <span className="material-symbols-outlined text-[18px]">smart_toy</span>
                )}
              </div>

              <div
                className={`max-w-2xl p-space-md rounded-2xl font-body-sm text-body-sm leading-relaxed relative group ${
                  m.sender === 'user'
                    ? 'bg-primary text-on-primary rounded-tr-none'
                    : 'bg-surface-container-low text-on-surface rounded-tl-none border border-outline-variant/30'
                }`}
              >
                {/* Copy Button */}
                {m.sender === 'ai' && (
                  <button
                    onClick={() => handleCopyText(m.text, m.id)}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md bg-surface-container hover:bg-surface-container-high text-secondary hover:text-primary text-[11px]"
                    title="Copy response"
                  >
                    <span className="material-symbols-outlined text-[14px]">
                      {copiedId === m.id ? 'check' : 'content_copy'}
                    </span>
                  </button>
                )}

                {/* Body Content */}
                <div className="text-on-surface whitespace-normal">
                  {renderFormattedText(m.text)}
                </div>

                {/* Sources Attribution */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-outline-variant/20 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-outline">Verified Sources:</span>
                    {m.sources.map((s, idx) => (
                      <Link
                        key={idx}
                        to={s.link || '#'}
                        className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg bg-surface-container text-primary font-label-xs text-[11px] hover:bg-surface-container-high transition-colors"
                      >
                        <span className="material-symbols-outlined text-[12px]">verified</span>
                        <span>{s.title}</span>
                      </Link>
                    ))}
                  </div>
                )}

                {/* Recommended Actions */}
                {m.recommendedActions && m.recommendedActions.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                    {m.recommendedActions.map((act, idx) => (
                      <Link
                        key={idx}
                        to={act.link}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-primary/10 hover:bg-primary/20 text-primary font-label-xs font-semibold transition-colors border border-primary/20"
                      >
                        <span>{act.label}</span>
                        <span className="material-symbols-outlined text-[13px]">arrow_forward</span>
                      </Link>
                    ))}
                  </div>
                )}

                {/* Suggested Followup Chips */}
                {m.suggestedFollowups && m.suggestedFollowups.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-outline-variant/15">
                    <span className="text-[10px] font-semibold text-secondary uppercase tracking-wider block mb-1">
                      Suggested Follow-ups:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.suggestedFollowups.map((sug, idx) => (
                        <button
                          key={idx}
                          disabled={loading}
                          onClick={() => handleSendMessage(null, sug)}
                          className="text-[11px] px-2.5 py-1 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface hover:text-primary transition-colors text-left border border-outline-variant/20"
                        >
                          {sug} →
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <span
                  className={`text-[10px] mt-2 block ${
                    m.sender === 'user' ? 'text-primary-fixed/80' : 'text-outline'
                  }`}
                >
                  {m.time}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-start gap-space-sm flex-row">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-surface-container text-primary">
                <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>
              </div>
              <div className="p-space-md rounded-2xl bg-surface-container-low text-secondary font-body-sm text-body-sm rounded-tl-none border border-outline-variant/30 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
                <span>Synthesizing verified profile data, match vectors & career intelligence...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Modes & Intent Shortcuts Bar */}
        <div className="px-space-md py-2 bg-surface-container-low/60 flex items-center gap-2 overflow-x-auto scrollbar-none border-t border-outline-variant/20">
          <span className="text-[11px] font-bold text-secondary uppercase tracking-wider whitespace-nowrap shrink-0">
            Quick Prompts:
          </span>
          {CATEGORY_MODES.map((mode) => (
            <button
              key={mode.label}
              disabled={loading}
              onClick={() => handleSendMessage(null, mode.prompt)}
              className="px-3 py-1 rounded-full bg-surface-container-lowest hover:bg-surface-container text-on-surface font-label-xs text-[11px] font-medium whitespace-nowrap transition-colors border border-outline-variant/30 shadow-2xs hover:text-primary"
            >
              {mode.label}
            </button>
          ))}
        </div>

        {/* Chat Input Box */}
        <form onSubmit={handleSendMessage} className="p-space-md border-t border-outline-variant/30 bg-surface-container-lowest flex items-center gap-space-sm">
          <input
            type="text"
            disabled={loading}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask about interview prep, missing skills, tailored cover pitches, or branch opportunities..."
            className="flex-1 h-11 px-space-md rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary disabled:opacity-60 placeholder:text-outline"
          />
          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="h-11 px-space-lg bg-primary hover:bg-primary-container disabled:opacity-50 text-on-primary rounded-xl font-label-md font-semibold flex items-center gap-1 transition-colors shadow-sm shrink-0"
          >
            <span>Send</span>
            <span className="material-symbols-outlined text-[18px]">send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
