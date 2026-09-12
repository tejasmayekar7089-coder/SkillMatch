import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { applicationService, NotificationItem } from '../../services/applicationService';
import { authService, AuthUser, getSafeAvatarUrl } from '../../services/authService';
import { profileService } from '../../services/profileService';

interface HeaderProps {
  onToggleMobileMenu?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileMenu }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(authService.getCurrentUser());
  const [profileSubtitle, setProfileSubtitle] = useState<string>('');
  const navigate = useNavigate();
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  const loadNotifications = () => {
    applicationService.getNotifications().then((data) => {
      if (data) setNotifications(data);
    });
  };

  useEffect(() => {
    authService.fetchCurrentUser().then((user) => {
      if (user) {
        setCurrentUser(user);
        if (user.role === 'admin') {
          setProfileSubtitle('Global Talent Operations');
        } else if (user.branch) {
          setProfileSubtitle(`${user.branch}${user.academic_year ? `, ${user.academic_year}` : ''}`);
        }
      }
    });
    profileService.getProfile().then((prof) => {
      if (prof && prof.major) {
        setProfileSubtitle(`${prof.major}${prof.year ? `, ${prof.year}` : ''}`);
      }
    });
    loadNotifications();
  }, [location.pathname]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/discover?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/discover');
    }
  };

  const markAllAsRead = async () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    await applicationService.markAllNotificationsRead();
  };

  const handleNotificationClick = async (n: NotificationItem) => {
    setShowNotifications(false);
    if (!n.read) {
      setNotifications((prev) =>
        prev.map((item) => (item.id === n.id ? { ...item, read: true } : item))
      );
      await applicationService.markNotificationRead(n.id);
    }
  };

  return (
    <header className="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-surface-container-lowest border-b border-outline-variant/30 z-40 px-space-md lg:px-space-xl flex items-center justify-between gap-space-base">
      {/* Mobile Menu Button & Search Form */}
      <div className="flex items-center gap-space-sm flex-1 max-w-xl">
        <button
          onClick={onToggleMobileMenu}
          className="p-space-xs rounded-xl text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface lg:hidden"
          aria-label="Toggle Navigation Menu"
        >
          <span className="material-symbols-outlined text-[24px]">menu</span>
        </button>

        <form onSubmit={handleSearchSubmit} className="relative flex-1 flex items-center">
          <span className="material-symbols-outlined absolute left-space-md text-outline text-[20px]">
            search
          </span>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-10 pl-10 pr-space-base rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-body-sm text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
            placeholder={
              isAdminRoute
                ? "Search active opportunities, candidates, credential audits..."
                : "Search internships, hackathons, scholarships..."
            }
            type="text"
          />
        </form>
      </div>

      {/* Right Cluster: Notifications + Profile */}
      <div className="flex items-center gap-space-sm lg:gap-space-base relative">
        {/* Notifications Button */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="Notifications"
            className="relative p-space-xs rounded-xl text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface transition-colors"
          >
            <span className="material-symbols-outlined text-[22px]">notifications</span>
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 flex items-center justify-center w-4 h-4 rounded-full bg-error text-on-error font-label-xs text-[10px] font-bold">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Popover */}
          {showNotifications && (
            <div className="absolute right-0 top-12 w-80 sm:w-96 bg-surface-container-lowest border border-outline-variant/40 rounded-2xl shadow-xl z-50 p-space-md space-y-space-sm">
              <div className="flex items-center justify-between pb-space-xs border-b border-outline-variant/20">
                <span className="font-headline-sm text-label-md text-on-surface font-semibold">
                  Notifications ({unreadCount} new)
                </span>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="font-label-xs text-primary hover:underline"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="space-y-space-xs max-h-72 overflow-y-auto">
                {notifications.map((n) => (
                  <Link
                    key={n.id}
                    to={n.link || '/dashboard'}
                    onClick={() => handleNotificationClick(n)}
                    className={`p-space-sm rounded-xl block transition-colors ${
                      !n.read ? 'bg-surface-container-low' : 'hover:bg-surface-container-low/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-space-xs">
                      <p className="font-label-sm text-on-surface font-semibold leading-snug">
                        {n.title}
                      </p>
                      <span className="font-label-xs text-outline text-[11px] whitespace-nowrap">
                        {n.timeAgo}
                      </span>
                    </div>
                    <p className="font-body-sm text-label-xs text-secondary mt-0.5">
                      {n.description}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quick Admin Elevation Button (when viewing /admin as student) */}
        {isAdminRoute && currentUser?.role !== 'admin' && (
          <button
            onClick={async () => {
              try {
                await authService.login('admin@skillmatch.edu', 'AdminPassword123!');
                window.location.reload();
              } catch (e: any) {
                alert(e.message || 'Failed to authenticate as Corporate Administrator');
              }
            }}
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all"
            title="Authenticate with Corporate Admin credentials"
          >
            <span className="material-symbols-outlined text-[16px]">verified_user</span>
            <span>Switch to MNC Admin</span>
          </button>
        )}

        <div className="h-8 w-px bg-outline-variant/30 hidden sm:block"></div>

        {/* Profile Pill */}
        <Link
          to="/profile"
          className="flex items-center gap-space-md p-1 rounded-xl hover:bg-surface-container-low transition-colors"
        >
          <div className="text-right hidden sm:block">
            <p className="font-headline-sm text-label-md text-on-surface leading-tight">
              {currentUser?.name || (currentUser?.role === 'admin' ? 'SkillMatch Administrator' : 'Alex Morgan')}
            </p>
            <p className="font-body-sm text-label-xs text-on-surface-variant">
              {currentUser?.role === 'admin'
                ? 'Global Talent Operations'
                : profileSubtitle || (currentUser?.branch ? `${currentUser.branch}${currentUser.academic_year ? `, ${currentUser.academic_year}` : ''}` : 'Engineering Student')}
            </p>
          </div>
          <img
            alt={currentUser?.name || 'Profile'}
            className="w-8 h-8 rounded-full object-cover ring-1 ring-outline-variant/40"
            src={getSafeAvatarUrl(currentUser?.avatarUrl, currentUser?.name || 'Student')}
            onError={(e) => {
              (e.target as HTMLImageElement).src = getSafeAvatarUrl(null, currentUser?.name || 'Student');
            }}
          />
        </Link>
      </div>
    </header>
  );
};
