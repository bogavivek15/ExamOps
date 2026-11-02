import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Shield, CheckCircle2, ChevronDown, User, Calendar, Menu } from 'lucide-react';
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
  const { currentRole, switchRole, availableRoles, currentUser } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const title = ROUTE_TITLES[location.pathname] || 'Exam Operations';

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
        {/* Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-[4px] bg-brand-elevated border border-brand-border hover:border-brand-accent/50 text-xs text-white transition-colors"
            aria-expanded={roleDropdownOpen}
            aria-label="Select role perspective"
          >
            <Shield size={14} className="text-brand-accent shrink-0" />
            <span className="hidden sm:inline font-normal text-[11px] text-brand-muted">Role:</span>
            <span className="font-semibold text-brand-accent text-[11px] truncate max-w-[90px] sm:max-w-none">
              {availableRoles.find((r) => r.id === currentRole)?.label || currentRole}
            </span>
            <ChevronDown size={14} className="text-brand-muted shrink-0" />
          </button>

          {roleDropdownOpen && (
            <div
              className="absolute right-0 mt-2 w-64 bg-[#1C1C1C] border border-white/20 rounded-[4px] shadow-2xl py-1 z-50 text-xs"
              onMouseLeave={() => setRoleDropdownOpen(false)}
            >
              <div className="px-3 py-1.5 border-b border-white/10 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Preview Role Experience
              </div>
              {availableRoles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => {
                    switchRole(role.id);
                    setRoleDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-white/10 transition-colors ${
                    currentRole === role.id ? 'text-brand-accent font-semibold bg-brand-accent/10' : 'text-slate-300'
                  }`}
                >
                  <span>{role.label}</span>
                  {currentRole === role.id && (
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_6px_#B8EF43]" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Identity Pill */}
        <div className="flex items-center gap-2 pl-2 sm:pl-3 border-l border-brand-border text-xs">
          <div
            className="w-8 h-8 rounded-[4px] bg-[#1C1C1C] border border-white/20 flex items-center justify-center text-brand-accent font-semibold shrink-0"
            title={currentUser?.email || 'admin@examops.edu'}
          >
            <User size={15} />
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="font-medium text-white text-xs leading-none truncate">
              {currentUser?.display_name || 'Academic Administrator'}
            </span>
            <span className="text-[10px] text-brand-muted leading-tight mt-1 truncate">
              {currentUser?.email || 'admin@examops.edu'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
