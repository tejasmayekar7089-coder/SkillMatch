import React, { useState, useEffect } from 'react';
import { StudentProfile } from '../../types';
import { profileService } from '../../services/profileService';
import { resumeService, ResumeExtractedData } from '../../services/resumeService';
import { Modal } from '../../components/common/Modal';
import { getSafeAvatarUrl } from '../../services/authService';

export const BRANCH_OPTIONS = [
  'Computer Science',
  'AI & Machine Learning',
  'Data Science',
  'Mechanical Engineering',
  'Electrical & Electronics Engineering',
  'Electronics & Communication Engineering',
  'Finance & Economics',
  'Information Technology',
  'Civil Engineering',
];

export const TARGET_ROLE_OPTIONS = [
  'Machine Learning Engineer',
  'Data Scientist',
  'Full-Stack Developer',
  'Cloud Solutions Architect',
  'Cybersecurity Analyst',
  'Mechanical Design Engineer',
  'Robotics & Mechatronics Engineer',
  'Automotive & EV Systems Engineer',
  'Embedded Systems Engineer',
  'VLSI Design Engineer',
  'Power & Renewable Energy Engineer',
  'Financial Analyst',
  'Quantitative Finance Analyst',
  'Equity Research & Investment Analyst',
];

export const SUGGESTED_SKILLS_BY_DOMAIN: Record<string, string[]> = {
  mechanical: ['SolidWorks', 'ANSYS FEA', 'Thermodynamics', 'GD&T', 'Robotics & ROS', 'MATLAB', 'DFM'],
  electrical: ['Embedded C', 'STM32', 'RTOS', 'PCB Design', 'Verilog', 'Circuit Design', 'Power Electronics'],
  finance: ['Financial Modeling', 'DCF Valuation', 'Corporate Finance', 'Bloomberg', 'Advanced Excel', 'Equity Research'],
  cs: ['Python', 'PyTorch', 'FastAPI', 'React', 'TypeScript', 'Docker', 'PostgreSQL', 'AWS Cloud'],
};

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editBio, setEditBio] = useState('');
  const [editGpa, setEditGpa] = useState('3.82');
  const [editDegree, setEditDegree] = useState('');
  const [editMajor, setEditMajor] = useState('');
  const [editTargetRole, setEditTargetRole] = useState('');
  const [editUniversity, setEditUniversity] = useState('');
  const [editAvatarUrl, setEditAvatarUrl] = useState('');
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState('Intermediate');

  // Resume Intelligence States
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  const [resumeStep, setResumeStep] = useState<'upload' | 'processing' | 'preview' | 'success'>('upload');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [extractedData, setExtractedData] = useState<ResumeExtractedData | null>(null);
  const [confirmedSkills, setConfirmedSkills] = useState<string[]>([]);
  const [confirmedName, setConfirmedName] = useState('');
  const [confirmedCollege, setConfirmedCollege] = useState('');
  const [confirmedDegree, setConfirmedDegree] = useState('');
  const [confirmedBranch, setConfirmedBranch] = useState('');
  const [confirmedGpa, setConfirmedGpa] = useState('');
  const [confirmedSummary, setConfirmedSummary] = useState('');
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);

  useEffect(() => {
    profileService.getProfile().then((data) => {
      setProfile(data);
      setEditBio(data.summary || '');
      setEditGpa(data.gpa ? data.gpa.toString() : '3.82');
      setEditDegree(data.degree || '');
      setEditMajor(data.major || '');
      setEditTargetRole(data.targetRole || '');
      setEditUniversity(data.university || '');
      setEditAvatarUrl(data.avatarUrl || '');
      setLoading(false);
    });
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    const updated = await profileService.updateProfile({
      summary: editBio,
      gpa: parseFloat(editGpa) || profile.gpa,
      degree: editDegree || profile.degree,
      major: editMajor || profile.major,
      targetRole: editTargetRole || profile.targetRole,
      university: editUniversity || profile.university,
      avatarUrl: editAvatarUrl || undefined,
    } as any);
    setProfile(updated);
    setIsEditModalOpen(false);
  };

  const handleQuickAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;
    await profileService.addSkill(newSkillName.trim(), newSkillProficiency);
    setNewSkillName('');
    const refreshed = await profileService.getProfile();
    setProfile(refreshed);
  };

  const handleResumeFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setResumeError('Please select a valid PDF file.');
        return;
      }
      setResumeFile(file);
      setResumeError(null);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!resumeFile) return;
    setResumeStep('processing');
    setResumeError(null);
    try {
      const res = await resumeService.uploadResume(resumeFile);
      const data = res.extracted_data;
      setExtractedData(data);
      setConfirmedName(data.name || profile?.name || '');
      setConfirmedCollege(data.college || profile?.university || '');
      setConfirmedDegree(data.degree || profile?.degree || '');
      setConfirmedBranch(data.branch || profile?.major || '');
      setConfirmedGpa(data.gpa ? data.gpa.toString() : profile?.gpa?.toString() || '');
      setConfirmedSummary(data.summary || profile?.summary || '');
      setConfirmedSkills(data.skills || []);
      setResumeStep('preview');
    } catch (err: any) {
      setResumeError(err.message || 'Failed to extract resume details');
      setResumeStep('upload');
    }
  };

  const toggleSkill = (skill: string) => {
    if (confirmedSkills.includes(skill)) {
      setConfirmedSkills(confirmedSkills.filter((s) => s !== skill));
    } else {
      setConfirmedSkills([...confirmedSkills, skill]);
    }
  };

  const handleConfirmResume = async () => {
    setIsConfirming(true);
    setResumeError(null);
    try {
      await resumeService.confirmResume({
        name: confirmedName || undefined,
        college: confirmedCollege || undefined,
        degree: confirmedDegree || undefined,
        branch: confirmedBranch || undefined,
        gpa: confirmedGpa ? parseFloat(confirmedGpa) : undefined,
        summary: confirmedSummary || undefined,
        skills: confirmedSkills,
        projects: extractedData?.projects?.map((p) => ({
          title: p.title,
          description: p.description,
          technologies: p.technologies,
        })),
        certifications: extractedData?.certifications?.map((c) => ({
          name: c.name,
          issuing_organization: c.issuing_organization,
          issue_date: c.issue_date,
        })),
      });

      const updated = await profileService.getProfile();
      setProfile(updated);
      setResumeStep('success');
      setTimeout(() => {
        setIsResumeModalOpen(false);
        setResumeStep('upload');
        setResumeFile(null);
        setExtractedData(null);
      }, 1400);
    } catch (err: any) {
      setResumeError(err.message || 'Failed to apply resume data');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleResetResumeModal = () => {
    setIsResumeModalOpen(false);
    setResumeStep('upload');
    setResumeFile(null);
    setExtractedData(null);
    setResumeError(null);
  };

  if (loading || !profile) {
    return (
      <div className="py-20 flex justify-center">
        <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full space-y-space-xl">
      {/* Header Profile Bento Card */}
      <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-space-lg">
            <img
              src={getSafeAvatarUrl(profile.avatarUrl, profile.name)}
              alt={profile.name}
              onError={(e) => {
                (e.target as HTMLImageElement).src = getSafeAvatarUrl(null, profile.name);
              }}
              className="w-24 h-24 rounded-2xl object-cover ring-2 ring-primary/20 shadow-sm"
            />
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-space-xs">
                <h1 className="font-display-lg text-display-lg text-on-surface tracking-tight">{profile.name}</h1>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[#065F46] font-label-xs font-semibold">
                  <span className="material-symbols-outlined text-[14px]">verified</span>
                  Verified Profile {profile.verifiedProfilePercent || 94}%
                </span>
              </div>
              <p className="font-body-md text-secondary">
                {profile.degree} in {profile.major} • {profile.year} ({profile.university})
              </p>
              <p className="font-label-sm text-primary font-semibold">
                Target Role: {profile.targetRole} • Cumulative GPA: {profile.gpa} / 4.00
              </p>
            </div>
          </div>

          <div className="flex items-center gap-space-sm shrink-0">
            <button
              onClick={() => setIsResumeModalOpen(true)}
              className="px-space-md py-space-xs bg-primary hover:bg-primary-container text-on-primary font-label-md font-semibold rounded-xl transition-colors flex items-center gap-1 shadow-sm"
            >
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
              <span>Import Resume</span>
            </button>
            <button
              onClick={() => setIsEditModalOpen(true)}
              className="px-space-md py-space-xs bg-surface-container hover:bg-surface-container-high text-primary font-label-md font-semibold rounded-xl transition-colors flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[18px]">edit</span>
              <span>Edit Profile</span>
            </button>
          </div>
        </div>

        <div className="mt-space-lg pt-space-md border-t border-outline-variant/20">
          <p className="font-body-md text-on-surface-variant leading-relaxed">{profile.summary}</p>
        </div>
      </div>

      {/* Two Column Section: Skills & Academics vs Projects & Certifications */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        {/* Left Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-space-xl">
          {/* Verified Skills Matrix */}
          <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-md text-on-surface font-semibold">Verified Skills</h3>
              <span className="font-label-xs text-primary font-semibold">{profile.skills.length} Skills Validated</span>
            </div>

            {/* Quick Add Skill input */}
            <form onSubmit={handleQuickAddSkill} className="flex gap-2">
              <input
                type="text"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                placeholder="Add new skill (e.g. SolidWorks, Embedded C, Financial Modeling)"
                className="flex-1 h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary text-xs"
              />
              <select
                value={newSkillProficiency}
                onChange={(e) => setNewSkillProficiency(e.target.value)}
                className="h-9 px-2 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface text-xs"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Essential">Essential</option>
              </select>
              <button
                type="submit"
                className="px-3 h-9 rounded-xl bg-primary text-on-primary font-label-xs font-semibold hover:bg-primary-container transition-colors text-xs"
              >
                Add
              </button>
            </form>

            {/* Suggested Skill Chips for quick addition */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[11px] text-outline font-medium">Quick Add:</span>
              {(() => {
                const majorLower = (profile?.major || '').toLowerCase();
                const domainKey = majorLower.includes('mech')
                  ? 'mechanical'
                  : majorLower.includes('elec') || majorLower.includes('vlsi') || majorLower.includes('circuit')
                  ? 'electrical'
                  : majorLower.includes('finan') || majorLower.includes('econ')
                  ? 'finance'
                  : 'cs';
                const suggestions = SUGGESTED_SKILLS_BY_DOMAIN[domainKey] || SUGGESTED_SKILLS_BY_DOMAIN.cs;
                return suggestions.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => {
                      setNewSkillName(s);
                      profileService.addSkill(s, 'Intermediate').then(() => {
                        profileService.getProfile().then(setProfile);
                      });
                    }}
                    className="px-2 py-0.5 rounded-lg bg-surface-container hover:bg-primary hover:text-on-primary text-on-surface-variant text-[11px] font-medium transition-colors"
                  >
                    + {s}
                  </button>
                ));
              })()}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-sm">
              {profile.skills.map((s) => (
                <div key={s.name} className="p-space-sm rounded-xl bg-surface-container-low flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-label-md text-on-surface font-semibold">{s.name}</span>
                    <span
                      className={`text-label-xs font-semibold ${
                        s.verified ? 'text-tertiary' : 'text-secondary'
                      }`}
                    >
                      {s.level}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] text-on-surface-variant">
                    <span className="material-symbols-outlined text-[13px] text-tertiary">
                      {s.verified ? 'verified' : 'pending'}
                    </span>
                    <span className="truncate">{s.verifiedVia}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Academic Transcripts */}
          <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
            <h3 className="font-headline-md text-on-surface font-semibold">Academic Education</h3>
            {profile.education.map((edu, idx) => (
              <div key={idx} className="space-y-space-xs p-space-md rounded-xl bg-surface-container-low">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-headline-sm text-on-surface font-semibold">{edu.institution}</h4>
                    <p className="font-body-sm text-secondary">{edu.degree}</p>
                  </div>
                  <span className="font-label-xs text-primary font-bold">{edu.period}</span>
                </div>
                <p className="font-label-sm text-tertiary font-semibold">Verified Transcript: {edu.gpa}</p>
                <div className="pt-1 flex flex-wrap gap-1">
                  {edu.courses.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded bg-surface-container text-on-surface font-label-xs">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column (5 Cols) */}
        <div className="lg:col-span-5 space-y-space-xl">
          {/* Verified Repos & Projects */}
          <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
            <h3 className="font-headline-md text-on-surface font-semibold">Portfolio Projects</h3>
            <div className="space-y-space-sm">
              {profile.projects.map((proj) => (
                <div key={proj.name} className="p-space-md rounded-xl bg-surface-container-low space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-label-md text-on-surface font-bold">{proj.name}</h4>
                    <span className="material-symbols-outlined text-tertiary text-[18px]">verified</span>
                  </div>
                  <p className="font-body-sm text-secondary text-label-xs leading-relaxed">{proj.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {proj.technologies.map((t) => (
                      <span key={t} className="px-2 py-0.5 rounded bg-surface-container text-primary font-label-xs font-medium">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-xl border border-outline-variant/30 space-y-space-md">
            <h3 className="font-headline-md text-on-surface font-semibold">Certifications</h3>
            <div className="space-y-space-xs">
              {profile.certifications.map((cert) => (
                <div key={cert.name} className="p-space-sm rounded-xl bg-surface-container-low flex items-center justify-between">
                  <div>
                    <p className="font-label-sm text-on-surface font-semibold">{cert.name}</p>
                    <p className="font-label-xs text-secondary">{cert.issuer} • Issued {cert.date}</p>
                  </div>
                  <span className="material-symbols-outlined text-tertiary text-[18px]">verified</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title="Edit Student Profile">
        <form onSubmit={handleSaveProfile} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Profile Avatar (URL or Initials)</label>
            <div className="flex gap-2 items-center">
              <img
                src={getSafeAvatarUrl(editAvatarUrl || profile.avatarUrl, profile.name)}
                alt="Avatar Preview"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = getSafeAvatarUrl(null, profile.name);
                }}
                className="w-10 h-10 rounded-xl object-cover ring-1 ring-outline-variant/40 shrink-0"
              />
              <input
                type="text"
                value={editAvatarUrl}
                onChange={(e) => setEditAvatarUrl(e.target.value)}
                placeholder="https://... (or leave blank for your personalized initials avatar)"
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary text-xs"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">College / University</label>
            <input
              type="text"
              value={editUniversity}
              onChange={(e) => setEditUniversity(e.target.value)}
              className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="grid grid-cols-2 gap-space-sm">
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Degree</label>
              <input
                type="text"
                value={editDegree}
                onChange={(e) => setEditDegree(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Major / Branch</label>
              <input
                type="text"
                list="branch-list"
                value={editMajor}
                onChange={(e) => setEditMajor(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
              <datalist id="branch-list">
                {BRANCH_OPTIONS.map((b) => (
                  <option key={b} value={b} />
                ))}
              </datalist>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-space-sm">
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Target Role</label>
              <input
                type="text"
                list="role-list"
                value={editTargetRole}
                onChange={(e) => setEditTargetRole(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
              <datalist id="role-list">
                {TARGET_ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r} />
                ))}
              </datalist>
            </div>
            <div className="space-y-1">
              <label className="font-label-sm text-on-surface font-medium">Cumulative GPA (Scale of 4.0)</label>
              <input
                type="text"
                value={editGpa}
                onChange={(e) => setEditGpa(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Bio & Professional Summary</label>
            <textarea
              rows={3}
              value={editBio}
              onChange={(e) => setEditBio(e.target.value)}
              className="w-full p-2.5 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="flex justify-end gap-space-sm pt-space-xs">
            <button
              type="button"
              onClick={() => setIsEditModalOpen(false)}
              className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-space-lg py-space-xs bg-primary hover:bg-primary-container text-on-primary rounded-xl font-label-md"
            >
              Save Changes
            </button>
          </div>
        </form>
      </Modal>

      {/* Resume Intelligence Import Modal */}
      <Modal isOpen={isResumeModalOpen} onClose={handleResetResumeModal} title="Resume Intelligence & Skill Parser">
        {resumeError && (
          <div className="mb-4 p-3 rounded-xl bg-error/10 border border-error/20 flex items-center gap-2 text-error text-body-sm">
            <span className="material-symbols-outlined text-[18px]">error</span>
            <span>{resumeError}</span>
          </div>
        )}

        {resumeStep === 'upload' && (
          <div className="space-y-space-md">
            <div className="border-2 border-dashed border-outline-variant/60 rounded-2xl p-6 text-center hover:border-primary/50 transition-colors bg-surface-container-low/50">
              <span className="material-symbols-outlined text-[48px] text-primary mb-2 block">
                picture_as_pdf
              </span>
              <p className="font-headline-sm text-on-surface font-semibold">Upload Candidate Resume (PDF)</p>
              <p className="font-body-sm text-secondary mt-1 max-w-sm mx-auto">
                SkillMatch will extract your academic credentials, projects, and normalized technical skills automatically.
              </p>
              <div className="mt-4">
                <label className="inline-flex items-center gap-2 px-space-lg py-space-xs bg-primary text-on-primary font-label-md rounded-xl cursor-pointer hover:bg-primary-container transition-colors shadow-sm">
                  <span className="material-symbols-outlined text-[18px]">attach_file</span>
                  <span>Choose PDF File</span>
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    className="hidden"
                    onChange={handleResumeFileChange}
                  />
                </label>
              </div>
              {resumeFile && (
                <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-container text-on-surface text-label-sm font-medium">
                  <span className="material-symbols-outlined text-[16px] text-tertiary">check_circle</span>
                  <span>{resumeFile.name} ({(resumeFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={handleResetResumeModal}
                className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!resumeFile}
                onClick={handleUploadAndAnalyze}
                className="px-space-lg py-space-xs bg-primary disabled:opacity-50 text-on-primary rounded-xl font-label-md font-semibold flex items-center gap-1 shadow-sm"
              >
                <span>Extract & Review</span>
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>
            </div>
          </div>
        )}

        {resumeStep === 'processing' && (
          <div className="py-12 flex flex-col items-center justify-center space-y-4 text-center">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <div>
              <h4 className="font-headline-sm text-on-surface font-semibold">Analyzing Resume with AI</h4>
              <p className="font-body-sm text-secondary mt-1">
                Extracting technical skills, projects, and normalizing canonical competencies...
              </p>
            </div>
          </div>
        )}

        {resumeStep === 'preview' && (
          <div className="space-y-space-md max-h-[70vh] overflow-y-auto pr-1">
            <div className="p-3 bg-surface-container-low rounded-xl border border-outline-variant/30 flex items-start gap-2 text-on-surface text-body-sm">
              <span className="material-symbols-outlined text-[20px] text-primary shrink-0">info</span>
              <div>
                <p className="font-semibold text-xs text-primary uppercase tracking-wider">Preview Extracted Data</p>
                <p className="text-xs text-secondary mt-0.5">
                  Review the detected fields. Nothing has been saved yet. You can edit any field or toggle skills before confirming.
                </p>
              </div>
            </div>

            {/* Extracted Skills Selector */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="font-label-sm text-on-surface font-semibold">
                  Detected Skills ({confirmedSkills.length})
                </label>
                <span className="text-[11px] text-secondary">Click any chip to include/exclude</span>
              </div>
              <div className="flex flex-wrap gap-1.5 p-3 rounded-xl bg-surface-container-low border border-outline-variant/40 max-h-36 overflow-y-auto">
                {extractedData?.skills && extractedData.skills.length > 0 ? (
                  extractedData.skills.map((skill) => {
                    const isSelected = confirmedSkills.includes(skill);
                    return (
                      <button
                        key={skill}
                        type="button"
                        onClick={() => toggleSkill(skill)}
                        className={`px-2.5 py-1 rounded-lg text-label-xs font-semibold flex items-center gap-1 transition-all ${
                          isSelected
                            ? 'bg-primary text-on-primary shadow-sm'
                            : 'bg-surface-container text-secondary line-through opacity-60'
                        }`}
                      >
                        <span>{skill}</span>
                        <span className="material-symbols-outlined text-[14px]">
                          {isSelected ? 'check' : 'close'}
                        </span>
                      </button>
                    );
                  })
                ) : (
                  <span className="text-xs text-secondary">No skills identified in document text.</span>
                )}
              </div>
            </div>

            {/* Academic Information */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-sm">
              <div className="space-y-1">
                <label className="font-label-xs text-on-surface font-medium">Candidate Name</label>
                <input
                  type="text"
                  value={confirmedName}
                  onChange={(e) => setConfirmedName(e.target.value)}
                  className="w-full h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-xs text-on-surface"
                />
              </div>
              <div className="space-y-1">
                <label className="font-label-xs text-on-surface font-medium">University / College</label>
                <input
                  type="text"
                  value={confirmedCollege}
                  onChange={(e) => setConfirmedCollege(e.target.value)}
                  className="w-full h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-xs text-on-surface"
                />
              </div>
              <div className="space-y-1">
                <label className="font-label-xs text-on-surface font-medium">Degree</label>
                <input
                  type="text"
                  value={confirmedDegree}
                  onChange={(e) => setConfirmedDegree(e.target.value)}
                  className="w-full h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-xs text-on-surface"
                />
              </div>
              <div className="space-y-1">
                <label className="font-label-xs text-on-surface font-medium">Major / Branch</label>
                <input
                  type="text"
                  value={confirmedBranch}
                  onChange={(e) => setConfirmedBranch(e.target.value)}
                  className="w-full h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-xs text-on-surface"
                />
              </div>
              <div className="space-y-1">
                <label className="font-label-xs text-on-surface font-medium">Cumulative GPA</label>
                <input
                  type="text"
                  value={confirmedGpa}
                  onChange={(e) => setConfirmedGpa(e.target.value)}
                  className="w-full h-9 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-xs text-on-surface"
                />
              </div>
            </div>

            {/* Detected Projects Summary */}
            {extractedData?.projects && extractedData.projects.length > 0 && (
              <div className="space-y-1.5">
                <label className="font-label-sm text-on-surface font-semibold">
                  Detected Projects ({extractedData.projects.length})
                </label>
                <div className="divide-y divide-outline-variant/20 rounded-xl bg-surface-container-low border border-outline-variant/40 overflow-hidden">
                  {extractedData.projects.map((p, idx) => (
                    <div key={idx} className="p-2.5 text-xs">
                      <p className="font-semibold text-on-surface">{p.title}</p>
                      <p className="text-secondary mt-0.5 line-clamp-2">{p.description}</p>
                      {p.technologies && p.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {p.technologies.map((t, i) => (
                            <span key={i} className="px-1.5 py-0.5 rounded bg-surface-container text-[10px] font-medium text-primary">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detected Certifications Summary */}
            {extractedData?.certifications && extractedData.certifications.length > 0 && (
              <div className="space-y-1.5">
                <label className="font-label-sm text-on-surface font-semibold">
                  Detected Certifications ({extractedData.certifications.length})
                </label>
                <div className="divide-y divide-outline-variant/20 rounded-xl bg-surface-container-low border border-outline-variant/40 overflow-hidden">
                  {extractedData.certifications.map((c, idx) => (
                    <div key={idx} className="p-2.5 text-xs flex justify-between items-center">
                      <div>
                        <p className="font-semibold text-on-surface">{c.name}</p>
                        <p className="text-secondary">{c.issuing_organization}</p>
                      </div>
                      <span className="text-[11px] text-outline">{c.issue_date}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-2 border-t border-outline-variant/20">
              <button
                type="button"
                onClick={() => setResumeStep('upload')}
                className="px-space-md py-space-xs text-secondary hover:text-on-surface font-label-md"
              >
                Back
              </button>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleResetResumeModal}
                  className="px-space-md py-space-xs bg-surface-container-low rounded-xl font-label-md"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={isConfirming}
                  onClick={handleConfirmResume}
                  className="px-space-lg py-space-xs bg-primary hover:bg-primary-container text-on-primary rounded-xl font-label-md font-semibold flex items-center gap-1 shadow-sm"
                >
                  <span className="material-symbols-outlined text-[18px]">verified</span>
                  <span>{isConfirming ? 'Saving...' : 'Confirm & Update Profile'}</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {resumeStep === 'success' && (
          <div className="py-12 flex flex-col items-center justify-center space-y-3 text-center">
            <div className="w-14 h-14 rounded-full bg-[#ECFDF5] text-[#065F46] flex items-center justify-center">
              <span className="material-symbols-outlined text-[32px]">check_circle</span>
            </div>
            <h4 className="font-headline-md text-on-surface font-bold">Profile Successfully Updated!</h4>
            <p className="font-body-sm text-secondary max-w-sm">
              Your confirmed skills, academic background, and projects have been merged into your verified profile.
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
};
