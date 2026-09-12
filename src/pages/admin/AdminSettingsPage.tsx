import React, { useState } from 'react';
import { apiFetch } from '../../services/apiClient';

export const AdminSettingsPage: React.FC = () => {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await apiFetch<any>('/health');
      setTestResult(`Backend Online: status='${res.status}', database='${res.database}', version='${res.version}'`);
      alert(`Connection Verified!\n\nStatus: ${res.status}\nDatabase: ${res.database}\nVersion: ${res.version}`);
    } catch (err: any) {
      setTestResult(`Connection Failed: ${err.message}`);
      alert(`Connection Failed: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="flex flex-col w-full space-y-space-xl max-w-3xl">
      <div className="space-y-space-2xs pb-space-xs">
        <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">Admin System Settings</h1>
        <p className="font-body-lg text-secondary">Manage FastAPI backend connections, algorithm weighting hyperparameters, and API keys.</p>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
        <h3 className="font-headline-md text-on-surface font-semibold">Backend Integration Settings</h3>
        <div className="space-y-space-sm font-body-sm text-secondary">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">FastAPI Backend Endpoint URL</label>
            <input
              type="text"
              defaultValue="http://127.0.0.1:8000/api"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Embedding / Vector Model Endpoint</label>
            <input
              type="text"
              defaultValue="all-MiniLM-L6-v2 (Local Sentence-Transformers)"
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface"
            />
          </div>

          {testResult && (
            <div className="p-3 rounded-xl bg-surface-container text-primary font-label-sm">
              {testResult}
            </div>
          )}

          <div className="pt-2">
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="px-space-md py-space-xs bg-surface-container hover:bg-surface-container-high text-primary font-label-md font-semibold rounded-xl disabled:opacity-50"
            >
              {testing ? 'Testing...' : 'Test Backend Connection'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
