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
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import MetricDisplay from '../components/common/MetricDisplay';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';

export default function OverviewDashboard() {
  const navigate = useNavigate();
  const { currentRole, currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState(null);

  // Student portal specific state
  const [studentSchedule, setStudentSchedule] = useState([]);
  const [studentEnrollments, setStudentEnrollments] = useState([]);
  const [studentAccommodations, setStudentAccommodations] = useState([]);

  useEffect(() => {
    loadOverview();
  }, [currentRole]);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);

      if (currentRole === 'LEARNER') {
        const studentId = currentUser?.student_id;
        const [sched, enrs, accs] = await Promise.all([
          studentId ? api.getStudentSchedule(studentId).catch(() => []) : [],
          studentId ? api.getStudentEnrollments(studentId).catch(() => []) : [],
          api.listAccommodations().catch(() => []),
        ]);
        setStudentSchedule(Array.isArray(sched) ? sched : []);
        setStudentEnrollments(Array.isArray(enrs) ? enrs : []);
        const accItems = Array.isArray(accs) ? accs : (accs?.items || []);
        setStudentAccommodations(accItems);
      } else {
        const data = await api.getAnalyticsOverview();
        setOverview(data);
      }
    } catch (err) {
      setError(err.message || 'Unable to load timetable overview. Please verify your connection.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading exam operations overview..." />;
  if (error) {
    return (
      <div className="p-6 bg-brand-surface border border-brand-danger/30 rounded-[4px] text-center text-brand-danger">
        <AlertTriangle className="mx-auto mb-2" size={24} />
        <p className="text-sm font-semibold">{error}</p>
        <button
          onClick={loadOverview}
          className="mt-4 px-4 py-1.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-white hover:border-brand-accent transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Learner Role View: Dedicated Personal Student Portal
  if (currentRole === 'LEARNER') {
    return (
      <div className="space-y-6">
        {/* Student Welcome Banner */}
        <div className="bg-[#121212] border border-brand-border rounded-[4px] p-4 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs uppercase font-mono tracking-wider text-brand-accent font-semibold">
                Student Examination Portal
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
              <span className="text-xs text-brand-muted">Fall 2026 Examination Period</span>
            </div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Welcome, {currentUser?.display_name || 'Candidate'}
            </h2>
            <p className="text-xs text-brand-muted mt-1">
              Account: <span className="font-mono text-slate-300">{currentUser?.email}</span> • Status:{' '}
              <span className="text-brand-accent font-semibold">Active Enrolled Student</span>
            </p>
          </div>

          <div className="flex items-center gap-2 bg-brand-elevated border border-brand-border rounded-[4px] px-3.5 py-2">
            <CheckCircle2 className="w-4 h-4 text-brand-accent shrink-0" />
            <div className="text-xs">
              <div className="font-semibold text-white">Timetable Published</div>
              <div className="text-[11px] text-brand-muted">Official Examination Schedule</div>
            </div>
          </div>
        </div>

        {/* Student Scale Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          <MetricDisplay
            label="Scheduled Exams"
            value={studentSchedule.length}
            icon={GraduationCap}
            secondary="Published exam sessions"
          />
          <MetricDisplay
            label="Enrolled Courses"
            value={studentEnrollments.length}
            icon={Calendar}
            secondary="Active term registrations"
          />
          <MetricDisplay
            label="Accommodations"
            value={studentAccommodations.length}
            icon={HeartHandshake}
            secondary="Verified adjustments"
          />
          <MetricDisplay
            label="Privacy Status"
            value="Protected"
            icon={CheckCircle2}
            secondary="Student records isolated"
          />
        </div>

        {/* Personal Examination Timetable */}
        <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-brand-border">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <Calendar className="w-4 h-4 text-brand-accent" />
                My Official Examination Timetable
              </h3>
              <p className="text-xs text-brand-muted mt-0.5">
                Confirmed room locations, dates, and times for your scheduled examinations.
              </p>
            </div>
            <span className="text-[11px] font-mono text-brand-accent bg-brand-elevated px-2 py-0.5 rounded border border-brand-border self-start sm:self-auto">
              {studentSchedule.length} Examinations Seated
            </span>
          </div>

          {studentSchedule.length === 0 ? (
            <div className="p-8 text-center text-brand-muted text-xs bg-brand-elevated/40 rounded border border-brand-border">
              <Calendar className="w-8 h-8 text-slate-500 mx-auto mb-2" />
              <div className="font-semibold text-slate-300">No Examinations Scheduled</div>
              <div className="mt-1 text-slate-400">
                You do not have any examinations scheduled in the published timetable.
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-brand-border text-brand-muted font-mono text-[11px] uppercase tracking-wider">
                    <th className="py-2.5 px-3">Exam Code</th>
                    <th className="py-2.5 px-3">Examination Title</th>
                    <th className="py-2.5 px-3">Date & Time</th>
                    <th className="py-2.5 px-3">Venue / Room</th>
                    <th className="py-2.5 px-3">Duration</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-border/60">
                  {studentSchedule.map((s) => {
                    const start = new Date(s.start_time);
                    const end = new Date(s.end_time);
                    return (
                      <tr key={s.assignment_student_id || s.exam_code} className="hover:bg-white/[0.02] transition-colors">
                        <td className="py-3 px-3 font-mono font-semibold text-brand-accent">
                          {s.exam_code}
                        </td>
                        <td className="py-3 px-3">
                          <span className="font-medium text-white block">{s.exam_title}</span>
                          <span className="text-[11px] text-brand-muted font-mono">{s.assignment_code}</span>
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-300">
                          <div>{start.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</div>
                          <div className="text-[11px] text-brand-muted">
                            {start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -{' '}
                            {end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <div className="font-mono text-slate-200 font-semibold">{s.room_code}</div>
                          <div className="text-[11px] text-brand-muted">
                            {s.room_name} • {s.building}
                          </div>
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-300">
                          {s.effective_duration_minutes} min
                        </td>
                        <td className="py-3 px-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                            Confirmed
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Student Privacy & Guidelines Notice */}
        <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] flex items-start gap-3 text-xs text-brand-muted">
          <CheckCircle2 className="w-4 h-4 text-brand-accent shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold text-white block">Student Data Privacy & Examination Protocols</span>
            <p className="text-slate-400 text-[11px]">
              Your examination timetable is tailored to your registered courses. Candidate information, accommodations, and personal timetable entries are strictly isolated under institutional privacy policies. For queries regarding your schedule or accommodations, contact the Examinations Office.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const latestRun = overview?.latest_run;

  return (
    <div className="space-y-6">
      {/* Top Banner: Academic Term & Timetable Status */}
      <div className="bg-[#121212] border border-brand-border rounded-[4px] p-4 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs uppercase font-mono tracking-wider text-brand-accent font-semibold">
              Academic Term
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
            <span className="text-xs text-brand-muted">Current Semester</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
            {overview?.active_period?.name || 'Fall 2026 Examination Period'}
          </h2>
          <p className="text-xs text-brand-muted mt-1">
            Term Code: <span className="font-mono text-slate-300">{overview?.active_period?.code}</span> •
            Exam Dates: <span className="font-mono text-slate-300">{overview?.active_period?.exam_start_date}</span> to{' '}
            <span className="font-mono text-slate-300">{overview?.active_period?.exam_end_date}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/scheduling')}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2.5 bg-brand-accent hover:bg-brand-accent-hover text-black font-semibold rounded-[4px] text-xs transition-all border border-[#62626266]/40 shadow-sm"
          >
            <Play size={14} className="fill-current" />
            Open Scheduling Workspace
          </button>
        </div>
      </div>

      {/* Primary Scale Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Students"
          value={overview?.total_students?.toLocaleString()}
          icon={Users}
          secondary="Enrolled students"
        />
        <MetricDisplay
          label="Total Courses"
          value={overview?.total_courses?.toLocaleString()}
          icon={GraduationCap}
          secondary="Active this term"
        />
        <MetricDisplay
          label="Examinations"
          value={overview?.total_exams?.toLocaleString()}
          icon={Calendar}
          secondary="Midterms & finals"
        />
        <MetricDisplay
          label="Exam Rooms"
          value={overview?.total_rooms?.toLocaleString()}
          icon={DoorOpen}
          secondary="Available for exams"
        />
        <MetricDisplay
          label="Invigilators"
          value={overview?.total_invigilators?.toLocaleString()}
          icon={UserCheck}
          secondary="Exam supervision staff"
        />
        <MetricDisplay
          label="Accommodations"
          value={overview?.total_active_accommodations?.toLocaleString()}
          icon={HeartHandshake}
          secondary="Student support needs"
        />
      </div>

      {/* Schedule Condition Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-brand-border mb-5 gap-2">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                Current Timetable Status
              </h3>
              <p className="text-xs text-brand-muted mt-0.5">
                Official examination schedule for this academic term
              </p>
            </div>
            {latestRun ? (
              <StatusBadge status={latestRun.status} />
            ) : (
              <span className="text-xs text-brand-muted">No timetable generated yet</span>
            )}
          </div>

          {latestRun ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                <div className="p-3 bg-brand-elevated rounded-[4px] border border-brand-border">
                  <span className="text-[11px] text-brand-muted block mb-1">Scheduled Exams</span>
                  <span className="text-lg sm:text-xl font-bold font-mono text-brand-accent">
                    {latestRun.scheduled_count}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">
                    of {latestRun.total_exams} exams
                  </span>
                </div>

                <div className="p-3 bg-brand-elevated rounded-[4px] border border-brand-border">
                  <span className="text-[11px] text-brand-muted block mb-1">Unscheduled Exams</span>
                  <span className="text-lg sm:text-xl font-bold font-mono text-brand-warning">
                    {latestRun.unassigned_count}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Needs attention</span>
                </div>

                <div className="p-3 bg-brand-elevated rounded-[4px] border border-brand-border">
                  <span className="text-[11px] text-brand-muted block mb-1">Scheduling Success</span>
                  <span className="text-lg sm:text-xl font-bold font-mono text-brand-accent">
                    {overview?.completion_rate_pct}%
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Exams placed</span>
                </div>

                <div className="p-3 bg-brand-elevated rounded-[4px] border border-brand-border">
                  <span className="text-[11px] text-brand-muted block mb-1">Seated Students</span>
                  <span className="text-lg sm:text-xl font-bold font-mono text-white">
                    {overview?.total_seated_registrations?.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-brand-muted block mt-1">Desks assigned</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-xs text-brand-muted mb-2 font-mono">
                  <span>Overall Scheduling Progress</span>
                  <span className="text-white font-bold">{overview?.completion_rate_pct}%</span>
                </div>
                <div className="h-2.5 w-full bg-brand-elevated rounded-[2px] overflow-hidden border border-brand-border">
                  <div
                    className="h-full bg-brand-accent rounded-[2px] transition-all duration-500 shadow-[0_0_8px_rgba(184,239,67,0.5)]"
                    style={{ width: `${overview?.completion_rate_pct || 0}%` }}
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs pt-2 gap-2">
                <span className="text-brand-muted font-mono text-[11px]">
                  Timetable Code: {latestRun.run_code} • Scheduler v{latestRun.algorithm_version}
                </span>
                <button
                  onClick={() => navigate('/scheduling')}
                  className="flex items-center gap-1.5 text-brand-accent hover:text-brand-accent-hover font-medium transition-colors"
                >
                  View Timetable & Decisions <ArrowRight size={14} />
                </button>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-brand-muted text-xs">
              No exam timetables have been created for this term yet.
              <button
                onClick={() => navigate('/scheduling')}
                className="mt-3 block mx-auto text-brand-accent font-semibold"
              >
                Create First Timetable →
              </button>
            </div>
          )}
        </div>

        {/* Quick Operations & Resource Insights */}
        <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-white pb-4 border-b border-brand-border mb-4">
              Quick Actions
            </h3>

            <div className="space-y-3">
              <button
                onClick={() => navigate('/scheduling')}
                className="w-full text-left p-3 rounded-[4px] bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-brand-accent transition-colors">
                    Scheduling Workspace
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Create, review, and publish exam timetables
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors shrink-0" />
              </button>

              <button
                onClick={() => navigate('/exceptions')}
                className="w-full text-left p-3 rounded-[4px] bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-brand-accent transition-colors">
                    Issue Center
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Review {overview?.unassigned_exams || 0} unscheduled exams
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors shrink-0" />
              </button>

              <button
                onClick={() => navigate('/analytics')}
                className="w-full text-left p-3 rounded-[4px] bg-brand-elevated border border-brand-border hover:border-brand-accent/50 transition-colors flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-brand-accent transition-colors">
                    Reports & Insights
                  </div>
                  <div className="text-[11px] text-brand-muted">
                    Review room capacity and download records
                  </div>
                </div>
                <ArrowRight size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors shrink-0" />
              </button>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-brand-border text-[11px] text-brand-muted">
            <div className="flex items-center gap-1.5 text-brand-accent font-medium">
              <CheckCircle2 size={13} className="shrink-0" />
              All Scheduling Rules Met
            </div>
            <p className="mt-1 text-slate-400">
              Verified: Zero student clashes or room capacity overruns.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
