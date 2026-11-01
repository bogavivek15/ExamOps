import React, { useState, useEffect } from 'react';
import { 
  Settings, Users, Shield, Calendar, Clock, Sliders, 
  CheckCircle2, AlertTriangle, UserCheck, RefreshCw, Key
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function Administration() {
  const { role, switchRole } = useAuth();
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
      setError(err.message || 'Failed to load user profiles');
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
      header: 'Simulate As',
      cell: (row) => (
        <button
          onClick={() => switchRole(row.role_name || row.role)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <UserCheck className="w-3 h-3 text-brand-accent" />
          Assume Role
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-brand-border">
        <div>
          <h1 className="text-xl font-bold text-brand-text tracking-tight flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-brand-accent" />
            Administration & Policy Governance
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Institutional configuration parameters, user role permissions, and academic period rules.
          </p>
        </div>

        {/* Active Role Simulation Indicator */}
        <div className="flex items-center gap-2 bg-brand-elevated border border-brand-border rounded px-3 py-1.5">
          <Key className="w-3.5 h-3.5 text-brand-accent" />
          <span className="text-xs text-brand-muted">Active Role Context:</span>
          <span className="text-xs font-mono font-bold text-brand-accent">{role}</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-brand-border pb-2">
        <button
          onClick={() => setActiveTab('users')}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            activeTab === 'users'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          User Accounts & Access Control
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            activeTab === 'rules'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          Scheduling Rules & Constraints
        </button>
        <button
          onClick={() => setActiveTab('institution')}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            activeTab === 'institution'
              ? 'bg-brand-accent text-brand-bg font-semibold'
              : 'text-brand-muted hover:text-brand-text'
          }`}
        >
          Institutional Parameters
        </button>
      </div>

      {/* Tab 1: Users */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricDisplay
              label="Registered Operators"
              value={profiles.length || '12'}
              subtext="Platform user profiles"
              icon={Users}
            />
            <MetricDisplay
              label="Role Hierarchy"
              value="RBAC Enforced"
              subtext="Row-level security active"
              icon={Shield}
            />
            <MetricDisplay
              label="Session Security"
              value="JWT Bearer"
              subtext="Stateless authorization"
              icon={Key}
            />
            <MetricDisplay
              label="Audit Non-Repudiation"
              value="Synchronous"
              subtext="Logged per mutation"
              icon={CheckCircle2}
            />
          </div>

          {loading ? (
            <LoadingState message="Loading platform users..." />
          ) : error ? (
            <EmptyState
              icon={AlertTriangle}
              title="Error Loading Users"
              description={error}
              actionLabel="Retry"
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
          <div className="bg-brand-surface border border-brand-border rounded-lg p-5 space-y-4">
            <h3 className="text-sm font-bold text-brand-text flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-accent" />
              Hard Constraints (Uncompromising Invariants)
            </h3>
            <p className="text-xs text-brand-muted">
              Any candidate schedule containing a single violation of these constraints will be automatically rejected.
            </p>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">1. Student Conflict Prohibition</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  No individual student can be scheduled for two concurrent examinations at any overlapping minute.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">2. Venue Capacity Strict Bound</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  The count of candidates seated in any examination venue must not exceed its effective exam capacity.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">3. Invigilator Non-Overlapping Bound</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  No invigilator may be assigned to more than one simultaneous examination room.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">4. Operating Hours & Availability</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  All examination sessions must fall strictly within verified room availability windows.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">5. Accessibility Accommodations</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Candidate accessibility needs (extra time, step-free access) must be fully honored without exception.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-brand-surface border border-brand-border rounded-lg p-5 space-y-4">
            <h3 className="text-sm font-bold text-brand-text flex items-center gap-2">
              <Sliders className="w-4 h-4 text-brand-accent" />
              Soft Optimization Heuristics
            </h3>
            <p className="text-xs text-brand-muted">
              Objective weights applied during slot and room selection to optimize the candidate experience.
            </p>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">Student Exam Spread Penalty</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Penalizes scheduling consecutive examinations for the same student on identical calendar days.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">Venue Fill Density Maximization</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Selects venues that minimize unused desks while avoiding overflow.
                </p>
              </div>

              <div className="p-3 bg-brand-elevated border border-brand-border rounded">
                <span className="font-semibold text-brand-text block">Invigilator Workload Balance</span>
                <p className="text-brand-muted text-[11px] mt-0.5">
                  Evenly distributes proctoring duties across qualified staff members.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Institutional Parameters */}
      {activeTab === 'institution' && (
        <div className="bg-brand-surface border border-brand-border rounded-lg p-6 space-y-6">
          <div className="border-b border-brand-border pb-4">
            <h3 className="text-sm font-bold text-brand-text">Active Academic Period Configuration</h3>
            <p className="text-xs text-brand-muted mt-1">Fall 2026 Examination Period parameters</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Academic Period Code</label>
              <input
                type="text"
                disabled
                value="FALL-2026"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Examination Window</label>
              <input
                type="text"
                disabled
                value="2026-12-01 to 2026-12-14 (14 days)"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Daily Exam Slots</label>
              <input
                type="text"
                disabled
                value="3 slots / day (09:00, 13:00, 16:30)"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Standard Staffing Ratio</label>
              <input
                type="text"
                disabled
                value="1 invigilator per 30 students"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Minimum Inter-Exam Break</label>
              <input
                type="text"
                disabled
                value="30 minutes"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>

            <div className="space-y-1">
              <label className="text-brand-muted block font-medium">Synthetic Generator Seed</label>
              <input
                type="text"
                disabled
                value="20261022 (Fixed Seed)"
                className="w-full bg-brand-elevated border border-brand-border rounded px-3 py-2 text-brand-text font-mono"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

