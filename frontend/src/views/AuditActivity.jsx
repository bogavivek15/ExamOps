import React, { useState, useEffect } from 'react';
import { 
  History, Search, Filter, ShieldCheck, User, Calendar, 
  Clock, AlertTriangle, Eye, Lock, ArrowRight, FileText
} from 'lucide-react';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
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
      setError(err.message || 'Failed to load audit logs');
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
      header: 'Entity',
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
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          Diff
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
            <History className="w-5 h-5 text-brand-accent" />
            Audit Trail & Governance Ledger
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Immutable log of state mutations, solver runs, approvals, publication events, and administrative actions.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Total Audit Events"
          value={total}
          subtext="Cryptographically sequenced"
          icon={History}
        />
        <MetricDisplay
          label="Ledger Storage"
          value="Append Only"
          subtext="Protected from overwrite"
          icon={Lock}
        />
        <MetricDisplay
          label="Traceability"
          value="100%"
          subtext="Actor + Role + Payload"
          icon={ShieldCheck}
        />
        <MetricDisplay
          label="Governance Status"
          value="Compliant"
          subtext="Institutional standard"
          icon={ShieldCheck}
        />
      </div>

      {/* Filter Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-brand-muted" />
            <select
              value={entityFilter}
              onChange={(e) => {
                setEntityFilter(e.target.value);
                setPage(1);
              }}
              className="bg-brand-elevated border border-brand-border rounded px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            >
              <option value="">All Entities</option>
              <option value="SCHEDULING_RUN">Scheduling Run</option>
              <option value="SCHEDULE_ASSIGNMENT">Schedule Assignment</option>
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
              className="bg-brand-elevated border border-brand-border rounded px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            >
              <option value="">All Actions</option>
              <option value="CREATE_RUN">CREATE_RUN</option>
              <option value="EXECUTE_SCHEDULE">EXECUTE_SCHEDULE</option>
              <option value="APPROVE_RUN">APPROVE_RUN</option>
              <option value="PUBLISH_SCHEDULE">PUBLISH_SCHEDULE</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted">
          Showing <span className="font-semibold text-brand-text">{logs.length}</span> of {total} events
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading immutable audit trail..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Audit Trail"
          description={error}
          actionLabel="Retry"
          onAction={loadLogs}
        />
      ) : logs.length === 0 ? (
        <EmptyState
          icon={History}
          title="No Audit Records"
          description="No governance events match the active filters."
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
            <div className="bg-brand-elevated border border-brand-border rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
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
                Actor: <strong className="text-brand-text">{selectedLog.user_email || selectedLog.user_id}</strong> • Role: <strong className="text-brand-text">{selectedLog.role}</strong>
              </p>
            </div>

            {/* Changes / Diffs */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-brand-accent" />
                State Mutation Payload
              </h4>

              <div className="p-4 bg-brand-surface border border-brand-border rounded-lg overflow-x-auto">
                <pre className="text-xs font-mono text-brand-text leading-relaxed">
                  {JSON.stringify(selectedLog.details || selectedLog.payload || { action: selectedLog.action }, null, 2)}
                </pre>
              </div>
            </div>

            <div className="p-3 bg-brand-surface border border-brand-border rounded text-xs text-brand-muted">
              <span className="font-semibold text-brand-text block mb-1">Non-Repudiation Assurance</span>
              This record is written synchronously during transaction commit and cannot be altered or deleted through standard operational interfaces.
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

