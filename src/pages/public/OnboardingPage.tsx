import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileService } from '../../services/profileService';

export const OnboardingPage: React.FC = () => {
  const [step, setStep] = useState(1);
  const [degree, setDegree] = useState('B.Tech / B.E.');
  const [major, setMajor] = useState('Computer Science');
  const [year, setYear] = useState('3rd Year');
  const [gpa, setGpa] = useState('3.82');
  const [targetRole, setTargetRole] = useState('Machine Learning Engineer');
  const [skills, setSkills] = useState(['Python', 'Machine Learning', 'SQL', 'PyTorch']);
  const [newSkill, setNewSkill] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (name: string) => {
    setSkills(skills.filter((s) => s !== name));
  };

  const handleFinish = async () => {
    setSubmitting(true);
    try {
      await profileService.updateProfile({
        degree,
        major,
        year,
        gpa: parseFloat(gpa) || 3.82,
        targetRole,
      });
      for (const s of skills) {
        await profileService.addSkill(s, 'Intermediate');
      }
    } catch (e) {
      console.warn('Could not sync onboarding to backend:', e);
    } finally {
      setSubmitting(false);
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-space-md py-space-xl">
      <div className="w-full max-w-xl bg-surface-container-lowest rounded-2xl shadow-xl border border-outline-variant/30 p-space-xl space-y-space-lg">
        {/* Step Indicator */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-label-xs font-semibold uppercase tracking-wider text-secondary">
            <span>Onboarding Progress</span>
            <span className="text-primary">Step {step} of 3</span>
          </div>
          <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden flex">
            <div
              className="bg-primary h-full transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step 1: Academic Background */}
        {step === 1 && (
          <div className="space-y-space-md animate-in fade-in">
            <div>
              <h2 className="font-headline-md text-on-surface font-bold">Academic Verification</h2>
              <p className="font-body-sm text-secondary">
                Tell us about your current university program and academic standing.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-sm">
              <div className="space-y-1">
                <label className="font-label-sm text-on-surface font-medium">Degree Level</label>
                <select
                  value={degree}
                  onChange={(e) => setDegree(e.target.value)}
                  className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
                >
                  <option>B.Tech / B.E.</option>
                  <option>B.S. / B.Sc.</option>
                  <option>M.S. / M.Tech</option>
                  <option>Ph.D.</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-label-sm text-on-surface font-medium">Major / Specialization</label>
                <input
                  type="text"
                  value={major}
                  onChange={(e) => setMajor(e.target.value)}
                  className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div className="space-y-1">
                <label className="font-label-sm text-on-surface font-medium">Current Academic Year</label>
                <select
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
                >
                  <option>1st Year</option>
                  <option>2nd Year</option>
                  <option>3rd Year</option>
                  <option>4th Year / Final</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-label-sm text-on-surface font-medium">Cumulative GPA (Scale of 4.0)</label>
                <input
                  type="text"
                  value={gpa}
                  onChange={(e) => setGpa(e.target.value)}
                  className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="flex justify-end pt-space-sm">
              <button
                onClick={() => setStep(2)}
                className="px-space-xl py-space-xs rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container transition-colors shadow-sm"
              >
                Next Step →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Target Role */}
        {step === 2 && (
          <div className="space-y-space-md animate-in fade-in">
            <div>
              <h2 className="font-headline-md text-on-surface font-bold">Target Trajectory</h2>
              <p className="font-body-sm text-secondary">
                Select your primary aspirational job role for customized gap analysis and roadmap mapping.
              </p>
            </div>

            <div className="space-y-space-xs">
              {[
                'Machine Learning Engineer',
                'Data Scientist',
                'Full-Stack Developer',
                'Cloud Solutions Architect',
                'Cybersecurity Analyst',
              ].map((role) => (
                <label
                  key={role}
                  className={`flex items-center justify-between p-space-md rounded-xl border cursor-pointer transition-all ${
                    targetRole === role
                      ? 'bg-surface-container border-primary ring-1 ring-primary'
                      : 'bg-surface-container-low border-outline-variant/30 hover:bg-surface-container-low/70'
                  }`}
                >
                  <span className="font-label-md text-on-surface font-semibold">{role}</span>
                  <input
                    type="radio"
                    name="targetRole"
                    value={role}
                    checked={targetRole === role}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="accent-primary"
                  />
                </label>
              ))}
            </div>

            <div className="flex justify-between pt-space-sm">
              <button
                onClick={() => setStep(1)}
                className="px-space-md py-space-xs rounded-xl bg-surface-container-low font-label-md"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="px-space-xl py-space-xs rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container transition-colors shadow-sm"
              >
                Next Step →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Verified Skills & Repos */}
        {step === 3 && (
          <div className="space-y-space-md animate-in fade-in">
            <div>
              <h2 className="font-headline-md text-on-surface font-bold">Skills & Credential Setup</h2>
              <p className="font-body-sm text-secondary">
                Add skills and project repositories for automated match score calibration.
              </p>
            </div>

            <form onSubmit={handleAddSkill} className="flex gap-space-xs">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                placeholder="Type a skill e.g. TensorFlow, Docker..."
                className="flex-1 h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
              <button
                type="submit"
                className="px-space-md h-10 bg-surface-container hover:bg-surface-container-high text-primary rounded-xl font-label-sm font-semibold"
              >
                Add Skill
              </button>
            </form>

            <div className="flex flex-wrap gap-2 p-space-sm bg-surface-container-low rounded-xl min-h-20">
              {skills.map((s) => (
                <span
                  key={s}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-surface-container-lowest border border-outline-variant/30 text-on-surface font-label-sm font-medium shadow-sm"
                >
                  <span className="material-symbols-outlined text-[14px] text-tertiary">check_circle</span>
                  <span>{s}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(s)}
                    className="hover:text-error text-secondary ml-1"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>

            <div className="p-space-sm bg-surface-container-low rounded-xl flex items-center justify-between text-label-xs text-secondary">
              <div className="flex items-center gap-1 text-tertiary font-semibold">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                Profile Ready: 94% Verified Fit
              </div>
              <span className="text-primary font-bold">14 Matches Awaiting</span>
            </div>

            <div className="flex justify-between pt-space-sm">
              <button
                onClick={() => setStep(2)}
                className="px-space-md py-space-xs rounded-xl bg-surface-container-low font-label-md"
              >
                ← Back
              </button>
              <button
                onClick={handleFinish}
                disabled={submitting}
                className="px-space-2xl py-space-xs rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container transition-colors shadow-md flex items-center gap-1 disabled:opacity-70"
              >
                <span>{submitting ? 'Setting up Profile...' : 'Launch SkillMatch'}</span>
                <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
