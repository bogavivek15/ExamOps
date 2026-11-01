import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Shield, CheckCircle2, ChevronDown, User, Calendar, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const ROUTE_TITLES = {
  '/': 'Overview Dashboard',
  '/scheduling': 'Examination Scheduling Operations Workspace',
  '/exceptions': 'Exception & Conflict Resolution Center',
  '/exams': 'Examination Directory & Course Requirements',
  '/students': 'Student Registry & Exam Registrations',
  '/courses': 'Academic Courses & Student Enrollments',
  '/rooms': 'Venues, Capacities & Equipment Inventory',
  '/invigilators': 'Invigilators & Staffing Schedules',
  '/accommodations': 'Student Accommodations & Special Needs',
  '/analytics': 'Operational Analytics & Reconciliation Audit',
  '/audit': 'Governance, Traceability & Audit Logs',
  '/admin': 'Institutional Configuration & Access Control',
};

export default function TopNavigation() {
  const location = useLocation();
  const { currentRole, switchRole, availableRoles, currentUser } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const title = ROUTE_TITLES[location.pathname] || 'Operational Operations';

  return (
    <header className="h-16 border-b border-brand-border bg-brand-surface/80 backdrop-blur-md px-6 flex items-center justify-between z-20">
      {/* Page Context / Title */}
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-sm font-bold text-brand-text tracking-wide">{title}</h1>
          <div className="flex items-center gap-2 text-[11px] text-brand-muted mt-0.5">
            <span className="flex items-center gap-1 text-slate-400">
              <Calendar size={12} className="text-brand-accent" />
              Fall 2026 (TERM-2026-02)
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2 size={12} /> System Online
            </span>
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-brand-elevated border border-brand-border hover:border-brand-accent/50 text-xs text-brand-text transition-colors"
          >
            <Shield size={14} className="text-brand-accent" />
            <span className="font-medium text-[11px]">Role:</span>
            <span className="font-semibold text-brand-accent text-[11px]">
              {availableRoles.find((r) => r.id === currentRole)?.label || currentRole}
            </span>
            <ChevronDown size={14} className="text-brand-muted" />
          </button>

          {roleDropdownOpen && (
            <div
              className="absolute right-0 mt-2 w-56 bg-brand-elevated border border-brand-border rounded-lg shadow-xl py-1 z-50 text-xs"
              onMouseLeave={() => setRoleDropdownOpen(false)}
            >
              <div className="px-3 py-1.5 border-b border-brand-border text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                Simulate Perspective
              </div>
              {availableRoles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => {
                    switchRole(role.id);
                    setRoleDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-brand-surface transition-colors ${
                    currentRole === role.id ? 'text-brand-accent font-semibold bg-brand-surface/40' : 'text-slate-300'
                  }`}
                >
                  <span>{role.label}</span>
                  {currentRole === role.id && <span className="w-1.5 h-1.5 rounded-full bg-brand-accent" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Identity Pill */}
        <div className="flex items-center gap-2 pl-3 border-l border-brand-border text-xs">
          <div className="w-8 h-8 rounded-full bg-brand-elevated border border-brand-border flex items-center justify-center text-brand-accent font-semibold">
            <User size={15} />
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="font-medium text-brand-text text-xs leading-none truncate">
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

