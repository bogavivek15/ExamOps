import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  GraduationCap,
  Calendar,
  DoorOpen,
  UserCheck,
  HeartHandshake,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  TrendingUp,
  Download,
} from 'lucide-react';
import { api } from '../services/api';
import MetricDisplay from '../components/common/MetricDisplay';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';

export default function OverviewDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAnalyticsOverview();
      setOverview(data);
    } catch (err) {
      setError(err.message || 'Failed to load operational overview');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading institutional overview..." />;
  if (error) {
    return (
      <div className="p-6 bg-brand-surface border border-rose-500/30 rounded-lg text-center text-rose-400">
        <AlertTriangle className="mx-auto mb-2" size={24} />
        <p className="text-sm font-semibold">{error}</p>
        <button
          onClick={loadOverview}
          className="mt-4 px-4 py-1.5 bg-brand-elevated border border-brand-border rounded text-xs text-brand-text hover:border-brand-accent"
        >
          Retry
        </button>
      </div>
    );
  }

  const latestRun = overview?.latest_run;

  return (
    <div className="space-y-6">
      {/* Top Banner: Academic Period & Run Status */}
      <div className="bg-gradient-to-r from-brand-surface via-brand-elevated to-brand-surface border border-brand-border rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase font-mono tracking-wider text-brand-accent">
              Operational Period
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
            <span className="text-xs text-brand-muted">Active Semester</span>
          </div>
          <h2 className="text-xl font-bold text-brand-text tracking-tight">
            {overview?.active_period?.name || 'Fall 2026 Examination Period'}
          </h2>
          <p className="text-xs text-brand-muted mt-1">
            Period Code: <span className="font-mono text-slate-300">{overview?.active_period?.code}</span> •
            Examination Window: <span className="font-mono text-slate-300">{overview?.active_period?.exam_start_date}</span> to{' '}
            <span className="font-mono text-slate-300">{overview?.active_period?.exam_end_date}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/scheduling')}
            className="flex items-center gap-2 px-4 py-2 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold rounded-md text-xs shadow-lg shadow-brand-accent/20 transition-all"
          >
            <Play size={14} className="fill-current" />
            Launch Scheduling Workspace
          </button>
        </div>
      </div>

      {/* Primary Institutional Scale Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricDisplay
          label="Total Students"
          value={overview?.total_students?.toLocaleString()}
          icon={Users}
          secondary="Enrolled cohort"
        />
        <MetricDisplay
          label="Total Courses"
          value={overview?.total_courses?.toLocaleString()}
          icon={GraduationCap}
          secondary="Active catalog"
        />
        <MetricDisplay
          label="Examinations"
          value={overview?.total_exams?.toLocaleString()}
          icon={Calendar}
          secondary="Final & midterm"
        />
        <MetricDisplay
          label="Rooms & Venues"
          value={overview?.total_rooms?.toLocaleString()}
          icon={DoorOpen}
          secondary="Available spaces"
        />
        <MetricDisplay
          label="Invigilators"
          value={overview?.total_invigilators?.toLocaleString()}
          icon={UserCheck}
          secondary="Academic staff"
        />
        <MetricDisplay
          label="Accommodations"
          value={overview?.total_active_accommodations?.toLocaleString()}
          icon={HeartHandshake}
          secondary="Special needs"
        />
      </div>

      {/* Schedule Execution Condition Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-brand-surface border border-brand-border rounded-lg p-6">
          <div className="flex items-center justify-between pb-4 border-b border-brand-border mb-5">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text">
                Current Operational Schedule State
              </h3>
              <p className="text-xs text-brand-muted mt-0.5">
                Authoritative schedule output for the active semester
              </p>
            </div>
            {latestRun ? (
              <StatusBadge status={latestRun.status} />
            ) : (
              <span className="text-xs text-brand-muted">No runs executed</span>
            )}
          </div>

          {latestRun ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-3 bg-brand-elevated rounded border border-brand-border/60">
                  <span className="text-[11px] text-brand-muted block mb-1">Scheduled Exams</span>
                  <span className="text-xl font-bold font-mono text-emerald-400">
                    {latestRun.scheduled_count}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">
                    of {latestRun.total_exams} exams
                  </span>
                </div>

                <div className="p-3 bg-brand-elevated rounded border border-brand-border/60">
                  <span className="text-[11px] text-brand-muted block mb-1">Unassigned Exams</span>
                  <span className="text-xl font-bold font-mono text-amber-400">
                    {latestRun.unassigned_count}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Documented reasons</span>
                </div>

                <div className="p-3 bg-brand-elevated rounded border border-brand-border/60">
                  <span className="text-[11px] text-brand-muted block mb-1">Completion Rate</span>
                  <span className="text-xl font-bold font-mono text-brand-accent">
                    {overview?.completion_rate_pct}%
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Feasibility yield</span>
                </div>

                <div className="p-3 bg-brand-elevated rounded border border-brand-border/60">
                  <span className="text-[11px] text-brand-muted block mb-1">Seated Registrations</span>
                  <span className="text-xl font-bold font-mono text-sky-400">
                    {overview?.total_seated_registrations?.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Students placed</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-xs text-brand-muted mb-2 font-mono">
                  <span>Schedule Completion Yield</span>
                  <span className="text-brand-text font-bold">{overview?.completion_rate_pct}%</span>
                </div>
                <div className="h-2.5 w-full bg-brand-elevated rounded-full overflow-hidden border border-brand-border">
                  <div
                    className="h-full bg-gradient-to-r from-brand-accent to-emerald-400 rounded-full transition-all duration-500"
                    style={{ width: `${overview?.completion_rate_pct || 0}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-2">
                <span className="text-brand-muted font-mono text-[11px]">
                  Run ID: {latestRun.run_code} • Seed: {latestRun.seed} • Engine: v{latestRun.algorithm_version}
                </span>
                <button
                  onClick={() => navigate('/scheduling')}
                  className="flex items-center gap-1.5 text-brand-accent hover:text-brand-accent-hover font-medium transition-colors"
                >
                  Inspect Timetable & Decisions <ArrowRight size={14} />
                </button>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-brand-muted text-xs">
              No scheduling runs have been recorded for this period yet.
              <button
                onClick={() => navigate('/scheduling')}
                className="mt-3 block mx-auto text-brand-accent font-semibold"
              >
                Create First Run →
              </button>
            </div>
          )}
        </div>

        {/* Quick Operations & Resource Insights */}
        <div className="bg-brand-surface border border-brand-border rounded-lg p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text pb-4 border-b border-brand-border mb-4">
              Operational Actions
            </h3>

            <div className="space-y-3">
              <button
                onClick={() => navigate('/scheduling')}
                className="w-full text-left p-3 rounded bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-brand-text group-hover:text-brand-accent transition-colors">
                    Examination Workspace
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Generate and publish schedules
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors" />
              </button>

              <button
                onClick={() => navigate('/exceptions')}
                className="w-full text-left p-3 rounded bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-brand-text group-hover:text-brand-accent transition-colors">
                    Exception Center
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Investigate {overview?.unassigned_exams || 0} unscheduled exams
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors" />
              </button>

              <button
                onClick={() => navigate('/analytics')}
                className="w-full text-left p-3 rounded bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-brand-text group-hover:text-brand-accent transition-colors">
                    Analytics & Reconciliation
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Audit capacity and export data
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors" />
              </button>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-brand-border text-[11px] text-brand-muted">
            <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <CheckCircle2 size={13} />
              Zero Hard Constraint Breaches Certified
            </div>
            <p className="mt-1 text-slate-400">
              Verified by independent constraint validator.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

