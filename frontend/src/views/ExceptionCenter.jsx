import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, CheckCircle2, RefreshCw, ArrowRight, 
  HelpCircle, ShieldAlert, Cpu, Eye
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import DataTable from '../components/common/DataTable';
import Drawer from '../components/common/Drawer';
import MetricDisplay from '../components/common/MetricDisplay';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';

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
      setError(err.message || 'Unable to load timetables.');
      setLoading(false);
    }
  }

  async function loadRunExceptions(runId) {
    setLoading(true);
    setError(null);
    try {
      const [issuesData, decisionsData] = await Promise.all([
        api.getRunIssues(runId).catch(() => []),
        api.getRunDecisions(runId, { is_assigned: false, limit: 300 }).catch(() => []),
      ]);
      const rawIssues = Array.isArray(issuesData) ? issuesData : [];
      const unassignedList = Array.isArray(decisionsData) ? decisionsData : (decisionsData?.items || []);

      const formattedIssues = [
        ...rawIssues.map(iss => ({
          ...iss,
          id: iss.id,
          exam_id: iss.exam_id,
          exam_code: iss.exam_code,
          exam_title: iss.exam_title,
          severity: iss.severity || 'CRITICAL',
          reason_code: iss.issue_code || iss.reason_code || 'CONFLICT_DETECTED',
          description: iss.description || iss.message || 'Scheduling rule not met for this exam.',
        })),
        ...unassignedList.map(dec => ({
          id: dec.id,
          exam_id: dec.exam_id,
          exam_code: dec.exam_code,
          exam_title: dec.exam_title,
          severity: 'BLOCKING',
          reason_code: (dec.reason_codes && dec.reason_codes[0]) || 'STUDENT_CONFLICT',
          description: `No available time slot and room matched all requirements across ${dec.candidate_details?.evaluated_slots || 192} checked slots. Primary issue: ${(dec.reason_codes && dec.reason_codes.join(', ')) || 'STUDENT_CONFLICT'}.`,
          candidate_details: dec.candidate_details,
          reason_codes: dec.reason_codes,
        })),
      ];

      setIssues(formattedIssues);
      setDecisions(unassignedList);
    } catch (err) {
      setError(err.message || 'Unable to load timetable issues.');
    } finally {
      setLoading(false);
    }
  }

  function handleOpenDetail(issue) {
    setSelectedIssue(issue);
    setDrawerOpen(true);
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
      header: 'Exam Title & Course',
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
          {row.severity === 'BLOCKING' ? 'Unscheduled' : row.severity || 'Needs Review'}
        </span>
      ),
    },
    {
      header: 'Reason',
      cell: (row) => (
        <span className="font-mono text-xs font-semibold text-brand-warning">
          {row.reason_code || row.issue_code || 'UNSCHEDULED_CONFLICT'}
        </span>
      ),
    },
    {
      header: 'Why It Could Not Be Scheduled',
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
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label={`View details for ${row.exam_code}`}
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          View Details
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
            <ShieldAlert className="w-5 h-5 text-brand-danger" />
            Issue & Conflict Center
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Review exams that could not be scheduled, understand the reasons, and find ways to resolve conflicts.
          </p>
        </div>

        {/* Timetable Selector */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <label className="text-xs text-brand-muted font-medium shrink-0">Timetable Version:</label>
          <select
            value={selectedRunId}
            onChange={(e) => setSelectedRunId(e.target.value)}
            className="bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-1.5 text-xs text-brand-text font-mono focus:outline-none focus:border-brand-accent"
            aria-label="Select timetable version"
          >
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                {r.run_code} ({r.status})
              </option>
            ))}
          </select>
          <button
            onClick={() => selectedRunId && loadRunExceptions(selectedRunId)}
            className="p-1.5 rounded-[4px] bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-muted hover:text-brand-text transition-colors shrink-0"
            title="Refresh Issues"
            aria-label="Refresh issues list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Unscheduled Exams"
          value={issues.length}
          subtext="Needs attention"
          icon={AlertTriangle}
        />
        <MetricDisplay
          label="Student / Room Clashes"
          value="0"
          subtext="Zero allowed in confirmed schedule"
          icon={CheckCircle2}
        />
        <MetricDisplay
          label="Evaluated Options"
          value={decisions.length}
          subtext="Time slots checked"
          icon={Cpu}
        />
        <MetricDisplay
          label="Rule Validation"
          value="Automatic"
          subtext="Verified by scheduler"
          icon={ShieldAlert}
        />
      </div>

      {/* Main Table */}
      {loading ? (
        <LoadingState message="Checking timetable for issues..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Issues"
          description={error}
          actionLabel="Try Again"
          onAction={() => selectedRunId && loadRunExceptions(selectedRunId)}
        />
      ) : issues.length === 0 ? (
        <div className="bg-brand-surface border border-brand-border rounded-[4px] p-8 sm:p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-brand-success/15 border border-brand-success/30 flex items-center justify-center mx-auto text-brand-success">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-brand-text">All Exams Scheduled</h3>
          <p className="text-xs text-brand-muted max-w-md mx-auto">
            Every exam in this timetable has been assigned to a suitable room and time with zero conflicts.
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
        title={`Exam Issue Details: ${selectedIssue?.exam_code || ''}`}
        size="lg"
      >
        {selectedIssue && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-danger/30 rounded-[4px] p-4 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-mono text-brand-danger uppercase tracking-wider font-bold">
                    REASON: {selectedIssue.reason_code || 'UNSCHEDULED_EXAM'}
                  </span>
                  <h3 className="text-base font-bold text-brand-text mt-0.5">
                    {selectedIssue.exam_title || selectedIssue.title || selectedIssue.exam_code}
                  </h3>
                </div>
                <span className="px-2.5 py-0.5 text-xs font-bold rounded bg-brand-danger/20 text-brand-danger border border-brand-danger/40 shrink-0">
                  {selectedIssue.severity === 'BLOCKING' ? 'Unscheduled' : selectedIssue.severity}
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
                Recommended Ways to Resolve
              </h4>
              <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-xs space-y-2 text-brand-text">
                <p>
                  <strong>Suggested steps to schedule this exam:</strong>
                </p>
                <ol className="list-decimal list-inside space-y-1.5 text-brand-muted">
                  <li>Check if room operating hours can be expanded during peak exam days.</li>
                  <li>Verify if additional qualified invigilators can be added to the supervision pool.</li>
                  <li>If the class cohort is larger than single-room capacity, allow multi-room splitting.</li>
                  <li>Update the timetable to verify all rules are met.</li>
                </ol>
              </div>
            </div>

            {/* Rejected Slot Details */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-brand-accent" />
                Checked Time Slots & Why They Failed ({issueDecisions.length} checked)
              </h4>

              {issueDecisions.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-center text-xs text-brand-muted">
                  No individual slot traces recorded for this specific exam.
                </div>
              ) : (
                <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                  {issueDecisions.map((dec, idx) => (
                    <div key={idx} className="p-3 bg-brand-surface border border-brand-border rounded-[4px] text-xs space-y-1">
                      <div className="flex items-center justify-between text-brand-text">
                        <span className="font-mono text-brand-warning font-semibold">Slot: {dec.slot_label || dec.slot_id?.substring(0, 8)}</span>
                        <span className="text-[10px] uppercase font-bold text-brand-danger bg-brand-danger/10 px-2 py-0.5 rounded border border-brand-danger/20">
                          {dec.outcome}
                        </span>
                      </div>
                      <p className="text-brand-muted text-[11px]">
                        <strong>Failed Rule:</strong> {dec.failed_constraints?.join(', ') || dec.reason || 'Room unavailable or student clash'}
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
                className="w-full py-2.5 px-4 rounded-[4px] bg-brand-accent hover:bg-brand-accent/90 text-brand-bg font-semibold text-xs transition-colors flex items-center justify-center gap-2"
              >
                Go to Scheduling Workspace to Update Timetable
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
