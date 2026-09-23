export type OpportunityCategory =
  | 'internships'
  | 'hackathons'
  | 'scholarships'
  | 'courses'
  | 'projects'
  | 'jobs'
  | 'skill-opportunities';

export type WorkMode = 'Remote' | 'Hybrid' | 'On-site' | 'Online' | 'Flexible / Remote';

export type EligibilityStatus = 'Eligible' | 'Partially Eligible' | 'Not Eligible';

export interface MatchBreakdown {
  skillsScore: number; // out of 40
  skillsTotal: number; // 40
  educationScore: number; // out of 20
  educationTotal: number; // 20
  interestsScore: number; // out of 20
  interestsTotal: number; // 20
  experienceScore: number; // out of 20
  experienceTotal: number; // 20
  skillsFitPercent?: number;
  academicCriteriaPercent?: number;
  experienceLevelPercent?: number;
}

export interface PipelineStage {
  step: number;
  name: string;
  description: string;
  active?: boolean;
  completed?: boolean;
}

export interface SkillRequirement {
  name: string;
  level: 'Basic' | 'Intermediate' | 'Advanced' | 'Essential';
  matched: boolean;
  gap?: boolean;
  verificationSource?: string;
}

export interface Opportunity {
  id: string;
  title: string;
  organization: string;
  organizationLogoText: string;
  organizationSubtext?: string;
  category: OpportunityCategory;
  categoryLabel: string;
  domain: string;
  location: string;
  mode: WorkMode;
  compensation?: string;
  deadline: string;
  deadlineDaysRemaining?: number;
  postedAgo: string;
  duration?: string;
  cohortSize?: string;
  description: string;
  keyResponsibilities: string[];
  requirements: {
    technicalSkills: SkillRequirement[];
    academicCriteria: string[];
    experienceCriteria?: string[];
  };
  stages?: PipelineStage[];
  matchScore: number; // 0 - 100
  matchBreakdown: MatchBreakdown;
  matchedSkills: string[];
  missingSkills: string[];
  verified: boolean;
  eligibilityStatus: EligibilityStatus;
  eligibilityNote: string;
  requiredSkills?: string[];
  preferredSkills?: string[];
  eligibilityRequirements?: string;
  degreeRequirements?: string[];
  branchRequirements?: string[];
  academicYearRequirements?: string[];
  experienceRequirements?: string;
  applicationUrl?: string;
  status?: string;
  verifiedBy?: string;
  featured?: boolean;
  imageBanner?: string;
}

export interface SkillDetail {
  name: string;
  level: string;
  description: string;
  verificationNote: string;
  progressPercent?: number;
  rolesDemandPercent?: number;
  priority?: 'High' | 'Medium' | 'Low';
  learningUrl?: string;
}

export interface EmployerBenchmark {
  company: string;
  tier: string;
  role: string;
  matchScore: number;
  statusNote: string;
  isStrongFit?: boolean;
}

export interface TargetRoleGapData {
  roleId: string;
  roleTitle: string;
  readinessScore: number; // e.g. 78%
  estimatedWeeksToClose: string;
  competenciesMet: number;
  competenciesTotal: number;
  mastered: SkillDetail[];
  developing: SkillDetail[];
  criticalGaps: SkillDetail[];
  employerBenchmarks: EmployerBenchmark[];
}

export interface RoadmapStep {
  id: string;
  stepNumber: number;
  title: string;
  status: 'completed' | 'current' | 'upcoming';
  statusLabel: string;
  description: string;
  tag: string;
  meta: string;
  badge?: string;
}

export interface GapClosingResource {
  id: string;
  title: string;
  provider: string;
  type: 'Course' | 'Project' | 'Certification';
  addressesGap: string;
  duration: string;
  impactScore: string;
  description: string;
  perks: string;
  imageUrl: string;
}

export interface StatusHistoryEntry {
  status: string;
  stage?: string;
  timestamp: string;
  notes?: string;
}

export interface Application {
  id: string;
  opportunityId: string;
  opportunityTitle: string;
  organization: string;
  category: OpportunityCategory;
  appliedDate: string;
  status:
    | 'SAVED'
    | 'PLANNING'
    | 'DOING'
    | 'PENDING'
    | 'APPLIED'
    | 'SHORTLISTED'
    | 'INTERVIEW'
    | 'SELECTED'
    | 'COMPLETED'
    | 'NOT_COMPLETED'
    | 'ISSUED'
    | 'REJECTED'
    | 'Applied'
    | 'In Review'
    | 'Technical Assessment'
    | 'Interviewing'
    | 'Offered'
    | 'Rejected';
  statusColor?: string;
  currentStage: string;
  nextDeadline?: string;
  matchScore: number;
  notes?: string;
  statusHistory?: StatusHistoryEntry[];
}

export interface StudentProfile {
  name: string;
  avatarUrl: string;
  degree: string;
  major: string;
  year: string;
  university: string;
  gpa: number;
  graduationDate: string;
  verifiedProfilePercent: number;
  profileStrength: number;
  matchConfidence: number;
  targetRole: string;
  summary: string;
  skills: {
    name: string;
    level: string;
    verified: boolean;
    verifiedVia: string;
    category: 'Languages' | 'Frameworks' | 'Cloud & Tools' | 'Core CS';
  }[];
  education: {
    institution: string;
    degree: string;
    period: string;
    gpa: string;
    courses: string[];
  }[];
  projects: {
    name: string;
    description: string;
    technologies: string[];
    link?: string;
    verified: boolean;
  }[];
  certifications: {
    name: string;
    issuer: string;
    date: string;
    verified: boolean;
  }[];
}

export interface NotificationItem {
  id: string;
  title: string;
  description: string;
  timeAgo: string;
  read: boolean;
  type: 'match' | 'deadline' | 'application' | 'system';
  link?: string;
}
