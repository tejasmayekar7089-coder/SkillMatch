import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { AdminSidebar } from './AdminSidebar';
import { Header } from './Header';
import { MobileNav } from './MobileNav';

export const AppLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        {isAdminRoute ? <AdminSidebar /> : <Sidebar />}
      </div>

      {/* Mobile Drawer Sidebar */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-on-surface/40 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          ></div>
          <div className="relative w-64 h-full shadow-2xl">
            {isAdminRoute ? (
              <AdminSidebar onCloseMobile={() => setMobileMenuOpen(false)} />
            ) : (
              <Sidebar onCloseMobile={() => setMobileMenuOpen(false)} />
            )}
          </div>
        </div>
      )}

      {/* Main Content Area with Fixed Header */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <Header onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)} />

        <main className="w-full pt-16 pb-20 lg:pb-12 min-h-screen bg-background px-space-md sm:px-space-lg lg:px-space-xl py-space-lg lg:py-space-xl">
          <Outlet />
        </main>

        {/* Mobile Bottom Navigation */}
        <MobileNav />
      </div>
    </div>
  );
};
