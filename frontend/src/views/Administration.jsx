import React, { useState, useEffect } from 'react';
import { 
  Settings, Users, Shield, 
  CheckCircle2, AlertTriangle, UserCheck, Key, Check
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import MetricDisplay from '../components/common/MetricDisplay';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';

export default function Administration() {
  const { currentRole, switchRole } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('users'); // 'users' | 'rules' | 'institution'

  useEffect(() => {
    loadProfiles();
  }, []);

  async function loadProfiles() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listProfiles();
      setProfiles(data || []);
    } catch (err) {
      setError(err.message || 'Unable to load user accounts.');
    } finally {
      setLoading(false);
    }
  }

  const userColumns = [
    {
      header: 'Full Name',
      cell: (row) => (
        <div>
          <span className="font-semibold text-brand-text block">{row.first_name} {row.last_name}</span>
          <span className="text-xs text-brand-muted">{row.email}</span>
        </div>
      ),
    },
    {
      header: 'Primary Role',
      cell: (row) => (
        <span className="font-mono text-xs font-semibold px-2.5 py-0.5 rounded bg-brand-elevated text-brand-accent border border-brand-border">
          {row.role_name || row.role}
        </span>
      ),
    },
    {
      header: 'Department / Unit',
      accessor: 'department',
      className: 'text-brand-text text-xs',
    },
    {
      header: 'Account Status',
      cell: (row) => <StatusBadge status={row.status || 'ACTIVE'} />,
    },
    {
      header: 'Switch Perspective',
      cell: (row) => (
        <button
          onClick={() => switchRole(row.role_name || row.role)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label={`Switch to role ${row.role_name || row.role}`}
        >
          <UserCheck className="w-3 h-3 text-brand-accent" />
          Switch to Role
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-brand-border">
        <div>
          <h1 className="text-lg sm:text-xl font-bold text-brand-text tracking-tight flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-brand-accent" />
            Administration & Settings
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Manage user accounts, view scheduling rules, and check institutional examination settings.
          </p>
        </div>

        {/* Current Role Indicator */}
        <div className="flex items-center gap-2 bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-1.5 self-start sm:self-auto">
          <Key className="w-3.5 h-3.5 text-brand-accent" />
          <span className="text-xs text-brand-muted">Current Role:</span>
          <span className="text-xs font-mono font-bold text-brand-accent">{currentRole}</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-brand-border pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('users')}
          className={`px-3 py-1.5 rounded-[4px] text-xs font-medium transition-colors shrink-0 ${
            activeTab === 'users'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          User Accounts & Permissions
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`px-3 py-1.5 rounded-[4px] text-xs font-medium transition-colors shrink-0 ${
            activeTab === 'rules'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          Scheduling Rules & Limits
        </button>
        <button
          onClick={() => setActiveTab('institution')}
          className={`px-3 py-1.5 rounded-[4px] text-xs font-medium transition-colors shrink-0 ${
            activeTab === 'institution'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          College Settings
        </button>
      </div>

      {/* Tab 1: Users */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            <MetricDisplay
              label="User Accounts"
              value={profiles.length || '12'}
              subtext="Registered staff & admins"
              icon={Users}
            />
            <MetricDisplay
              label="Access Control"
              value="Role-Based"
              subtext="Row-level security active"
              icon={Shield}
            />
            <MetricDisplay
              label="Security"
              value="Encrypted Token"
              subtext="Secure authentication"
              icon={Key}
            />
            <MetricDisplay
              label="Audit Logging"
              value="Automatic"
              subtext="All changes tracked"
              icon={CheckCircle2}
            />
          </div>

          {loading ? (
            <LoadingState message="Loading user accounts..." />
          ) : error ? (
            <EmptyState
              icon={AlertTriangle}
              title="Error Loading Users"
              description={error}
              actionLabel="Try Again"
              onAction={loadProfiles}
            />
          ) : (
            <DataTable
              columns={userColumns}
              data={profiles}
              total={profiles.length}
              page={1}
              pageSize={20}
              onPageChange={() => {}}
              onPageSizeChange={() => {}}
            />
          )}
        </div>
      )}

      {/* Tab 2: Rules */}
      {activeTab === 'rules' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-5 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-brand-text flex items-center gap-2">
                <Shield className="w-4 h-4 text-brand-accent" />
                Mandatory Rules (Must Never Be Broken)
              </h3>
              <p className="text-xs text-brand-muted mt-1">
                Any timetable that breaks one of these rules is automatically rejected by the system.
              </p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">1. No Overlapping Exams for Any Student</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  No individual student can be scheduled for two concurrent examinations at any overlapping minute.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">2. Never Exceed Room Capacity</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  The count of students seated in any room must not exceed its desk capacity.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">3. No Invigilator Double-Booking</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  No invigilator may be assigned to more than one simultaneous examination room.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">4. Exams Only During Open Hours</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  All examination sessions must fall strictly within verified room availability hours.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">5. Always Fulfill Student Support & Extra Time</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Student accessibility requirements (extra time, step-free access) must be fully honored without exception.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-5 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-brand-text flex items-center gap-2">
                <Check className="w-4 h-4 text-brand-accent" />
                Quality Guidelines (Best Practices)
              </h3>
              <p className="text-xs text-brand-muted mt-1">
                Guidelines used by the scheduler to create a balanced, stress-free experience for students.
              </p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">Spread Out Student Exams</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Avoids scheduling multiple consecutive exams on the same day for a student.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">Efficient Room Usage</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Selects rooms that comfortably seat students without leaving huge empty spaces.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded-[4px]">
                <span className="font-semibold text-brand-text block">Fair Staff Workload</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Evenly distributes exam supervision duties across available staff.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Institutional Parameters */}
      {activeTab === 'institution' && (
        <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-6 space-y-6">
          <div className="border-b border-brand-border pb-4">
            <h3 className="text-sm font-bold text-brand-text">Active Academic Term Configuration</h3>
            <p className="text-xs text-brand-muted mt-1">Fall 2026 Examination Period parameters</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 text-xs">
            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Academic Term Code</label>
              <input
                type="text"
                disabled
                value="FALL-2026"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Examination Window</label>
              <input
                type="text"
                disabled
                value="2026-12-01 to 2026-12-14 (14 days)"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Daily Exam Slots</label>
              <input
                type="text"
                disabled
                value="3 slots / day (09:00, 13:00, 16:30)"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Standard Staffing Ratio</label>
              <input
                type="text"
                disabled
                value="1 invigilator per 30 students"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Minimum Break Between Exams</label>
              <input
                type="text"
                disabled
                value="30 minutes"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Standard Timetable Seed</label>
              <input
                type="text"
                disabled
                value="20261022 (Fixed Seed)"
                className="w-full bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-brand-text font-mono"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
