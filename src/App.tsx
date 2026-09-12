import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';

// Public Pages
import { LandingPage } from './pages/public/LandingPage';
import { LoginPage } from './pages/public/LoginPage';
import { RegisterPage } from './pages/public/RegisterPage';
import { OnboardingPage } from './pages/public/OnboardingPage';

// Student Pages
import { DashboardPage } from './pages/student/DashboardPage';
import { DiscoverPage } from './pages/student/DiscoverPage';
import { CategoryOpportunitiesPage } from './pages/student/CategoryOpportunitiesPage';
import { OpportunityDetailPage } from './pages/student/OpportunityDetailPage';
import { SkillGapPage } from './pages/student/SkillGapPage';
import { CareerRoadmapPage } from './pages/student/CareerRoadmapPage';
import { SavedOpportunitiesPage } from './pages/student/SavedOpportunitiesPage';
import { ApplicationTrackerPage } from './pages/student/ApplicationTrackerPage';
import { ProfilePage } from './pages/student/ProfilePage';
import { AIAssistantPage } from './pages/student/AIAssistantPage';
import { SettingsPage } from './pages/student/SettingsPage';

// Admin Pages
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { AdminOpportunitiesPage } from './pages/admin/AdminOpportunitiesPage';
import { AdminStudentsPage } from './pages/admin/AdminStudentsPage';
import { AdminVerificationPage } from './pages/admin/AdminVerificationPage';
import { AdminAnalyticsPage } from './pages/admin/AdminAnalyticsPage';
import { AdminSettingsPage } from './pages/admin/AdminSettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />

        {/* Student & Main Application Routes (wrapped in AppLayout) */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/discover" element={<DiscoverPage />} />

          {/* 7 Dedicated Opportunity Category Hubs */}
          <Route
            path="/internships"
            element={
              <CategoryOpportunitiesPage
                category="internships"
                title="Internships"
                subtitle="Summer, fall, and semester-long technical internships across high-growth startups and Tier-1 tech enterprises."
                icon="work"
              />
            }
          />
          <Route
            path="/hackathons"
            element={
              <CategoryOpportunitiesPage
                category="hackathons"
                title="Hackathons"
                subtitle="Competitive coding sprints, AI hackathons, and global open-source prize challenges."
                icon="code_blocks"
              />
            }
          />
          <Route
            path="/scholarships"
            element={
              <CategoryOpportunitiesPage
                category="scholarships"
                title="Scholarships & Grants"
                subtitle="Merit-based fellowships, tuition support, and research grant awards for undergraduate engineers."
                icon="school"
              />
            }
          />
          <Route
            path="/courses"
            element={
              <CategoryOpportunitiesPage
                category="courses"
                title="Courses & Curriculums"
                subtitle="Industry-verified courses with direct skill badge integration upon completion."
                icon="menu_book"
              />
            }
          />
          <Route
            path="/projects"
            element={
              <CategoryOpportunitiesPage
                category="projects"
                title="Collaborative Projects"
                subtitle="Team-based open source and capstone initiatives to build verified portfolio code."
                icon="terminal"
              />
            }
          />
          <Route
            path="/jobs"
            element={
              <CategoryOpportunitiesPage
                category="jobs"
                title="Early Career Jobs"
                subtitle="Campus placement and graduate engineering roles matching your verified credentials."
                icon="business_center"
              />
            }
          />
          <Route
            path="/skill-opportunities"
            element={
              <CategoryOpportunitiesPage
                category="skill-opportunities"
                title="Skill Opportunities"
                subtitle="Sponsored apprenticeship programs, cloud certification vouchers, and guided labs."
                icon="bolt"
              />
            }
          />

          {/* Detailed Opportunity & Match Explanation */}
          <Route path="/opportunity/:id" element={<OpportunityDetailPage />} />

          {/* Secondary Features */}
          <Route path="/skill-gap-analysis" element={<SkillGapPage />} />
          <Route path="/skill-gap" element={<Navigate to="/skill-gap-analysis" replace />} />
          <Route path="/career-roadmap" element={<CareerRoadmapPage />} />
          <Route path="/saved" element={<SavedOpportunitiesPage />} />
          <Route path="/applications" element={<ApplicationTrackerPage />} />

          {/* System & Profile */}
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/ai-assistant" element={<AIAssistantPage />} />
          <Route path="/settings" element={<SettingsPage />} />

          {/* Admin Portal Views */}
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/opportunities" element={<AdminOpportunitiesPage />} />
          <Route path="/admin/students" element={<AdminStudentsPage />} />
          <Route path="/admin/verification" element={<AdminVerificationPage />} />
          <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
          <Route path="/admin/settings" element={<AdminSettingsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
