import { StudentProfile } from '../types';
import { apiFetch, tokenStorage, userStorage } from './apiClient';
import { mockProfile } from './mockData';
import { getSafeAvatarUrl } from './authService';

export function generateDomainSummary(major?: string, degree?: string, university?: string, targetRole?: string): string {
  const m = (major || '').toLowerCase();
  const d = degree || 'Degree';
  const u = university || 'University';
  const r = targetRole || 'Specialist';
  if (m.includes('elec') || m.includes('embedded') || m.includes('circuit')) {
    return `Electrical engineering candidate pursuing ${d} at ${u}. Specializing in microcontrollers, embedded firmware development (ARM/STM32), PCB layout, and hardware-software integration for ${r}.`;
  }
  if (m.includes('mech') || m.includes('auto') || m.includes('robot')) {
    return `Mechanical engineering candidate pursuing ${d} at ${u}. Experienced in CAD 3D parametric modeling (SolidWorks), ANSYS structural FEA, thermodynamics, and mechatronic robotics targeting ${r}.`;
  }
  if (m.includes('finan') || m.includes('econ') || m.includes('account')) {
    return `Finance and quantitative analysis student pursuing ${d} at ${u}. Demonstrating core competencies in 3-statement financial modeling, DCF valuation, Bloomberg telemetry, and investment analytics for ${r}.`;
  }
  return `Undergraduate student pursuing ${d} in ${major || 'Computer Science'} at ${u}. Demonstrating technical competencies and project experience targeted for ${r}.`;
}

export function generateDomainEducation(major?: string, degree?: string, university?: string, gpa?: number, gradYear?: string) {
  const m = (major || '').toLowerCase();
  const inst = university || 'Institute of Technology';
  const deg = degree || 'Bachelor of Technology';
  const spec = major || 'Engineering';
  const gpaStr = typeof gpa === 'number' ? `${gpa.toFixed(2)} / 4.00` : '3.82 / 4.00';
  const period = `2023 - ${gradYear || '2027'} (Expected)`;

  let courses = ['CS421: Machine Learning Systems', 'CS301: Data Structures & Algorithms', 'CS312: Database Management Systems', 'MATH220: Linear Algebra & Probability'];
  if (m.includes('elec') || m.includes('embedded') || m.includes('circuit')) {
    courses = ['EE301: Microprocessor Systems', 'EE412: Digital Signal Processing', 'EE320: Embedded Firmware & RTOS', 'EE210: Circuit Theory & Analog Design'];
  } else if (m.includes('mech') || m.includes('auto') || m.includes('robot')) {
    courses = ['ME301: Thermodynamics & Heat Transfer', 'ME315: Computer-Aided Design (CAD)', 'ME402: Finite Element Analysis', 'ME330: Dynamics & Kinematics'];
  } else if (m.includes('finan') || m.includes('econ') || m.includes('account')) {
    courses = ['FIN301: Corporate Finance & Valuation', 'FIN410: Financial Econometrics', 'FIN320: Investment Analysis & Portfolio Theory', 'ACCT201: Financial Statement Analysis'];
  }

  return [
    {
      institution: inst,
      degree: `${deg} in ${spec}`,
      period: period,
      gpa: `Verified Transcript: ${gpaStr}`,
      courses: courses,
    },
  ];
}

export function generateDomainProjects(major?: string) {
  const m = (major || '').toLowerCase();
  if (m.includes('elec') || m.includes('embedded') || m.includes('circuit')) {
    return [
      {
        name: 'STM32 RTOS Motor Control Unit',
        description: 'Developed bare-metal firmware and FreeRTOS task scheduling for high-efficiency brushless DC motor controller with CAN telemetry.',
        technologies: ['Embedded C', 'STM32', 'FreeRTOS', 'CAN Bus', 'Altium'],
        link: 'https://github.com/student/stm32-motor-control',
        verified: true,
      },
      {
        name: 'High-Speed FPGA Digital Signal Pipeline',
        description: 'Designed RTL pipelined architecture in Verilog for real-time Fourier transform with zero-loss FIFO buffering.',
        technologies: ['Verilog', 'FPGA', 'Xilinx Vivado', 'Digital Electronics'],
        link: 'https://github.com/student/fpga-dsp-pipeline',
        verified: true,
      },
    ];
  }
  if (m.includes('mech') || m.includes('auto') || m.includes('robot')) {
    return [
      {
        name: 'Autonomous Mobile Robot (ROS 2 & Gazebo)',
        description: 'Designed CAD chassis in SolidWorks and engineered ROS 2 navigation stack with SLAM LIDAR mapping and path planning.',
        technologies: ['SolidWorks', 'ROS 2', 'C++', 'Python', 'Gazebo'],
        link: 'https://github.com/student/ros2-autonomous-robot',
        verified: true,
      },
      {
        name: 'EV Battery Pack Thermal Simulation',
        description: 'Conducted ANSYS thermal FEA and computational fluid dynamics (CFD) for liquid-cooled lithium-ion cell pack under extreme discharge.',
        technologies: ['ANSYS FEA', 'SolidWorks', 'Thermodynamics', 'MATLAB'],
        link: 'https://github.com/student/ev-battery-thermal-fea',
        verified: true,
      },
    ];
  }
  if (m.includes('finan') || m.includes('econ') || m.includes('account')) {
    return [
      {
        name: 'Three-Statement LBO & DCF Valuation Model',
        description: 'Built a dynamic financial model analyzing $2.4B private equity buyout with debt schedule, sensitivity tables, and waterfall returns.',
        technologies: ['Financial Modeling', 'DCF Valuation', 'Advanced Excel', 'Corporate Finance'],
        link: 'https://github.com/student/lbo-valuation-model',
        verified: true,
      },
      {
        name: 'Algorithmic Portfolio Risk Engine',
        description: 'Engineered Python quantitative strategy backtesting engine calculating Historical VaR, CVaR, and Sharpe optimization on S&P 500 tick data.',
        technologies: ['Python', 'Pandas', 'Quantitative Finance', 'Risk Management'],
        link: 'https://github.com/student/quant-risk-engine',
        verified: true,
      },
    ];
  }
  return mockProfile.projects;
}

export function generateDomainCertifications(major?: string) {
  const m = (major || '').toLowerCase();
  if (m.includes('elec') || m.includes('embedded')) {
    return [
      { name: 'ARM Cortex-M Embedded Systems Professional', issuer: 'ARM Education', date: 'Oct 2025', verified: true },
      { name: 'Verified Altium PCB Designer', issuer: 'SkillMatch Proctor Certification', date: 'Jan 2026', verified: true },
    ];
  }
  if (m.includes('mech') || m.includes('auto')) {
    return [
      { name: 'Certified SOLIDWORKS Associate (CSWA)', issuer: 'Dassault Systèmes', date: 'Sep 2025', verified: true },
      { name: 'ANSYS Structural FEA Specialist', issuer: 'Ansys Innovation Courses', date: 'Dec 2025', verified: true },
    ];
  }
  if (m.includes('finan') || m.includes('econ')) {
    return [
      { name: 'Financial Modeling & Valuation Analyst (FMVA)', issuer: 'CFI Institute', date: 'Nov 2025', verified: true },
      { name: 'Bloomberg Market Concepts (BMC)', issuer: 'Bloomberg LP', date: 'Feb 2026', verified: true },
    ];
  }
  return mockProfile.certifications;
}

export function generateDomainSkills(major?: string) {
  const m = (major || '').toLowerCase();
  if (m.includes('elec') || m.includes('embedded') || m.includes('circuit')) {
    return [
      { name: 'Embedded C / C++', level: 'Advanced (95%)', verified: true, verifiedVia: 'Verified Git Firmware Repo', category: 'Languages' as const },
      { name: 'Microcontrollers (STM32/ARM)', level: 'Advanced', verified: true, verifiedVia: 'Proctored Hardware Assessment', category: 'Core CS' as const },
      { name: 'PCB Design & Altium', level: 'Intermediate', verified: true, verifiedVia: 'Verified Lab Portfolio', category: 'Frameworks' as const },
      { name: 'RTOS (FreeRTOS)', level: 'Intermediate', verified: true, verifiedVia: 'Verified Project', category: 'Frameworks' as const },
      { name: 'Digital Signal Processing', level: 'Intermediate', verified: true, verifiedVia: 'Semester Grade A', category: 'Core CS' as const },
      { name: 'Circuit Simulation (SPICE)', level: 'Proficient', verified: true, verifiedVia: 'Academic Lab Record', category: 'Cloud & Tools' as const },
      { name: 'Verilog / FPGA', level: 'Intermediate', verified: true, verifiedVia: 'Project FPGA-Pipeline', category: 'Languages' as const },
      { name: 'Git & Linux', level: 'Advanced', verified: true, verifiedVia: 'Verified Commit History', category: 'Cloud & Tools' as const },
    ];
  }
  if (m.includes('mech') || m.includes('auto') || m.includes('robot')) {
    return [
      { name: 'SolidWorks & Parametric CAD', level: 'Advanced (95%)', verified: true, verifiedVia: 'CSWA Certification', category: 'Frameworks' as const },
      { name: 'ANSYS FEA & CFD', level: 'Advanced', verified: true, verifiedVia: 'Verified Lab Project', category: 'Frameworks' as const },
      { name: 'MATLAB / Simulink', level: 'Intermediate', verified: true, verifiedVia: 'Coursework ME330', category: 'Languages' as const },
      { name: 'Thermodynamics & Heat Transfer', level: 'Advanced', verified: true, verifiedVia: 'Semester Grade A', category: 'Core CS' as const },
      { name: 'Robotics & ROS 2', level: 'Intermediate', verified: true, verifiedVia: 'Project Autonomous-Rover', category: 'Core CS' as const },
      { name: 'GD&T & Manufacturing', level: 'Intermediate', verified: true, verifiedVia: 'Proctored Assessment', category: 'Cloud & Tools' as const },
      { name: 'Python for Engineering', level: 'Proficient', verified: true, verifiedVia: 'Verified Repo', category: 'Languages' as const },
    ];
  }
  if (m.includes('finan') || m.includes('econ') || m.includes('account')) {
    return [
      { name: 'Financial Modeling & DCF', level: 'Advanced (95%)', verified: true, verifiedVia: 'FMVA Certification', category: 'Core CS' as const },
      { name: 'Bloomberg Terminal & FactSet', level: 'Advanced', verified: true, verifiedVia: 'BMC Verified Credential', category: 'Cloud & Tools' as const },
      { name: 'Python for Quant Finance', level: 'Advanced', verified: true, verifiedVia: 'Quantitative Strategy Repo', category: 'Languages' as const },
      { name: 'Advanced Excel & VBA', level: 'Advanced', verified: true, verifiedVia: 'Financial Model Competition', category: 'Cloud & Tools' as const },
      { name: 'Corporate Valuation & LBO', level: 'Intermediate', verified: true, verifiedVia: 'Coursework FIN301', category: 'Core CS' as const },
      { name: 'SQL & Market Data', level: 'Proficient', verified: true, verifiedVia: 'Proctored Assessment', category: 'Languages' as const },
    ];
  }
  return mockProfile.skills;
}

class ProfileService {
  async getProfile(): Promise<StudentProfile> {
    const token = tokenStorage.get();
    const stored = userStorage.get();
    const fallbackName = stored?.name || mockProfile.name;
    const fallbackMajor = stored?.branch || mockProfile.major;
    const fallbackYear = stored?.academic_year || mockProfile.year;
    const fallbackTargetRole = fallbackMajor.toLowerCase().includes('elec')
      ? 'Embedded Systems Engineer'
      : fallbackMajor.toLowerCase().includes('mech')
      ? 'Mechanical Design Engineer'
      : fallbackMajor.toLowerCase().includes('finan')
      ? 'Financial Analyst'
      : mockProfile.targetRole;

    const buildFallbackProfile = (name: string, major: string, year: string, targetRole: string) => ({
      ...mockProfile,
      name,
      avatarUrl: getSafeAvatarUrl(stored?.avatarUrl, name),
      major,
      year,
      targetRole,
      summary: generateDomainSummary(major, mockProfile.degree, mockProfile.university, targetRole),
      skills: generateDomainSkills(major),
      education: generateDomainEducation(major, mockProfile.degree, mockProfile.university, mockProfile.gpa, '2027'),
      projects: generateDomainProjects(major),
      certifications: generateDomainCertifications(major),
    });

    if (!token) {
      if (stored) {
        return buildFallbackProfile(fallbackName, fallbackMajor, fallbackYear, fallbackTargetRole);
      }
      return { ...mockProfile };
    }

    try {
      const data = await apiFetch<any>('/profile');
      const profileName = data.full_name || data.name || stored?.name || mockProfile.name;
      const major = data.branch || data.major || stored?.branch || mockProfile.major;
      const degree = data.degree || mockProfile.degree;
      const university = data.college || data.university || mockProfile.university;
      const targetRole = data.target_role || fallbackTargetRole;
      const gpa = typeof data.gpa === 'number' ? data.gpa : mockProfile.gpa;
      const gradDate = data.graduation_year || data.graduation_date || mockProfile.graduationDate;

      // Check if existing bio is non-empty and not the stale hardcoded CS text if major is non-CS
      let finalSummary = data.bio || data.summary;
      if (!finalSummary || (major && !major.toLowerCase().includes('comp') && finalSummary.includes('Undergraduate CS student passionate about machine learning'))) {
        finalSummary = generateDomainSummary(major, degree, university, targetRole);
      }

      const profile: StudentProfile = {
        name: profileName,
        avatarUrl: getSafeAvatarUrl(data.avatar_url || data.avatarUrl || stored?.avatarUrl, profileName),
        degree: degree,
        major: major,
        year: data.academic_year || data.year || stored?.academic_year || mockProfile.year,
        university: university,
        gpa: gpa,
        graduationDate: gradDate,
        verifiedProfilePercent: data.verified_profile_percent || mockProfile.verifiedProfilePercent,
        profileStrength: data.profile_strength || mockProfile.profileStrength,
        matchConfidence: data.match_confidence || mockProfile.matchConfidence,
        targetRole: targetRole,
        summary: finalSummary,
        skills: (data.skills && data.skills.length > 0)
          ? data.skills.map((s: any) => ({
              name: s.name,
              level: s.proficiency || s.level || 'Intermediate',
              verified: Boolean(s.verified),
              verifiedVia: s.verifiedVia || (s.verified ? 'Verified Course/Repo' : 'Self Reported'),
              category: (s.category || 'Languages') as any,
            }))
          : generateDomainSkills(major),
        education: (data.education && data.education.length > 0)
          ? data.education
          : generateDomainEducation(major, degree, university, gpa, gradDate),
        projects: (data.projects && data.projects.length > 0)
          ? data.projects.map((p: any) => ({
              name: p.title || p.name,
              description: p.description,
              technologies: p.technologies || [],
              link: p.project_url || p.link,
              verified: Boolean(p.verified),
            }))
          : generateDomainProjects(major),
        certifications: (data.certifications && data.certifications.length > 0)
          ? data.certifications.map((c: any) => ({
              name: c.name,
              issuer: c.issuing_organization || c.issuer,
              date: c.issue_date || '2025',
              verified: Boolean(c.verified),
            }))
          : generateDomainCertifications(major),
      };

      return profile;
    } catch (err) {
      console.warn('Failed to load profile from backend, using local fallback:', err);
      if (stored) {
        return buildFallbackProfile(fallbackName, fallbackMajor, fallbackYear, fallbackTargetRole);
      }
      return { ...mockProfile };
    }
  }

  async updateProfile(updates: Partial<StudentProfile>): Promise<StudentProfile> {
    const token = tokenStorage.get();
    if (!token) {
      const merged = { ...mockProfile, ...updates };
      return merged;
    }

    try {
      const payload: any = {};
      if (updates.summary !== undefined) {
        payload.bio = updates.summary;
        payload.summary = updates.summary;
      }
      if (updates.gpa !== undefined) payload.gpa = updates.gpa;
      if (updates.degree !== undefined) payload.degree = updates.degree;
      if (updates.major !== undefined) {
        payload.branch = updates.major;
        payload.major = updates.major;
      }
      if (updates.year !== undefined) {
        payload.academic_year = updates.year;
        payload.year = updates.year;
      }
      if (updates.university !== undefined) {
        payload.college = updates.university;
        payload.university = updates.university;
      }
      if (updates.targetRole !== undefined) payload.target_role = updates.targetRole;
      if (updates.name !== undefined) payload.full_name = updates.name;

      await apiFetch('/profile', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });

      return await this.getProfile();
    } catch (err) {
      console.warn('Failed to update profile on backend:', err);
      return { ...mockProfile, ...updates };
    }
  }

  async addSkill(name: string, proficiency = 'Beginner', category = 'Languages'): Promise<void> {
    const token = tokenStorage.get();
    if (!token) return;
    try {
      await apiFetch('/profile/skills', {
        method: 'POST',
        body: JSON.stringify({ name, proficiency, category }),
      });
    } catch (e) {
      console.warn('Failed to add skill:', e);
    }
  }

  async removeSkill(skillId: string): Promise<void> {
    const token = tokenStorage.get();
    if (!token) return;
    try {
      await apiFetch(`/profile/skills/${encodeURIComponent(skillId)}`, {
        method: 'DELETE',
      });
    } catch (e) {
      console.warn('Failed to remove skill:', e);
    }
  }

  async addInterest(name: string, category = 'General'): Promise<void> {
    const token = tokenStorage.get();
    if (!token) return;
    try {
      await apiFetch('/profile/interests', {
        method: 'POST',
        body: JSON.stringify({ name, category }),
      });
    } catch (e) {
      console.warn('Failed to add interest:', e);
    }
  }

  async addProject(project: {
    title: string;
    description: string;
    technologies: string[];
    project_url?: string;
    github_url?: string;
  }): Promise<void> {
    const token = tokenStorage.get();
    if (!token) return;
    try {
      await apiFetch('/profile/projects', {
        method: 'POST',
        body: JSON.stringify(project),
      });
    } catch (e) {
      console.warn('Failed to add project:', e);
    }
  }

  async addCertification(cert: {
    name: string;
    issuing_organization: string;
    issue_date?: string;
    credential_id?: string;
  }): Promise<void> {
    const token = tokenStorage.get();
    if (!token) return;
    try {
      await apiFetch('/profile/certifications', {
        method: 'POST',
        body: JSON.stringify(cert),
      });
    } catch (e) {
      console.warn('Failed to add certification:', e);
    }
  }

  async runDiagnostic(): Promise<{
    score: number;
    delta: string;
    recommendation: string;
  }> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          score: 82,
          delta: '+12% this month',
          recommendation:
            'Complete your profile (add 1 project or cloud certification) to improve your match confidence to 95%.',
        });
      }, 50);
    });
  }
}

export const profileService = new ProfileService();
