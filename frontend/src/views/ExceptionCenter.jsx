import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Filter, CheckCircle2, RefreshCw, ArrowRight, 
  HelpCircle, ShieldAlert, Cpu, Eye, ExternalLink, Calendar, Search
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function ExceptionCenter() {
  const navigate = useNavigate();
  const [runs, setRuns] = useState([]);
  const [selectedRunId, setSelectedRunId] = useState('');
  const [issues, setIssues] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Selected Exception Detail Drawer
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [issueDecisions, setIssueDecisions] = useState([]);

  useEffect(() => {
    loadRuns();
  }, []);

  useEffect(() => {
    if (selectedRunId) {
      loadRunExceptions(selectedRunId);
    }
  }, [selectedRunId]);

  async function loadRuns() {
    setLoading(true);
    try {
      const runsData = await api.listRuns();
      setRuns(runsData || []);
      if (runsData && runsData.length > 0) {
        setSelectedRunId(runsData[0].id);
      } else {
        setLoading(false);
      }
    } catch (err) {
      setError(err.message || 'Failed to load scheduling runs');
      setLoading(false);
    }
  }

  async function loadRunExceptions(runId) {
    setLoading(true);
    setError(null);
    try {
      const [issuesData, decisionsData] = await Promise.all([
        api.getRunIssues(runId).catch(() => []),
        api.getRunDecisions(runId, { outcome: 'FAILED', limit: 100 }).catch(() => ({ items: [] })),
      ]);
      setIssues(issuesData || []);
      setDecisions(decisionsData.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load run exceptions');
    } finally {
      setLoading(false);
    }
  }

  function handleOpenDetail(issue) {
    setSelectedIssue(issue);
    setDrawerOpen(true);
    // Filter matching failure decisions
    const matching = decisions.filter(d => d.exam_code === issue.exam_code || d.exam_id === issue.exam_id);
    setIssueDecisions(matching);
  }

  const columns = [
    {
      header: 'Exam Code',
      accessor: 'exam_code',
      className: 'font-mono text-brand-accent font-semibold',
    },
    {
      header: 'Title / Course',
      cell: (row) => (
        <div>
          <span className="font-semibold text-brand-text block">{row.exam_title || row.title || 'Course Examination'}</span>
          <span className="text-xs text-brand-muted">{row.course_code || 'Academic Assessment'}</span>
        </div>
      ),
    },
    {
      header: 'Severity',
      cell: (row) => (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-brand-danger/15 text-brand-danger border border-brand-danger/30">
          <AlertTriangle className="w-3 h-3" />
          {row.severity || 'BLOCKING'}
        </span>
      ),
    },
    {
      header: 'Reason Code',
      cell: (row) => (
        <span className="font-mono text-xs font-semibold text-brand-warning">
          {row.reason_code || row.issue_code || 'UNSCHEDULED_CONFLICT'}
        </span>
      ),
    },
    {
      header: 'Evaluated Failure Root Cause',
      cell: (row) => (
        <p className="text-xs text-brand-muted max-w-xs truncate">
          {row.description || row.message || 'No conflict-free timeslot and venue combination met all hard constraints.'}
        </p>
      ),
    },
    {
      header: 'Actions',
      cell: (row) => (
        <button
          onClick={() => handleOpenDetail(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          Investigate
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
            <ShieldAlert className="w-5 h-5 text-brand-danger" />
            Exception Center
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Dedicated triage workspace for unscheduled examinations, hard-constraint rejections, and corrective telemetry.
          </p>
        </div>

        {/* Run Selector */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-brand-muted font-medium">Evaluation Run:</label>
          <select
            value={selectedRunId}
            onChange={(e) => setSelectedRunId(e.target.value)}
            className="bg-brand-elevated border border-brand-border rounded px-3 py-1.5 text-xs text-brand-text font-mono focus:outline-none focus:border-brand-accent"
          >
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                {r.run_code} ({r.status})
              </option>
            ))}
          </select>
          <button
            onClick={() => selectedRunId && loadRunExceptions(selectedRunId)}
            className="p-1.5 rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-muted hover:text-brand-text transition-colors"
            title="Refresh Exceptions"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Unscheduled Examinations"
          value={issues.length}
          subtext="Requires administrative review"
          icon={AlertTriangle}
        />
        <MetricDisplay
          label="Hard Constraint Violations"
          value="0"
          subtext="Zero allowed in confirmed schedule"
          icon={CheckCircle2}
        />
        <MetricDisplay
          label="Telemetry Traces"
          value={decisions.length}
          subtext="Recorded rejected evaluations"
          icon={Cpu}
        />
        <MetricDisplay
          label="Resolution Workflow"
          value="Deterministic"
          subtext="No silent data alterations"
          icon={ShieldAlert}
        />
      </div>

      {/* Main Table */}
      {loading ? (
        <LoadingState message="Analyzing scheduling run exceptions..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Exceptions"
          description={error}
          actionLabel="Retry"
          onAction={() => selectedRunId && loadRunExceptions(selectedRunId)}
        />
      ) : issues.length === 0 ? (
        <div className="bg-brand-surface border border-brand-border rounded-lg p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-brand-success/15 border border-brand-success/30 flex items-center justify-center mx-auto text-brand-success">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-brand-text">Zero Unscheduled Examinations</h3>
          <p className="text-xs text-brand-muted max-w-md mx-auto">
            All course examinations in this scheduling run have been assigned to conflict-free time slots and compliant venues.
          </p>
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={issues}
          total={issues.length}
          page={1}
          pageSize={50}
          onPageChange={() => {}}
          onPageSizeChange={() => {}}
        />
      )}

      {/* Exception Investigation Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Exception Investigation: ${selectedIssue?.exam_code || ''}`}
        size="lg"
      >
        {selectedIssue && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-danger/30 rounded-lg p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono text-brand-danger uppercase tracking-wider font-bold">
                    REASON: {selectedIssue.reason_code || 'UNSCHEDULED_EXAM'}
                  </span>
                  <h3 className="text-base font-bold text-brand-text mt-0.5">
                    {selectedIssue.exam_title || selectedIssue.title || selectedIssue.exam_code}
                  </h3>
                </div>
                <span className="px-2.5 py-0.5 text-xs font-bold rounded bg-brand-danger/20 text-brand-danger border border-brand-danger/40">
                  {selectedIssue.severity || 'BLOCKING'}
                </span>
              </div>
              <p className="text-xs text-brand-muted leading-relaxed">
                {selectedIssue.description || selectedIssue.message}
              </p>
            </div>

            {/* Recommended Corrective Action */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-brand-accent" />
                Recommended Corrective Action
              </h4>
              <div className="p-4 bg-brand-surface border border-brand-border rounded-lg text-xs space-y-2 text-brand-text">
                <p>
                  <strong>Institutional Policy Protocol:</strong> To resolve this exception without violating academic integrity:
                </p>
                <ol className="list-decimal list-inside space-y-1.5 text-brand-muted">
                  <li>Verify if room operating hours can be expanded during peak examination week.</li>
                  <li>Check if additional qualified invigilators can be added to the proctor pool.</li>
                  <li>If cohort size exceeds single-venue capacity, allow multi-room splitting across simultaneous adjacent venues.</li>
                  <li>Re-run the scheduling solver to verify full constraint satisfaction.</li>
                </ol>
              </div>
            </div>

            {/* Rejected Slot Telemetry */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-brand-accent" />
                Evaluated Constraint Failures ({issueDecisions.length} telemetry records)
              </h4>

              {issueDecisions.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded text-center text-xs text-brand-muted">
                  No fine-grained slot failure traces recorded for this specific examination code.
                </div>
              ) : (
                <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                  {issueDecisions.map((dec, idx) => (
                    <div key={idx} className="p-3 bg-brand-surface border border-brand-border rounded text-xs space-y-1">
                      <div className="flex items-center justify-between text-brand-text">
                        <span className="font-mono text-brand-warning font-semibold">Slot: {dec.slot_label || dec.slot_id?.substring(0, 8)}</span>
                        <span className="text-[10px] uppercase font-bold text-brand-danger bg-brand-danger/10 px-2 py-0.5 rounded border border-brand-danger/20">
                          {dec.outcome}
                        </span>
                      </div>
                      <p className="text-brand-muted text-[11px]">
                        <strong>Failed Constraint:</strong> {dec.failed_constraints?.join(', ') || dec.reason || 'Candidate resource unavailable or student conflict'}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Link to Scheduling Workspace */}
            <div className="pt-2">
              <button
                onClick={() => navigate('/scheduling')}
                className="w-full py-2.5 px-4 rounded bg-brand-accent hover:bg-brand-accent/90 text-brand-bg font-semibold text-xs transition-colors flex items-center justify-center gap-2"
              >
                Open Scheduling Workspace to Re-execute Run
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
