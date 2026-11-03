import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, CheckCircle2, User, Calendar, Menu, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const ROUTE_TITLES = {
  '/': 'Overview Dashboard',
  '/scheduling': 'Scheduling Operations Center',
  '/exceptions': 'Issue & Conflict Center',
  '/exams': 'Examination Directory',
  '/students': 'Student Registry & Timetables',
  '/courses': 'Courses & Enrollments',
  '/rooms': 'Rooms & Facilities',
  '/invigilators': 'Invigilators & Staff Schedules',
  '/accommodations': 'Student Accommodations & Support',
  '/analytics': 'Analytics & Reports',
  '/audit': 'Activity History & Audit Log',
  '/admin': 'Administration & Settings',
};

export default function TopNavigation({ onToggleMobileMenu }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentRole, availableRoles, currentUser, logout } = useAuth();

  const title = ROUTE_TITLES[location.pathname] || 'Exam Operations';
  const roleLabel = availableRoles.find((r) => r.id === currentRole)?.label || currentRole || 'Academic Administrator';

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="h-16 border-b border-brand-border bg-brand-surface/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between z-20">
      {/* Page Context / Mobile Hamburger & Title */}
      <div className="flex items-center gap-2 sm:gap-4 min-w-0">
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden p-2 rounded-[4px] text-brand-muted hover:text-white hover:bg-brand-elevated border border-brand-border transition-colors shrink-0"
          aria-label="Open menu"
        >
          <Menu size={18} />
        </button>

        <div className="truncate">
          <h1 className="text-xs sm:text-sm font-bold text-white tracking-wide truncate">{title}</h1>
          <div className="flex items-center gap-2 text-[11px] text-brand-muted mt-0.5 truncate">
            <span className="hidden xs:flex items-center gap-1 text-slate-300">
              <Calendar size={12} className="text-brand-accent" />
              Fall 2026 Term
            </span>
            <span className="hidden xs:inline">•</span>
            <span className="flex items-center gap-1 text-brand-accent font-medium text-[10px] sm:text-[11px]">
              <CheckCircle2 size={12} /> System Online
            </span>
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-4 shrink-0">
        {/* Verified Database Role Badge */}
        <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-[4px] bg-brand-elevated border border-brand-border text-xs text-white">
          <Shield size={14} className="text-brand-accent shrink-0" />
          <span className="hidden sm:inline font-normal text-[11px] text-brand-muted">Role:</span>
          <span className="font-semibold text-brand-accent text-[11px] truncate max-w-[120px] sm:max-w-none">
            {roleLabel}
          </span>
        </div>

        {/* User Identity Pill */}
        <div className="flex items-center gap-2 pl-2 sm:pl-3 border-l border-brand-border text-xs">
          <div
            className="w-8 h-8 rounded-[4px] bg-[#1C1C1C] border border-white/20 flex items-center justify-center text-brand-accent font-semibold shrink-0"
            title={currentUser?.email || 'evaluator@examops.edu'}
          >
            <User size={15} />
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="font-medium text-white text-xs leading-none truncate">
              {currentUser?.display_name || 'Academic Administrator'}
            </span>
            <span className="text-[10px] text-brand-muted leading-tight mt-1 truncate">
              {currentUser?.email || 'evaluator@examops.edu'}
            </span>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-[4px] bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 text-xs font-medium transition-colors"
          title="Sign out of ExamOps"
          aria-label="Sign out"
        >
          <LogOut size={14} className="shrink-0" />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
}
