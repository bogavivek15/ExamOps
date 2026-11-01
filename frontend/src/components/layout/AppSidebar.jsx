import React from 'react';
import { NavLink } from 'react-router-dom';
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
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_GROUPS = [
  {
    title: 'Operations',
    items: [
      { to: '/', label: 'Overview', icon: LayoutDashboard },
      { to: '/scheduling', label: 'Scheduling Workspace', icon: CalendarDays },
      { to: '/exceptions', label: 'Exception Center', icon: AlertTriangle },
    ],
  },
  {
    title: 'Academic Master',
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
    title: 'Governance',
    items: [
      { to: '/analytics', label: 'Analytics & Reports', icon: BarChart3 },
      { to: '/audit', label: 'Audit & Activity', icon: ShieldCheck },
      { to: '/admin', label: 'Administration', icon: Settings },
    ],
  },
];

export default function AppSidebar({ collapsed, onToggle }) {
  const { currentRole, availableRoles } = useAuth();
  const roleObj = availableRoles.find((r) => r.id === currentRole) || availableRoles[0];

  return (
    <aside
      className={`h-screen bg-brand-sidebar border-r border-brand-border flex flex-col justify-between transition-all duration-300 z-30 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-4 border-b border-brand-border">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-accent to-emerald-600 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-brand-accent/20 shrink-0">
              <Layers size={20} />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-sm tracking-wider text-brand-text flex items-center gap-1.5">
                  ExamOps
                  <span className="text-[10px] px-1.5 py-0.2 bg-brand-accent/10 text-brand-accent rounded font-mono font-normal">
                    v1.0
                  </span>
                </span>
                <span className="text-[10px] text-brand-muted tracking-tight truncate">
                  Intelligent Operations
                </span>
              </div>
            )}
          </div>
          <button
            onClick={onToggle}
            className="p-1 rounded text-brand-muted hover:text-brand-text hover:bg-brand-elevated transition-colors"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Navigation Groups */}
        <div className="p-3 space-y-6 overflow-y-auto max-h-[calc(100vh-140px)]">
          {NAV_GROUPS.map((group) => (
            <div key={group.title} className="space-y-1">
              {!collapsed && (
                <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
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
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors relative ${
                        isActive
                          ? 'bg-brand-elevated text-brand-accent border-l-2 border-brand-accent font-semibold'
                          : 'text-brand-muted hover:text-brand-text hover:bg-brand-surface'
                      } ${collapsed ? 'justify-center px-0' : ''}`
                    }
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon size={16} className="shrink-0" />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Role Context Indicator Footer */}
      <div className="p-3 border-t border-brand-border bg-brand-sidebar/80">
        {!collapsed ? (
          <div className="flex flex-col gap-1 text-[11px]">
            <span className="text-slate-500 uppercase tracking-wider text-[9px] font-semibold">
              Current Perspective
            </span>
            <div
              className={`px-2 py-1 rounded text-[11px] font-medium border ${roleObj.badge} truncate`}
            >
              {roleObj.label}
            </div>
          </div>
        ) : (
          <div className="flex justify-center" title={`Active: ${roleObj.label}`}>
            <span className="w-2.5 h-2.5 rounded-full bg-brand-accent animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
}

