import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [deadlineReminders, setDeadlineReminders] = useState(true);
  const [aiRecommendations, setAiRecommendations] = useState(true);
  const [publicProfile, setPublicProfile] = useState(true);

  return (
    <div className="flex flex-col w-full space-y-space-xl max-w-4xl">
      {/* Header */}
      <div className="space-y-space-2xs pb-space-xs">
        <div className="inline-flex items-center gap-space-xs px-space-sm py-0.5 rounded-full bg-surface-container text-primary font-label-xs text-label-xs uppercase tracking-wider">
          <span className="material-symbols-outlined text-[16px]">settings</span>
          <span>Account Settings</span>
        </div>
        <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Settings & Preferences</h1>
        <p className="font-body-lg text-body-lg text-secondary">
          Manage your notification settings, algorithm personalization, profile visibility, and verified credential keys.
        </p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-space-lg">
        {/* Notification Settings */}
        <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
          <h3 className="font-headline-md text-on-surface font-semibold">Notification Preferences</h3>
          <div className="space-y-space-sm">
            <label className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low cursor-pointer">
              <div>
                <p className="font-label-md text-on-surface font-semibold">High-Match Opportunity Alerts (≥80%)</p>
                <p className="font-body-sm text-secondary text-label-xs">Receive email alerts when roles closely fitting your profile are published.</p>
              </div>
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="w-4 h-4 rounded accent-primary cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low cursor-pointer">
              <div>
                <p className="font-label-md text-on-surface font-semibold">Approaching Deadline Alerts</p>
                <p className="font-body-sm text-secondary text-label-xs">Get notified 7 days and 48 hours prior to application close dates.</p>
              </div>
              <input
                type="checkbox"
                checked={deadlineReminders}
                onChange={(e) => setDeadlineReminders(e.target.checked)}
                className="w-4 h-4 rounded accent-primary cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low cursor-pointer">
              <div>
                <p className="font-label-md text-on-surface font-semibold">AI Skill Vector Recommendations</p>
                <p className="font-body-sm text-secondary text-label-xs">Weekly suggestions for free micro-courses to close high-demand skill gaps.</p>
              </div>
              <input
                type="checkbox"
                checked={aiRecommendations}
                onChange={(e) => setAiRecommendations(e.target.checked)}
                className="w-4 h-4 rounded accent-primary cursor-pointer"
              />
            </label>
          </div>
        </div>

        {/* Privacy & Recruiter Visibility */}
        <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
          <h3 className="font-headline-md text-on-surface font-semibold">Recruiter Discovery & Privacy</h3>
          <label className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low cursor-pointer">
            <div>
              <p className="font-label-md text-on-surface font-semibold">Verified Recruiter Direct Inbox</p>
              <p className="font-body-sm text-secondary text-label-xs">Allow verified partner company talent teams to invite you directly for assessments.</p>
            </div>
            <input
              type="checkbox"
              checked={publicProfile}
              onChange={(e) => setPublicProfile(e.target.checked)}
              className="w-4 h-4 rounded accent-primary cursor-pointer"
            />
          </label>
        </div>

        {/* Account Session */}
        <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
          <h3 className="font-headline-md text-on-surface font-semibold">Account Session</h3>
          <div className="flex items-center justify-between p-space-sm rounded-xl bg-surface-container-low">
            <div>
              <p className="font-label-md text-on-surface font-semibold">Active Session</p>
              <p className="font-body-sm text-secondary text-label-xs">Sign out of your SkillMatch account on this device.</p>
            </div>
            <button
              onClick={async () => {
                await authService.logout();
                navigate('/login');
              }}
              className="px-space-md py-1.5 rounded-xl border border-error/30 text-error hover:bg-error/10 font-label-sm font-semibold transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>

        <div className="flex justify-end gap-space-sm pt-space-xs">
          <button
            onClick={() => alert('Settings saved successfully!')}
            className="px-space-xl py-space-sm bg-primary hover:bg-primary-container text-on-primary rounded-xl font-label-md font-semibold transition-colors shadow-sm"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
};
