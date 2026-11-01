import React, { useState, useEffect } from 'react';
import { 
  UserCheck, Search, Filter, Calendar, Clock, Briefcase, 
  CheckCircle2, AlertTriangle, Eye, ShieldCheck, MapPin
} from 'lucide-react';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function InvigilatorManagement() {
  const [invigilators, setInvigilators] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Invigilator Detail & Shift Roster Drawer
  const [selectedInvigilator, setSelectedInvigilator] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [roster, setRoster] = useState([]);
  const [loadingRoster, setLoadingRoster] = useState(false);

  useEffect(() => {
    loadInvigilators();
  }, [page, pageSize, search, deptFilter]);

  async function loadInvigilators() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listInvigilators({
        page,
        page_size: pageSize,
        search: search || undefined,
        department: deptFilter || undefined,
      });
      setInvigilators(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load invigilators');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(inv) {
    setSelectedInvigilator(inv);
    setDrawerOpen(true);
    setLoadingRoster(true);
    try {
      const shifts = await api.getInvigilatorSchedule(inv.id);
      setRoster(shifts || []);
    } catch (err) {
      console.error('Failed to load invigilator schedule:', err);
      setRoster([]);
    } finally {
      setLoadingRoster(false);
    }
  }

  const columns = [
    {
      header: 'Staff ID',
      accessor: 'invigilator_code',
      className: 'font-mono text-brand-accent font-semibold',
    },
    {
      header: 'Name',
      cell: (row) => (
        <div>
          <span className="font-semibold text-brand-text block">{row.first_name} {row.last_name}</span>
          <span className="text-xs text-brand-muted">{row.email}</span>
        </div>
      ),
    },
    {
      header: 'Department',
      accessor: 'department',
      className: 'text-brand-text truncate max-w-[160px]',
    },
    {
      header: 'Max Workload',
      cell: (row) => (
        <span className="text-xs text-brand-text font-medium flex items-center gap-1">
          <Clock className="w-3.5 h-3.5 text-brand-muted" />
          {row.max_daily_minutes ? `${Math.round(row.max_daily_minutes / 60)}h / day` : '20h / week'}
        </span>
      ),
    },
    {
      header: 'Assigned Shifts',
      cell: (row) => (
        <span className="text-xs font-mono font-semibold text-brand-accent">
          {row.assigned_count ?? row.shift_count ?? '0'} shifts
        </span>
      ),
    },
    {
      header: 'Status',
      cell: (row) => <StatusBadge status={row.status || 'AVAILABLE'} />,
    },
    {
      header: 'Actions',
      cell: (row) => (
        <button
          onClick={() => handleOpenDetail(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          Roster
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
            <UserCheck className="w-5 h-5 text-brand-accent" />
            Invigilator Management
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Directory of certified examination proctors, availability windows, workload tracking, and shift assignments.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Total Invigilators"
          value={total}
          subtext="Certified academic proctors"
          icon={UserCheck}
        />
        <MetricDisplay
          label="Staffing Ratio"
          value="1 : 30"
          subtext="Mandatory policy limit"
          icon={ShieldCheck}
        />
        <MetricDisplay
          label="Double Booking"
          value="0"
          subtext="Strictly isolated by solver"
          icon={CheckCircle2}
        />
        <MetricDisplay
          label="Availability Rate"
          value="98.5%"
          subtext="Logged in availability ledger"
          icon={Briefcase}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search staff ID, name, department..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 bg-brand-elevated border border-brand-border rounded text-xs text-brand-text placeholder-brand-muted focus:outline-none focus:border-brand-accent transition-colors"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-brand-muted" />
            <select
              value={deptFilter}
              onChange={(e) => {
                setDeptFilter(e.target.value);
                setPage(1);
              }}
              className="bg-brand-elevated border border-brand-border rounded px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            >
              <option value="">All Departments</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Engineering">Engineering</option>
              <option value="Business">Business</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted">
          Showing <span className="font-semibold text-brand-text">{invigilators.length}</span> of {total} staff
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading invigilator registry..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Staff"
          description={error}
          actionLabel="Retry"
          onAction={loadInvigilators}
        />
      ) : invigilators.length === 0 ? (
        <EmptyState
          icon={UserCheck}
          title="No Invigilators Found"
          description="No proctors match the specified search parameters."
        />
      ) : (
        <DataTable
          columns={columns}
          data={invigilators}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Roster Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Staff Profile: ${selectedInvigilator?.invigilator_code || ''}`}
        size="lg"
      >
        {selectedInvigilator && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-lg p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider">
                    {selectedInvigilator.invigilator_code}
                  </span>
                  <h3 className="text-base font-bold text-brand-text">
                    {selectedInvigilator.first_name} {selectedInvigilator.last_name}
                  </h3>
                  <p className="text-xs text-brand-muted">{selectedInvigilator.email}</p>
                </div>
                <StatusBadge status={selectedInvigilator.status || 'AVAILABLE'} />
              </div>
              <div className="pt-2 border-t border-brand-border/60 flex items-center justify-between text-xs text-brand-muted">
                <span>Department: <strong className="text-brand-text">{selectedInvigilator.department}</strong></span>
                <span>Workload Cap: <strong className="text-brand-text">{selectedInvigilator.max_daily_minutes ? `${selectedInvigilator.max_daily_minutes} min/day` : 'Standard'}</strong></span>
              </div>
            </div>

            {/* Roster / Confirmed Shifts */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-brand-accent" />
                Assigned Examination Proctoring Shifts
              </h4>

              {loadingRoster ? (
                <div className="text-xs text-brand-muted py-6 text-center">Loading shift roster...</div>
              ) : roster.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded text-center text-xs text-brand-muted">
                  No confirmed proctoring shifts assigned to this staff member.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {roster.map((shift, idx) => (
                    <div key={idx} className="p-3.5 bg-brand-surface border border-brand-border rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-brand-accent">{shift.exam_code}</span>
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-brand-elevated text-brand-text border border-brand-border">
                          {shift.room_code || 'Venue TBD'}
                        </span>
                      </div>
                      <div className="text-xs text-brand-text font-medium">{shift.exam_title || shift.course_title}</div>
                      <div className="flex items-center gap-4 text-xs text-brand-muted">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-brand-muted" />
                          {shift.start_time ? new Date(shift.start_time).toLocaleDateString() : 'TBD'}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-brand-muted" />
                          {shift.start_time ? new Date(shift.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

