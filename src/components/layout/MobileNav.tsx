import React from 'react';
import { NavLink } from 'react-router-dom';

export const MobileNav: React.FC = () => {
  const items = [
    { to: '/dashboard', label: 'Home', icon: 'dashboard' },
    { to: '/discover', label: 'Discover', icon: 'explore' },
    { to: '/skill-gap-analysis', label: 'Skill Gap', icon: 'tune' },
    { to: '/career-roadmap', label: 'Roadmap', icon: 'route' },
    { to: '/applications', label: 'Applications', icon: 'fact_check' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-surface-container-lowest border-t border-outline-variant/30 z-40 flex lg:hidden items-center justify-around px-space-xs">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center w-14 h-12 rounded-xl text-label-xs transition-colors ${
              isActive ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-on-surface'
            }`
          }
        >
          <span className="material-symbols-outlined text-[22px]">{item.icon}</span>
          <span className="text-[10px] mt-0.5">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
};
