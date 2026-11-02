import React, { useState, useEffect } from 'react';
import { 
  UserCheck, Search, Filter, Calendar, Clock, Briefcase, 
  CheckCircle2, AlertTriangle, Eye, ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import useDebounce from '../hooks/useDebounce';
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

  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    loadInvigilators();
  }, [page, pageSize, debouncedSearch, deptFilter]);

  async function loadInvigilators() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listInvigilators({
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        department: deptFilter || undefined,
      });
      setInvigilators(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load invigilator directory.');
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
      header: 'Daily Limit',
      cell: (row) => (
        <span className="text-xs text-brand-text font-medium flex items-center gap-1">
          <Clock className="w-3.5 h-3.5 text-brand-muted" />
          {row.max_daily_minutes ? `${Math.round(row.max_daily_minutes / 60)}h / day` : '6h / day'}
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
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label={`View shifts for ${row.first_name} ${row.last_name}`}
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          View Shifts
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
            <UserCheck className="w-5 h-5 text-brand-accent" />
            Invigilators & Staff Schedules
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            View exam invigilators, track daily workloads, and check assigned exam shifts.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Invigilators"
          value={total}
          subtext="Exam supervision staff"
          icon={UserCheck}
        />
        <MetricDisplay
          label="Staffing Ratio"
          value="1 : 30"
          subtext="Standard policy limit"
          icon={ShieldCheck}
        />
        <MetricDisplay
          label="Schedule Clashes"
          value="0"
          subtext="Zero double-bookings"
          icon={CheckCircle2}
        />
        <MetricDisplay
          label="Staff Availability"
          value="98.5%"
          subtext="Ready to supervise"
          icon={Briefcase}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-full sm:max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search staff ID, name, department..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-brand-text placeholder-brand-muted focus:outline-none focus:border-brand-accent transition-colors"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-brand-muted shrink-0" />
            <select
              value={deptFilter}
              onChange={(e) => {
                setDeptFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
              aria-label="Filter by department"
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

        <div className="text-xs text-brand-muted text-right">
          Showing <span className="font-semibold text-brand-text">{invigilators.length}</span> of {total} staff
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading invigilator directory..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Staff"
          description={error}
          actionLabel="Try Again"
          onAction={loadInvigilators}
        />
      ) : invigilators.length === 0 ? (
        <EmptyState
          icon={UserCheck}
          title="No Invigilators Found"
          description="No staff members match your search criteria."
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
        title={`Invigilator Details: ${selectedInvigilator?.invigilator_code || ''}`}
        size="lg"
      >
        {selectedInvigilator && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider font-semibold">
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
                <span>Workload Limit: <strong className="text-brand-text">{selectedInvigilator.max_daily_minutes ? `${Math.round(selectedInvigilator.max_daily_minutes / 60)}h / day` : 'Standard (6h)'}</strong></span>
              </div>
            </div>

            {/* Roster / Confirmed Shifts */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-brand-accent" />
                Assigned Exam Shifts
              </h4>

              {loadingRoster ? (
                <div className="text-xs text-brand-muted py-6 text-center">Loading shift roster...</div>
              ) : roster.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-center text-xs text-brand-muted">
                  No exam shifts assigned to this staff member yet.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {roster.map((shift, idx) => (
                    <div key={idx} className="p-3.5 bg-brand-surface border border-brand-border rounded-[4px] space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-brand-accent">{shift.exam_code}</span>
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-brand-elevated text-brand-text border border-brand-border">
                          {shift.room_code || 'Venue TBD'}
                        </span>
                      </div>
                      <div className="text-xs text-brand-text font-medium">{shift.exam_title || shift.course_title}</div>
                      <div className="flex items-center gap-4 text-xs text-brand-muted flex-wrap">
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
