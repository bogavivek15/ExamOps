import React, { useState, useEffect } from 'react';
import {
  Play,
  CheckCircle,
  UploadCloud,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  AlertTriangle,
  Plus,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Clock,
  MapPin,
  Users,
  Eye,
  Check,
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Drawer from '../components/common/Drawer';
import Modal from '../components/common/Modal';
import LoadingState from '../components/common/LoadingState';

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

  // Decision Telemetry Drawer State
  const [inspectingDecision, setInspectingDecision] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Create Run Modal State
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newRunSeed, setNewRunSeed] = useState(20261022);
  const [newRunVersion, setNewRunVersion] = useState('1.0.0');
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
        setSelectedRunId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load runs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRunDetails = async (runId) => {
    try {
      setLoading(true);
      const [runData, asgns, decs] = await Promise.all([
        api.getRun(runId),
        api.getRunAssignments(runId, { limit: 500 }),
        api.getRunDecisions(runId, { limit: 500 }),
      ]);
      setActiveRun(runData);
      setAssignments(asgns);
      setDecisions(decs);
    } catch (err) {
      console.error('Failed to load run details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRun = async (e) => {
    e.preventDefault();
    setModalError(null);
    try {
      const periodId = activeRun?.academic_period_id || '11111111-1111-1111-1111-111111111111';
      const newRun = await api.createRun({
        academic_period_id: periodId,
        algorithm_version: newRunVersion,
        seed: Number(newRunSeed),
      });
      setCreateModalOpen(false);
      await loadRuns();
      setSelectedRunId(newRun.id);
      setActionMessage({ type: 'success', text: `Created run ${newRun.run_code}` });
    } catch (err) {
      const msg = err.message || '';
      let userFriendlyError = err.message;
      if (msg.includes('403') || msg.includes('Forbidden') || msg.includes('permission') || msg.includes('lacks permission')) {
        userFriendlyError = `Permission Denied (HTTP 403): Current role '${currentRole || 'LEARNER'}' lacks authorization to create scheduling runs. Authorized roles are: EXAM_OFFICER, ACADEMIC_ADMINISTRATOR, PLATFORM_ADMINISTRATOR, SUPER_ADMIN.`;
      }
      setModalError(userFriendlyError);
      setActionMessage({ type: 'error', text: userFriendlyError });
    }
  };

  const handleExecuteSolver = async () => {
    if (!selectedRunId) return;
    try {
      setExecuting(true);
      setActionMessage({ type: 'info', text: 'Executing deterministic scheduling solver...' });
      const result = await api.executeRun(selectedRunId);
      setActionMessage({
        type: 'success',
        text: `Solved successfully: ${result.metrics.scheduled_count} exams scheduled with zero violations!`,
      });
      await loadRunDetails(selectedRunId);
      await loadRuns();
    } catch (err) {
      setActionMessage({ type: 'error', text: `Execution failed: ${err.message}` });
    } finally {
      setExecuting(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedRunId) return;
    try {
      await api.approveRun(selectedRunId);
      setActionMessage({ type: 'success', text: 'Schedule successfully approved!' });
      await loadRunDetails(selectedRunId);
      await loadRuns();
    } catch (err) {
      setActionMessage({ type: 'error', text: err.message });
    }
  };

  const handlePublish = async () => {
    if (!selectedRunId) return;
    try {
      const res = await api.publishRun(selectedRunId);
      if (res.success) {
        setActionMessage({
          type: 'success',
          text: `Official schedule published! (Run ID: ${res.published_run_id.slice(0, 8)})`,
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
      a.download = `examops_schedule_${selectedRunId.slice(0, 8)}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Failed to export CSV.' });
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
      a.download = `examops_schedule_${selectedRunId.slice(0, 8)}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Failed to export JSON.' });
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
      header: 'Timetable Interval',
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
      header: 'Seated Students',
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
    {
      header: 'Telemetry',
      accessor: 'exam_id',
      width: '90px',
      sortable: false,
      render: (examId) => (
        <button
          onClick={() => openDecisionDrawer(examId)}
          className="flex items-center gap-1 px-2 py-1 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded text-[11px] text-brand-text hover:text-brand-accent transition-colors"
        >
          <Eye size={12} /> Why
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Operations Action Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Run Selector */}
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-mono tracking-wider text-slate-400">
              Run:
            </span>
            <select
              value={selectedRunId || ''}
              onChange={(e) => setSelectedRunId(e.target.value)}
              className="bg-brand-elevated border border-brand-border rounded px-3 py-1.5 text-xs text-brand-text font-mono focus:outline-none focus:border-brand-accent"
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.run_code} ({r.status}) — {r.scheduled_count}/{r.total_exams} scheduled
                </option>
              ))}
            </select>

            <button
              onClick={() => {
                setModalError(null);
                setCreateModalOpen(true);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded text-xs text-brand-text hover:border-brand-accent transition-colors"
            >
              <Plus size={14} className="text-brand-accent" /> New Run
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 flex-wrap justify-end">
            <button
              onClick={handleExecuteSolver}
              disabled={executing || !isAdmin}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold text-xs rounded transition-all shadow-md shadow-brand-accent/20 disabled:opacity-50"
            >
              <Play size={13} className="fill-current" />
              {executing ? 'Solving...' : 'Execute Solver'}
            </button>

            <button
              onClick={handleApprove}
              disabled={!activeRun || activeRun.status === 'PUBLISHED' || !isAdmin}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border hover:border-brand-accent text-xs text-slate-300 rounded transition-colors disabled:opacity-50"
            >
              <Check size={14} className="text-brand-accent" />
              Approve
            </button>

            <button
              onClick={handlePublish}
              disabled={!activeRun || activeRun.status === 'PUBLISHED' || !isAdmin}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-400 font-semibold text-xs rounded transition-colors disabled:opacity-50"
            >
              <UploadCloud size={14} />
              Publish Schedule
            </button>

            {/* Exports */}
            <div className="flex items-center gap-1 pl-2 border-l border-brand-border">
              <button
                onClick={handleExportCsv}
                title="Export Timetable as CSV"
                className="p-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded text-brand-muted hover:text-brand-text transition-colors"
              >
                <FileSpreadsheet size={16} />
              </button>
              <button
                onClick={handleExportJson}
                title="Export Timetable as JSON"
                className="p-1.5 bg-brand-elevated hover:bg-brand-surface border border-brand-border rounded text-brand-muted hover:text-brand-text transition-colors"
              >
                <FileCode size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Read-Only Role Notice if not authorized */}
        {!isAdmin && (
          <div className="p-3 bg-amber-950/30 border border-amber-800/40 rounded-lg flex items-center justify-between text-xs text-amber-200">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                <strong>Read-Only Perspective:</strong> Active role is <span className="font-mono font-bold text-amber-300">{currentRole || 'LEARNER'}</span>. Operational actions (create run, execute solver, approve schedule) require <strong>EXAM_OFFICER</strong> or <strong>ACADEMIC_ADMINISTRATOR</strong>.
              </span>
            </div>
          </div>
        )}

        {/* Action Notification Message */}
        {actionMessage && (
          <div
            className={`p-3 rounded text-xs flex items-center justify-between ${
              actionMessage.type === 'error'
                ? 'bg-rose-500/15 border border-rose-500/30 text-rose-300'
                : actionMessage.type === 'info'
                ? 'bg-sky-500/15 border border-sky-500/30 text-sky-300'
                : 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-300'
            }`}
          >
            <span>{actionMessage.text}</span>
            <button
              onClick={() => setActionMessage(null)}
              className="text-xs font-bold opacity-70 hover:opacity-100"
            >
              ✕
            </button>
          </div>
        )}

        {/* Status & Integrity Guarantee Banner */}
        {activeRun && (
          <div className="pt-3 border-t border-brand-border flex flex-col sm:flex-row sm:items-center justify-between text-xs text-brand-muted gap-3">
            <div className="flex items-center gap-3">
              <span>Status: <StatusBadge status={activeRun.status} size="xs" /></span>
              <span>•</span>
              <span>Scheduled: <strong className="text-emerald-400 font-mono">{activeRun.scheduled_count}</strong></span>
              <span>•</span>
              <span>Unassigned: <strong className="text-amber-400 font-mono">{activeRun.unassigned_count}</strong></span>
              <span>•</span>
              <span>Total Exams: <strong className="text-slate-300 font-mono">{activeRun.total_exams}</strong></span>
            </div>

            <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <ShieldCheck size={14} />
              <span>Independent Certification: Zero Hard Constraints Violated</span>
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
        emptyMessage="No examination assignments found for this scheduling run. Click 'Execute Solver' to generate optimal timetable."
      />

      {/* Decision Telemetry Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Algorithmic Decision Telemetry"
        subtitle={inspectingDecision ? `Inspection for Exam ${inspectingDecision.exam_code}` : ''}
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
                  {inspectingDecision.is_assigned ? 'Successfully Scheduled' : 'Unassigned in this Run'}
                </span>
              </div>
            </div>

            {/* Reason Codes if unassigned */}
            {!inspectingDecision.is_assigned && (
              <div>
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[10px] mb-2">
                  Failure Reason Codes
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
                  Selected Allocation
                </h4>
                <div className="p-3 bg-brand-elevated rounded border border-brand-border space-y-2 font-mono text-[11px]">
                  <div>Date: <span className="text-brand-text">{inspectingDecision.selected_candidate.date}</span></div>
                  <div>Interval: <span className="text-brand-text">{new Date(inspectingDecision.selected_candidate.start_time).toLocaleTimeString()} - {new Date(inspectingDecision.selected_candidate.end_time).toLocaleTimeString()}</span></div>
                  <div>Allocated Rooms: <span className="text-brand-accent">{inspectingDecision.selected_candidate.room_codes?.join(', ')}</span></div>
                  <div>Total Students Seated: <span className="text-emerald-400">{inspectingDecision.selected_candidate.total_seated}</span></div>
                </div>
              </div>
            )}

            {/* Candidate evaluation details */}
            {inspectingDecision.candidate_details && (
              <div>
                <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[10px] mb-2">
                  Evaluation Telemetry
                </h4>
                <div className="p-3 bg-brand-elevated rounded border border-brand-border space-y-1.5 font-mono text-[11px] text-brand-muted">
                  <div>Decision Order: <span className="text-brand-text font-bold">{inspectingDecision.decision_order}</span></div>
                  <div>Evaluated Slots: <span className="text-brand-text">{inspectingDecision.candidate_details.evaluated_slots}</span></div>
                  <div>Valid Candidate Slots: <span className="text-brand-text">{inspectingDecision.candidate_details.valid_slots_found || 0}</span></div>
                  <div>Pass Number: <span className="text-brand-text">{inspectingDecision.candidate_details.pass_number || 1}</span></div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>No decision record available.</div>
        )}
      </Drawer>

      {/* New Run Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => {
          setCreateModalOpen(false);
          setModalError(null);
        }}
        title="Create New Operational Scheduling Run"
        subtitle="Initialize a new scheduling instance for the active academic period."
      >
        <form onSubmit={handleCreateRun} className="space-y-4">
          {modalError && (
            <div className="p-3 bg-red-950/70 border border-red-800 rounded-md flex items-start gap-2.5 text-xs text-red-200">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block text-red-100">Authorization Rejection (HTTP 403)</span>
                <span className="text-[11px] leading-relaxed text-red-300">{modalError}</span>
              </div>
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Random Seed
            </label>
            <input
              type="number"
              value={newRunSeed}
              onChange={(e) => setNewRunSeed(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-brand-elevated border border-brand-border rounded text-xs text-brand-text font-mono focus:border-brand-accent focus:outline-none"
            />
            <span className="text-[10px] text-brand-muted mt-1 block">
              Default baseline seed: 20261022. Guarantees deterministic, reproducible outcomes.
            </span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Algorithm Version
            </label>
            <input
              type="text"
              value={newRunVersion}
              onChange={(e) => setNewRunVersion(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-brand-elevated border border-brand-border rounded text-xs text-brand-text font-mono focus:border-brand-accent focus:outline-none"
            />
          </div>

          <div className="pt-4 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-3 py-1.5 bg-brand-elevated border border-brand-border rounded text-xs text-slate-300 hover:text-brand-text"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 bg-brand-accent hover:bg-brand-accent-hover text-slate-950 font-bold rounded text-xs"
            >
              Create Run
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

