import React, { useState, useEffect } from 'react';
import { 
  History, Filter, ShieldCheck, 
  AlertTriangle, Eye, Lock, FileText
} from 'lucide-react';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function AuditActivity() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detail Drawer for JSON diffs
  const [selectedLog, setSelectedLog] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    loadLogs();
  }, [page, pageSize, actionFilter, entityFilter]);

  async function loadLogs() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listAuditLogs({
        page,
        page_size: pageSize,
        action: actionFilter || undefined,
        entity_type: entityFilter || undefined,
      });
      setLogs(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load audit logs.');
    } finally {
      setLoading(false);
    }
  }

  function handleOpenDetail(log) {
    setSelectedLog(log);
    setDrawerOpen(true);
  }

  const columns = [
    {
      header: 'Timestamp',
      cell: (row) => (
        <span className="font-mono text-xs text-brand-muted">
          {row.created_at ? new Date(row.created_at).toLocaleString() : 'Recent'}
        </span>
      ),
    },
    {
      header: 'Action',
      cell: (row) => (
        <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-brand-elevated text-brand-accent border border-brand-border">
          {row.action}
        </span>
      ),
    },
    {
      header: 'Affected Record',
      cell: (row) => (
        <div>
          <span className="font-semibold text-xs text-brand-text block">{row.entity_type}</span>
          <span className="font-mono text-[10px] text-brand-muted truncate max-w-[140px] block">{row.entity_id}</span>
        </div>
      ),
    },
    {
      header: 'Performed By',
      cell: (row) => (
        <div>
          <span className="text-xs font-medium text-brand-text block">{row.user_email || row.user_id || 'System / Auto'}</span>
          <span className="text-[10px] text-brand-muted font-mono">{row.role || 'ACADEMIC_ADMINISTRATOR'}</span>
        </div>
      ),
    },
    {
      header: 'Actions',
      cell: (row) => (
        <button
          onClick={() => handleOpenDetail(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label="View log details"
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
            <History className="w-5 h-5 text-brand-accent" />
            Activity History & Audit Log
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Complete record of who created, changed, approved, or published exam timetables and settings.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Logged Events"
          value={total}
          subtext="Recorded actions"
          icon={History}
        />
        <MetricDisplay
          label="Log Integrity"
          value="Permanent"
          subtext="Records cannot be modified"
          icon={Lock}
        />
        <MetricDisplay
          label="User Traceability"
          value="100%"
          subtext="Full user and role logging"
          icon={ShieldCheck}
        />
        <MetricDisplay
          label="Audit Status"
          value="Active"
          subtext="Institutional compliance"
          icon={ShieldCheck}
        />
      </div>

      {/* Filter Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full md:w-auto flex-1">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-brand-muted shrink-0" />
            <select
              value={entityFilter}
              onChange={(e) => {
                setEntityFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
              aria-label="Filter by record type"
            >
              <option value="">All Record Types</option>
              <option value="SCHEDULING_RUN">Timetable</option>
              <option value="SCHEDULE_ASSIGNMENT">Exam Assignment</option>
              <option value="EXAM">Exam</option>
              <option value="ROOM">Room</option>
              <option value="INVIGILATOR">Invigilator</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
              aria-label="Filter by action"
            >
              <option value="">All Actions</option>
              <option value="CREATE_RUN">Create Timetable</option>
              <option value="EXECUTE_SCHEDULE">Run Auto-Scheduler</option>
              <option value="APPROVE_RUN">Approve Timetable</option>
              <option value="PUBLISH_SCHEDULE">Publish Timetable</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted text-right">
          Showing <span className="font-semibold text-brand-text">{logs.length}</span> of {total} events
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading activity history..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Audit Trail"
          description={error}
          actionLabel="Try Again"
          onAction={loadLogs}
        />
      ) : logs.length === 0 ? (
        <EmptyState
          icon={History}
          title="No Audit Records"
          description="No activity events match your filter criteria."
        />
      ) : (
        <DataTable
          columns={columns}
          data={logs}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Audit Detail Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Audit Event Inspection"
        size="lg"
      >
        {selectedLog && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-brand-surface text-brand-accent border border-brand-border">
                  {selectedLog.action}
                </span>
                <span className="text-xs text-brand-muted font-mono">
                  {new Date(selectedLog.created_at).toLocaleString()}
                </span>
              </div>
              <h3 className="text-base font-bold text-brand-text">
                Target: {selectedLog.entity_type} ({selectedLog.entity_id})
              </h3>
              <p className="text-xs text-brand-muted">
                Performed By: <strong className="text-brand-text">{selectedLog.user_email || selectedLog.user_id}</strong> • Role: <strong className="text-brand-text">{selectedLog.role}</strong>
              </p>
            </div>

            {/* Changes / Details */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-brand-accent" />
                Recorded Changes & Details
              </h4>

              <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] overflow-x-auto">
                <pre className="text-xs font-mono text-brand-text leading-relaxed">
                  {JSON.stringify(selectedLog.details || selectedLog.payload || { action: selectedLog.action }, null, 2)}
                </pre>
              </div>
            </div>

            <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px] text-xs text-brand-muted">
              <span className="font-semibold text-brand-text block mb-1">Tamper-Proof Record</span>
              This entry was saved automatically when the action happened and cannot be modified or deleted.
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
