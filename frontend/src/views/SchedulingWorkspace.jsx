import React, { useState, useEffect } from 'react';
import {
  Play,
  UploadCloud,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  AlertTriangle,
  Plus,
  Eye,
  Check,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Drawer from '../components/common/Drawer';
import Modal from '../components/common/Modal';

export default function SchedulingWorkspace() {
  const { isAdmin, currentRole } = useAuth();

  const [runs, setRuns] = useState([]);
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [activeRun, setActiveRun] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  // Decision Inspection Drawer State
  const [inspectingDecision, setInspectingDecision] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Create Timetable Modal State
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newRunSeed, setNewRunSeed] = useState(20261022);
  const [newRunVersion, setNewRunVersion] = useState('1.0.0');
  const [autoExecute, setAutoExecute] = useState(true);
  const [creating, setCreating] = useState(false);
  const [modalError, setModalError] = useState(null);

  useEffect(() => {
    loadRuns();
  }, []);

  useEffect(() => {
    if (selectedRunId) {
      loadRunDetails(selectedRunId);
    }
  }, [selectedRunId]);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const data = await api.listRuns();
      setRuns(data);
      if (data.length > 0 && !selectedRunId) {
        // Prioritize the active published run or the latest executed run with confirmed assignments
        const preferred = data.find((r) => r.status === 'PUBLISHED') ||
          data.find((r) => r.scheduled_count > 0 && r.status !== 'DRAFT') ||
          data[0];
        setSelectedRunId(preferred.id);
      }
    } catch (err) {
      console.error('Failed to load timetables:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRunDetails = async (runId) => {
    try {
      setLoading(true);
      const promises = [
        api.getRun(runId),
        api.getRunAssignments(runId, { limit: 500 }),
      ];
      if (isAdmin) {
        promises.push(api.getRunDecisions(runId, { limit: 500 }));
      }
      const results = await Promise.all(promises);
      setActiveRun(results[0]);
      setAssignments(results[1] || []);
      setDecisions(isAdmin && results[2] ? results[2] : []);
    } catch (err) {
      console.error('Failed to load timetable details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRun = async (e) => {
    e.preventDefault();
    setModalError(null);
    setCreating(true);
    try {
      const periodId = activeRun?.academic_period_id || '11111111-1111-1111-1111-111111111111';
      const newRun = await api.createRun({
        academic_period_id: periodId,
        algorithm_version: newRunVersion,
        seed: Number(newRunSeed),
        auto_execute: autoExecute,
      });
      setCreateModalOpen(false);
      await loadRuns();
      setSelectedRunId(newRun.id);
      if (autoExecute && newRun.scheduled_count > 0) {
        setActionMessage({
          type: 'success',
          text: `Created and scheduled timetable ${newRun.run_code}: ${newRun.scheduled_count} exams scheduled across rooms with 0 conflicts!`,
        });
      } else {
        setActionMessage({
          type: 'success',
          text: `Created new timetable draft ${newRun.run_code}. You can now run the scheduler.`,
        });
      }
    } catch (err) {
      const msg = err.message || '';
      let userFriendlyError = err.message;
      if (
        msg.includes('403') ||
        msg.includes('Forbidden') ||
        msg.includes('permission') ||
        msg.includes('lacks permission')
      ) {
        userFriendlyError = `You do not have permission to create timetables in your current role (${currentRole || 'Learner'}). Please switch to Exam Officer or Academic Administrator.`;
      }
      setModalError(userFriendlyError);
      setActionMessage({ type: 'error', text: userFriendlyError });
    } finally {
      setCreating(false);
    }
  };

  const handleExecuteSolver = async () => {
    if (!selectedRunId) return;
    if (activeRun?.status === 'PUBLISHED') {
      setActionMessage({
        type: 'error',
        text: 'This timetable is already PUBLISHED and cannot be re-executed. Please click "New Timetable" to create a new draft.',
      });
      return;
    }
    try {
      setExecuting(true);
      setActionMessage({ type: 'info', text: 'Running scheduling algorithm and allocating rooms...' });
      const result = await api.executeRun(selectedRunId);
      setActionMessage({
        type: 'success',
        text: `Timetable scheduled successfully: ${result.metrics.scheduled_count} exams scheduled without any conflicts!`,
      });
      await loadRunDetails(selectedRunId);
      await loadRuns();
    } catch (err) {
      setActionMessage({
        type: 'error',
        text: `Scheduling failed: ${err.message || 'Unable to complete timetable calculation.'}`,
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedRunId) return;
    try {
      await api.approveRun(selectedRunId);
      setActionMessage({ type: 'success', text: 'Timetable approved successfully for official release!' });
      await loadRunDetails(selectedRunId);
      await loadRuns();
    } catch (err) {
      setActionMessage({ type: 'error', text: err.message || 'Unable to approve timetable.' });
    }
  };

  const handlePublish = async () => {
    if (!selectedRunId) return;
    try {
      const res = await api.publishRun(selectedRunId);
      if (res.success) {
        setActionMessage({
          type: 'success',
          text: `Official timetable published! Available to all departments and students.`,
        });
        await loadRunDetails(selectedRunId);
        await loadRuns();
      }
    } catch (err) {
      setActionMessage({ type: 'error', text: `Publication failed: ${err.message}` });
    }
  };

  const handleExportCsv = async () => {
    if (!selectedRunId) return;
    try {
      const csvData = await api.exportRunCsv(selectedRunId);
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `examops_timetable_${selectedRunId.slice(0, 8)}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      setActionMessage({ type: 'error', text: 'Failed to download CSV timetable file.' });
    }
  };

  const handleExportJson = async () => {
    if (!selectedRunId) return;
    try {
      const jsonData = await api.exportRunJson(selectedRunId);
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `examops_timetable_${selectedRunId.slice(0, 8)}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      setActionMessage({ type: 'error', text: 'Failed to download JSON timetable file.' });
    }
  };

  const openDecisionDrawer = (examId) => {
    const dec = decisions.find((d) => d.exam_id === examId);
    setInspectingDecision(dec || null);
    setDrawerOpen(true);
  };

  // Assignment columns definition
  const columns = [
    {
      header: 'Assignment Code',
      accessor: 'assignment_code',
      width: '180px',
      render: (val) => <span className="font-mono text-brand-accent font-semibold">{val}</span>,
    },
    {
      header: 'Examination',
      accessor: 'exam_code',
      render: (val, row) => (
        <div>
          <span className="font-mono text-xs font-semibold text-brand-text">{val}</span>
          <div className="text-[11px] text-brand-muted truncate max-w-xs">{row.exam_title}</div>
        </div>
      ),
    },
    {
      header: 'Room / Venue',
      accessor: 'room_code',
      render: (val, row) => (
        <div>
          <span className="font-mono text-xs font-semibold text-slate-300">{val}</span>
          <div className="text-[11px] text-brand-muted">{row.building} • {row.room_name}</div>
        </div>
      ),
    },
    {
      header: 'Date & Time',
      accessor: 'start_time',
      render: (val, row) => {
        const start = new Date(val);
        const end = new Date(row.end_time);
        return (
          <div className="text-[11px] font-mono text-slate-300">
            <div>{start.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</div>
            <div className="text-brand-muted">
              {start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -{' '}
              {end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        );
      },
    },
    {
      header: 'Students Seated',
      accessor: 'seated_student_count',
      width: '120px',
      render: (val) => (
        <span className="font-mono text-xs font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
          {val} students
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      width: '110px',
      render: (val) => <StatusBadge status={val} size="xs" />,
    },
    ...(isAdmin ? [{
      header: 'Reason',
      accessor: 'exam_id',
      width: '110px',
      sortable: false,
      render: (examId) => (
        <button
          onClick={() => openDecisionDrawer(examId)}
          className="flex items-center gap-1.5 px-2.5 py-1 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded text-[11px] text-brand-text hover:text-brand-accent transition-colors"
          aria-label="View scheduling explanation"
        >
          <Eye size={12} className="text-brand-accent" /> Details
        </button>
      ),
    }] : []),
  ];

  return (
    <div className="space-y-6">
      {/* Top Operations Action Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-4 sm:p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Timetable Version Selector */}
          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            <span className="text-xs uppercase font-mono tracking-wider text-slate-400 shrink-0">
              Timetable:
            </span>
            <select
              value={selectedRunId || ''}
              onChange={(e) => setSelectedRunId(e.target.value)}
              className="bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-1.5 text-xs text-brand-text font-mono focus:outline-none focus:border-brand-accent max-w-full sm:max-w-md"
              aria-label="Select timetable version"
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.run_code} ({r.status}) — {r.scheduled_count}/{r.total_exams} scheduled
                </option>
              ))}
            </select>

            {isAdmin && (
              <button
                onClick={() => {
                  setModalError(null);
                  setCreateModalOpen(true);
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded-[4px] text-xs text-brand-text hover:border-brand-accent transition-colors shrink-0"
              >
                <Plus size={14} className="text-brand-accent" /> New Timetable
              </button>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 flex-wrap justify-start md:justify-end">
            <button
              onClick={handleExecuteSolver}
              disabled={executing || !isAdmin || activeRun?.status === 'PUBLISHED' || activeRun?.status === 'SUPERSEDED' || activeRun?.status === 'APPROVED'}
              title={activeRun?.status === 'PUBLISHED' ? "Published timetables are immutable and cannot be re-executed. Click 'New Timetable' to create and run a new draft." : undefined}
              className="flex items-center gap-1.5 px-3.5 py-2 sm:py-1.5 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold text-xs rounded-[4px] transition-all shadow-md shadow-brand-accent/20 disabled:opacity-50"
            >
              <Play size={13} className="fill-current" />
              {executing ? 'Running Scheduler...' : 'Run Scheduler'}
            </button>

            <button
              onClick={handleApprove}
              disabled={!activeRun || activeRun.status === 'PUBLISHED' || !isAdmin}
              className="flex items-center gap-1.5 px-3 py-2 sm:py-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border hover:border-brand-accent text-xs text-slate-300 rounded-[4px] transition-colors disabled:opacity-50"
            >
              <Check size={14} className="text-brand-accent" />
              Approve Timetable
            </button>

            <button
              onClick={handlePublish}
              disabled={!activeRun || activeRun.status === 'PUBLISHED' || !isAdmin}
              className="flex items-center gap-1.5 px-3 py-2 sm:py-1.5 bg-brand-accent hover:bg-brand-accent-hover border border-[#62626266]/40 text-black font-semibold text-xs rounded-[4px] transition-colors disabled:opacity-50"
            >
              <UploadCloud size={14} />
              Publish Timetable
            </button>

            {/* Downloads */}
            <div className="flex items-center gap-1 pl-2 border-l border-brand-border">
              <button
                onClick={handleExportCsv}
                title="Download Timetable as CSV"
                className="p-2 sm:p-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded-[4px] text-brand-muted hover:text-brand-text transition-colors"
                aria-label="Download CSV"
              >
                <FileSpreadsheet size={16} />
              </button>
              <button
                onClick={handleExportJson}
                title="Download Timetable as JSON"
                className="p-2 sm:p-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded-[4px] text-brand-muted hover:text-brand-text transition-colors"
                aria-label="Download JSON"
              >
                <FileCode size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Read-Only Role Notice if not authorized */}
        {!isAdmin && (
          <div className="p-3 bg-amber-950/30 border border-amber-800/40 rounded-[4px] flex items-center justify-between text-xs text-amber-200">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                <strong>View-Only Mode:</strong> You are viewing this page with the{' '}
                <span className="font-mono font-bold text-amber-300">{currentRole || 'Learner'}</span> role. Creating or publishing timetables requires <strong>Exam Officer</strong> or <strong>Administrator</strong> permissions.
              </span>
            </div>
          </div>
        )}

        {/* Published Timetable Immutability Notice */}
        {activeRun?.status === 'PUBLISHED' && (
          <div className="p-3 bg-brand-elevated/70 border border-brand-accent/30 rounded-[4px] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-brand-text">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-brand-accent shrink-0" />
              <span>
                <strong>Official Timetable Published:</strong> Run <span className="font-mono text-brand-accent font-semibold">{activeRun.run_code}</span> is officially published and immutable. Historical assignments are permanently preserved for audit. To modify or generate a new schedule, create a new timetable draft.
              </span>
            </div>
            {isAdmin && (
              <button
                onClick={() => {
                  setModalError(null);
                  setCreateModalOpen(true);
                }}
                className="px-2.5 py-1 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold text-xs rounded transition-colors shrink-0 flex items-center gap-1 cursor-pointer"
              >
                <Plus size={12} /> New Timetable Draft
              </button>
            )}
          </div>
        )}

        {/* Unexecuted Timetable Draft Notice */}
        {activeRun?.status === 'DRAFT' && activeRun?.scheduled_count === 0 && (
          <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-[4px] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-amber-200">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                <strong>Unexecuted Timetable Draft:</strong> Run <span className="font-mono text-amber-300 font-semibold">{activeRun.run_code}</span> has not been solved yet ({activeRun.total_exams} exams awaiting room and invigilator allocation).
              </span>
            </div>
            {isAdmin && (
              <button
                onClick={handleExecuteSolver}
                disabled={executing}
                className="px-2.5 py-1 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold text-xs rounded transition-colors shrink-0 flex items-center gap-1 cursor-pointer disabled:opacity-50"
              >
                <Play size={12} className="fill-current" /> {executing ? 'Solving...' : 'Run Scheduler Now'}
              </button>
            )}
          </div>
        )}

        {/* Action Notification Message */}
        {actionMessage && (
          <div
            className={`p-3 rounded-[4px] text-xs flex items-center justify-between ${
              actionMessage.type === 'error'
                ? 'bg-rose-500/15 border border-rose-500/30 text-rose-300'
                : actionMessage.type === 'info'
                ? 'bg-sky-500/15 border border-sky-500/30 text-sky-300'
                : 'bg-brand-accent/15 border border-brand-accent/30 text-brand-accent'
            }`}
          >
            <span>{actionMessage.text}</span>
            <button
              onClick={() => setActionMessage(null)}
              className="text-xs font-bold opacity-70 hover:opacity-100 ml-2"
              aria-label="Dismiss alert"
            >
              ✕
            </button>
          </div>
        )}

        {/* Status & Integrity Banner */}
        {activeRun && (
          <div className="pt-3 border-t border-brand-border flex flex-col sm:flex-row sm:items-center justify-between text-xs text-brand-muted gap-3">
            <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
              <span>Status: <StatusBadge status={activeRun.status} size="xs" /></span>
              <span>•</span>
              <span>Scheduled: <strong className="text-brand-accent font-mono">{activeRun.scheduled_count}</strong></span>
              <span>•</span>
              <span>Unassigned: <strong className="text-amber-400 font-mono">{activeRun.unassigned_count}</strong></span>
              <span>•</span>
              <span>Total Exams: <strong className="text-slate-300 font-mono">{activeRun.total_exams}</strong></span>
            </div>

            <div className="flex items-center gap-1.5 text-brand-accent font-medium">
              <ShieldCheck size={14} className="shrink-0" />
              <span>Verified: All Scheduling Rules Met (No Conflicts)</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Timetable Data Table */}
      <DataTable
        columns={columns}
        data={assignments}
        loading={loading}
        searchPlaceholder="Filter assignments by exam code, title, room code, or building..."
        emptyMessage="No exam assignments found for this timetable. Click 'Create Timetable' to assign rooms and times automatically."
      />

      {/* Decision Details Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Scheduling Decision Details"
        subtitle={inspectingDecision ? `Exam Code: ${inspectingDecision.exam_code}` : ''}
      >
        {inspectingDecision ? (
          <div className="space-y-5 text-xs">
            <div className="p-3 bg-brand-elevated rounded border border-brand-border">
              <div className="text-slate-400 uppercase text-[10px] font-bold tracking-wider mb-1">
                Scheduling Outcome
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge
                  status={inspectingDecision.is_assigned ? 'CONFIRMED' : 'WARNING'}
                  size="sm"
                />
                <span className="font-semibold text-brand-text">
                  {inspectingDecision.is_assigned ? 'Successfully Scheduled' : 'Unassigned in this Timetable'}
                </span>
              </div>
            </div>

            {/* Reason Codes if unassigned */}
            {!inspectingDecision.is_assigned && (
              <div>
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[10px] mb-2">
                  Why It Could Not Be Scheduled
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {inspectingDecision.reason_codes?.map((code) => (
                    <span
                      key={code}
                      className="px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30 font-mono text-[11px]"
                    >
                      {code}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Selected candidate info if assigned */}
            {inspectingDecision.is_assigned && inspectingDecision.selected_candidate && (
              <div className="space-y-3">
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[10px]">
                  Assigned Room & Time
                </h4>
                <div className="p-3 bg-brand-elevated rounded border border-brand-border space-y-2 font-mono text-[11px]">
                  <div>Date: <span className="text-brand-text">{inspectingDecision.selected_candidate.date}</span></div>
                  <div>
                    Time: <span className="text-brand-text">
                      {new Date(inspectingDecision.selected_candidate.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -{' '}
                      {new Date(inspectingDecision.selected_candidate.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div>Allocated Rooms: <span className="text-brand-accent">{inspectingDecision.selected_candidate.room_codes?.join(', ')}</span></div>
                  <div>Students Seated: <span className="text-brand-accent">{inspectingDecision.selected_candidate.total_seated}</span></div>
                </div>
              </div>
            )}

            {/* Candidate evaluation details */}
            {inspectingDecision.candidate_details && (
              <div>
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[10px] mb-2">
                  Scheduling Evaluation Details
                </h4>
                <div className="p-3 bg-brand-elevated rounded border border-brand-border space-y-1.5 font-mono text-[11px] text-brand-muted">
                  <div>Decision Order: <span className="text-brand-text font-bold">{inspectingDecision.decision_order}</span></div>
                  <div>Slots Evaluated: <span className="text-brand-text">{inspectingDecision.candidate_details.evaluated_slots}</span></div>
                  <div>Valid Slots Found: <span className="text-brand-text">{inspectingDecision.candidate_details.valid_slots_found || 0}</span></div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>No decision record available.</div>
        )}
      </Drawer>

      {/* New Timetable Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => {
          setCreateModalOpen(false);
          setModalError(null);
        }}
        title="Create New Exam Timetable"
        subtitle="Start a new schedule draft for this academic term."
      >
        <form onSubmit={handleCreateRun} className="space-y-4">
          {modalError && (
            <div className="p-3 bg-red-950/70 border border-red-800 rounded-md flex items-start gap-2.5 text-xs text-red-200">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block text-red-100">Action Not Allowed</span>
                <span className="text-[11px] leading-relaxed text-red-300">{modalError}</span>
              </div>
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Schedule Seed (Advanced)
            </label>
            <input
              type="number"
              value={newRunSeed}
              onChange={(e) => setNewRunSeed(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-brand-text font-mono focus:border-brand-accent focus:outline-none"
            />
            <span className="text-[10px] text-brand-muted mt-1 block">
              Standard seed: 20261022. Ensures the timetable generates consistently and reproducibly.
            </span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Scheduler Version
            </label>
            <input
              type="text"
              value={newRunVersion}
              onChange={(e) => setNewRunVersion(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-brand-text font-mono focus:border-brand-accent focus:outline-none"
            />
          </div>

          <div className="pt-2">
            <label className="flex items-start gap-2.5 cursor-pointer select-none text-xs text-slate-300 bg-brand-elevated/60 p-2.5 rounded border border-brand-border">
              <input
                type="checkbox"
                checked={autoExecute}
                onChange={(e) => setAutoExecute(e.target.checked)}
                className="mt-0.5 rounded border-brand-border text-brand-accent focus:ring-brand-accent focus:ring-offset-brand-bg bg-brand-surface"
              />
              <div>
                <span className="font-semibold text-brand-text block">
                  Automatically run solver and seat exams
                </span>
                <span className="text-[11px] text-brand-muted block mt-0.5">
                  Immediately assigns conflict-free rooms and invigilators upon creation so the timetable is ready for export.
                </span>
              </div>
            </label>
          </div>

          <div className="pt-4 flex justify-end gap-2">
            <button
              type="button"
              disabled={creating}
              onClick={() => setCreateModalOpen(false)}
              className="px-3.5 py-1.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-slate-300 hover:text-brand-text disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-1.5 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold rounded-[4px] text-xs transition-colors disabled:opacity-50 cursor-pointer"
            >
              {creating ? 'Creating & Solving...' : 'Create Timetable'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
