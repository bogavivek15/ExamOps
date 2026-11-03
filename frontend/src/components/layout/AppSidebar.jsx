import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarDays,
  AlertTriangle,
  GraduationCap,
  Users,
  BookOpen,
  DoorOpen,
  UserCheck,
  HeartHandshake,
  BarChart3,
  ShieldCheck,
  Settings,
  ChevronLeft,
  ChevronRight,
  X,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_GROUPS = [
  {
    title: 'Operations',
    items: [
      { to: '/', label: 'Overview', icon: LayoutDashboard },
      { to: '/scheduling', label: 'Scheduling Workspace', icon: CalendarDays },
      { to: '/exceptions', label: 'Issue Center', icon: AlertTriangle },
    ],
  },
  {
    title: 'Academic Records',
    items: [
      { to: '/exams', label: 'Examinations', icon: GraduationCap },
      { to: '/students', label: 'Students', icon: Users },
      { to: '/courses', label: 'Courses & Enrollments', icon: BookOpen },
    ],
  },
  {
    title: 'Resources',
    items: [
      { to: '/rooms', label: 'Rooms & Venues', icon: DoorOpen },
      { to: '/invigilators', label: 'Invigilators', icon: UserCheck },
      { to: '/accommodations', label: 'Accommodations', icon: HeartHandshake },
    ],
  },
  {
    title: 'Reports & Governance',
    items: [
      { to: '/analytics', label: 'Analytics & Reports', icon: BarChart3 },
      { to: '/audit', label: 'Audit & Activity', icon: ShieldCheck },
      { to: '/admin', label: 'Administration', icon: Settings },
    ],
  },
];

const ROLE_PERMITTED_ROUTES = {
  LEARNER: ['/', '/exams', '/courses', '/accommodations', '/students'],
  INSTRUCTOR: ['/', '/exams', '/courses', '/rooms', '/invigilators'],
  SUPPORT_STAFF: ['/', '/exceptions', '/rooms', '/invigilators', '/accommodations', '/analytics'],
  ACADEMIC_ADMINISTRATOR: ['/', '/scheduling', '/exceptions', '/exams', '/students', '/courses', '/rooms', '/invigilators', '/accommodations', '/analytics', '/audit', '/admin'],
  PLATFORM_ADMINISTRATOR: ['/', '/scheduling', '/exceptions', '/exams', '/students', '/courses', '/rooms', '/invigilators', '/accommodations', '/analytics', '/audit', '/admin'],
};

export default function AppSidebar({ collapsed, onToggle, mobileOpen, onCloseMobile }) {
  const navigate = useNavigate();
  const { currentRole, availableRoles, logout } = useAuth();
  const roleObj = availableRoles.find((r) => r.id === currentRole) || availableRoles[0];

  const handleLogout = async () => {
    if (onCloseMobile) onCloseMobile();
    await logout();
    navigate('/login', { replace: true });
  };

  const permittedRoutes = ROLE_PERMITTED_ROUTES[currentRole] || ROLE_PERMITTED_ROUTES.ACADEMIC_ADMINISTRATOR;
  const visibleGroups = NAV_GROUPS.map((group) => {
    const items = group.items
      .filter((item) => permittedRoutes.includes(item.to))
      .map((item) => {
        if (currentRole === 'LEARNER') {
          if (item.to === '/') return { ...item, label: 'My Timetable' };
          if (item.to === '/students') return { ...item, label: 'My Profile' };
          if (item.to === '/exams') return { ...item, label: 'My Exams' };
          if (item.to === '/courses') return { ...item, label: 'My Courses' };
          if (item.to === '/accommodations') return { ...item, label: 'My Accommodations' };
        }
        return item;
      });
    return { ...group, items };
  }).filter((group) => group.items.length > 0);

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 md:static md:z-30 h-screen bg-brand-sidebar border-r border-brand-border flex flex-col justify-between transition-all duration-300 ${
          mobileOpen ? 'translate-x-0 w-72' : '-translate-x-full md:translate-x-0'
        } ${collapsed ? 'md:w-16' : 'md:w-64'}`}
        aria-label="Main Navigation"
      >
        {/* Brand Header */}
        <div>
          <div className="h-16 flex items-center justify-between px-4 border-b border-brand-border">
            <div className="flex items-center gap-3 overflow-hidden">
              {/* Bespoke ExamOps Icon */}
              <div
                className="w-9 h-9 rounded-[4px] bg-[#141414] border border-white/20 flex items-center justify-center shrink-0 shadow-sm p-1"
                title="ExamOps — Examination Operations & Scheduling Platform"
              >
                <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="7" y="2.5" width="3.5" height="4.5" rx="1.5" fill="#B8EF43" />
                  <rect x="21.5" y="2.5" width="3.5" height="4.5" rx="1.5" fill="#B8EF43" />
                  <rect
                    x="3"
                    y="4.5"
                    width="26"
                    height="24.5"
                    rx="4.5"
                    fill="#141414"
                    stroke="rgba(255, 255, 255, 0.24)"
                    strokeWidth="1.2"
                  />
                  <line x1="3" y1="10.5" x2="29" y2="10.5" stroke="rgba(255, 255, 255, 0.16)" strokeWidth="1" />
                  <rect x="6.5" y="13" width="2.5" height="13" rx="1.25" fill="#FFFFFF" />
                  <rect x="11" y="13" width="9.5" height="3" rx="1.5" fill="#FFFFFF" />
                  <circle cx="23.5" cy="14.5" r="1.5" fill="#FCF7F3" fillOpacity="0.8" />
                  <rect x="11" y="18" width="14" height="3" rx="1.5" fill="#B8EF43" />
                  <circle cx="21.5" cy="19.5" r="0.75" fill="#000000" />
                  <rect x="11" y="23" width="10.5" height="3" rx="1.5" fill="#FFFFFF" fillOpacity="0.85" />
                  <circle cx="24.5" cy="24.5" r="1.5" fill="#FCF7F3" fillOpacity="0.8" />
                </svg>
              </div>

              {(!collapsed || mobileOpen) && (
                <div className="flex flex-col">
                  <span className="font-bold text-sm tracking-wider text-brand-text flex items-center gap-1.5">
                    ExamOps
                    <span className="text-[10px] px-1.5 py-0.5 bg-brand-accent/20 text-brand-accent border border-brand-accent/40 rounded-[2px] font-mono font-medium">
                      v1.0
                    </span>
                  </span>
                  <span className="text-[10px] text-brand-muted tracking-tight truncate uppercase font-semibold">
                    Exam Operations
                  </span>
                </div>
              )}
            </div>

            {/* Desktop Collapse Toggle */}
            <button
              onClick={onToggle}
              className="hidden md:flex p-1.5 rounded-[4px] text-brand-muted hover:text-brand-text hover:bg-brand-elevated border border-transparent hover:border-brand-border transition-colors"
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>

            {/* Mobile Close Button */}
            <button
              onClick={onCloseMobile}
              className="md:hidden p-1.5 rounded-[4px] text-brand-muted hover:text-brand-text hover:bg-brand-elevated border border-brand-border transition-colors"
              aria-label="Close navigation"
            >
              <X size={18} />
            </button>
          </div>

          {/* Navigation Groups */}
          <div className="p-3 space-y-6 overflow-y-auto max-h-[calc(100vh-140px)]">
            {visibleGroups.map((group) => (
              <div key={group.title} className="space-y-1">
                {(!collapsed || mobileOpen) && (
                  <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    {group.title}
                  </div>
                )}
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === '/'}
                      onClick={() => {
                        if (mobileOpen && onCloseMobile) {
                          onCloseMobile();
                        }
                      }}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 rounded-[4px] text-xs font-medium transition-colors relative ${
                          isActive
                            ? 'bg-brand-accent/15 text-brand-accent border-l-2 border-brand-accent font-semibold shadow-sm'
                            : 'text-brand-muted hover:text-white hover:bg-white/5'
                        } ${collapsed && !mobileOpen ? 'justify-center px-0' : ''}`
                      }
                      title={collapsed && !mobileOpen ? item.label : undefined}
                    >
                      <Icon size={16} className="shrink-0" />
                      {(!collapsed || mobileOpen) && <span className="truncate">{item.label}</span>}
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Role Context Indicator Footer */}
        <div className="p-3 border-t border-brand-border bg-brand-sidebar space-y-2">
          {!collapsed || mobileOpen ? (
            <>
              <div className="flex flex-col gap-1 text-[11px]">
                <span className="text-slate-400 uppercase tracking-wider text-[9px] font-semibold">
                  Active User Role
                </span>
                <div
                  className={`px-2.5 py-1 rounded-[4px] text-[11px] font-medium border ${roleObj?.badge || 'border-brand-border'} truncate`}
                >
                  {roleObj?.label || currentRole || 'Academic Administrator'}
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-2.5 py-1.5 rounded-[4px] bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 text-xs font-medium transition-colors"
                title="Sign out of ExamOps"
              >
                <LogOut size={14} className="shrink-0" />
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full flex justify-center p-1.5 rounded-[4px] text-red-300 hover:bg-red-500/20 transition-colors"
              title="Sign Out"
            >
              <LogOut size={16} />
            </button>
          )}
        </div>
      </aside>
    </>
  );
}
