import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { authService, AuthUser } from '../../services/authService';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());

  useEffect(() => {
    authService.fetchCurrentUser().then((user) => {
      if (user) setCurrentUser(user);
    });
  }, []);

  const mainNavItems = [
    { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { to: '/discover', label: 'Discover', icon: 'explore' },
    { to: '/internships', label: 'Internships', icon: 'work' },
    { to: '/hackathons', label: 'Hackathons', icon: 'code_blocks' },
    { to: '/scholarships', label: 'Scholarships', icon: 'school' },
    { to: '/courses', label: 'Courses', icon: 'menu_book' },
    { to: '/projects', label: 'Projects', icon: 'terminal' },
    { to: '/jobs', label: 'Jobs', icon: 'business_center' },
    { to: '/skill-opportunities', label: 'Skill Opportunities', icon: 'bolt' },
  ];

  const secondaryNavItems = [
    { to: '/skill-gap-analysis', label: 'Skill Gap Analysis', icon: 'tune' },
    { to: '/career-roadmap', label: 'Career Roadmap', icon: 'route' },
    { to: '/saved', label: 'Saved', icon: 'bookmark' },
    { to: '/applications', label: 'Applications', icon: 'fact_check' },
  ];

  const systemNavItems = [
    { to: '/ai-assistant', label: 'AI Assistant', icon: 'smart_toy' },
    ...(currentUser?.role === 'admin'
      ? [{ to: '/admin', label: 'Admin Portal', icon: 'shield_person' }]
      : []),
    { to: '/profile', label: 'Profile', icon: 'person' },
    { to: '/settings', label: 'Settings', icon: 'settings' },
  ];

  const renderNavLink = (item: { to: string; label: string; icon: string }) => (
    <NavLink
      key={item.to}
      to={item.to}
      onClick={onCloseMobile}
      className={({ isActive }) =>
        `flex items-center gap-space-sm px-space-sm py-space-xs rounded-xl font-label-md text-label-md transition-colors ${
          isActive
            ? 'bg-surface-container text-primary font-medium'
            : 'text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface'
        }`
      }
    >
      <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
      <span>{item.label}</span>
    </NavLink>
  );

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface-container-lowest border-r border-outline-variant/30 z-50 flex flex-col justify-between overflow-y-auto">
      <div className="flex flex-col">
        {/* Logo and Brand Header */}
        <Link
          to="/dashboard"
          className="h-16 px-space-lg flex items-center gap-space-sm border-b border-outline-variant/20 flex-shrink-0"
        >
          <img
            alt="SkillMatch Logo"
            className="h-8 w-auto object-contain"
            src="/assets/logo.svg"
          />
        </Link>

        {/* Navigation Sections */}
        <nav className="px-space-md py-space-base space-y-space-xl">
          {/* Main */}
          <div className="space-y-space-2xs">
            <p className="px-space-sm pb-space-xs font-label-xs text-label-xs uppercase tracking-wider text-outline">
              Main
            </p>
            {mainNavItems.map(renderNavLink)}
          </div>

          {/* Secondary */}
          <div className="space-y-space-2xs">
            <p className="px-space-sm pb-space-xs font-label-xs text-label-xs uppercase tracking-wider text-outline">
              Secondary
            </p>
            {secondaryNavItems.map(renderNavLink)}
          </div>

          {/* System */}
          <div className="space-y-space-2xs">
            <p className="px-space-sm pb-space-xs font-label-xs text-label-xs uppercase tracking-wider text-outline">
              System
            </p>
            {systemNavItems.map(renderNavLink)}
          </div>
        </nav>
      </div>

      {/* Verified Profile Status Footer */}
      <div className="p-space-base border-t border-outline-variant/20">
        <Link
          to="/profile"
          className="bg-surface-container-low rounded-xl p-space-sm flex items-center justify-between hover:bg-surface-container transition-colors block"
        >
          <div className="flex items-center gap-space-xs">
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            <span className="font-label-xs text-label-xs text-on-surface-variant">Verified Profile</span>
          </div>
          <span className="font-label-xs text-label-xs text-primary font-medium">94%</span>
        </Link>
      </div>
    </aside>
  );
};
