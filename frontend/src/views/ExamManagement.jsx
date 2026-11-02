import React, { useState, useEffect } from 'react';
import { 
  FileText, Search, Filter, Clock, Users, Laptop, 
  CheckCircle, AlertTriangle, Eye
} from 'lucide-react';
import { api } from '../services/api';
import useDebounce from '../hooks/useDebounce';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function ExamManagement() {
  const [exams, setExams] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detail Drawer
  const [selectedExam, setSelectedExam] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [examReqs, setExamReqs] = useState([]);
  const [loadingReqs, setLoadingReqs] = useState(false);

  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    loadExams();
  }, [page, pageSize, debouncedSearch, statusFilter]);

  async function loadExams() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listExams({
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        status: statusFilter || undefined,
      });
      setExams(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load examination catalog.');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(exam) {
    setSelectedExam(exam);
    setDrawerOpen(true);
    setLoadingReqs(true);
    try {
      const reqs = await api.getExamRequirements(exam.id);
      setExamReqs(reqs || []);
    } catch (err) {
      console.error('Failed to load exam requirements:', err);
      setExamReqs([]);
    } finally {
      setLoadingReqs(false);
    }
  }

  const columns = [
    {
      header: 'Exam Code',
      accessor: 'exam_code',
      className: 'font-mono text-brand-accent font-semibold',
    },
    {
      header: 'Course',
      cell: (row) => (
        <div>
          <span className="font-semibold text-brand-text">{row.course_code || 'General'}</span>
          <span className="text-xs text-brand-muted block truncate max-w-[200px]">{row.course_title || 'General Examination'}</span>
        </div>
      ),
    },
    {
      header: 'Exam Title',
      accessor: 'title',
      className: 'text-brand-text truncate max-w-[240px]',
    },
    {
      header: 'Duration',
      cell: (row) => (
        <span className="flex items-center gap-1.5 text-brand-text">
          <Clock className="w-3.5 h-3.5 text-brand-muted" />
          {row.base_duration_minutes || row.duration_minutes || 120} min
        </span>
      ),
    },
    {
      header: 'Enrolled Students',
      cell: (row) => (
        <span className="flex items-center gap-1.5 font-medium text-brand-text">
          <Users className="w-3.5 h-3.5 text-brand-muted" />
          {row.enrolled_count ?? row.enrolled_student_count ?? '—'}
        </span>
      ),
    },
    {
      header: 'Status',
      cell: (row) => <StatusBadge status={row.status || 'DRAFT'} />,
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
            <FileText className="w-5 h-5 text-brand-accent" />
            Examination Directory
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Browse and manage exams, room requirements, enrolled students, and durations.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Exams"
          value={total}
          subtext="In active term"
          icon={FileText}
        />
        <MetricDisplay
          label="Standard Duration"
          value="120 min"
          subtext="Typical exam length"
          icon={Clock}
        />
        <MetricDisplay
          label="Scheduled Batches"
          value="300"
          subtext="Active exam sessions"
          icon={Users}
        />
        <MetricDisplay
          label="Term Status"
          value="Active"
          subtext="Fall 2026 Semester"
          icon={CheckCircle}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-full sm:max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search exam code, course, title..."
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
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
              aria-label="Filter by exam status"
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="SCHEDULED">Scheduled</option>
              <option value="UNASSIGNED">Unassigned</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted text-right">
          Showing <span className="font-semibold text-brand-text">{exams.length}</span> of {total} exams
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading examination catalog..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Exams"
          description={error}
          actionLabel="Try Again"
          onAction={loadExams}
        />
      ) : exams.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No Examinations Found"
          description="No examination records match your search criteria."
        />
      ) : (
        <DataTable
          columns={columns}
          data={exams}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Detail Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Exam Details: ${selectedExam?.exam_code || ''}`}
        size="lg"
      >
        {selectedExam && (
          <div className="space-y-6">
            {/* Header info */}
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider font-semibold">
                    {selectedExam.exam_code}
                  </span>
                  <h3 className="text-base font-bold text-brand-text mt-0.5">{selectedExam.title}</h3>
                </div>
                <StatusBadge status={selectedExam.status || 'DRAFT'} />
              </div>
              <p className="text-xs text-brand-muted">
                Course: <span className="text-brand-text font-medium">{selectedExam.course_code} - {selectedExam.course_title}</span>
              </p>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px]">
                <span className="text-xs text-brand-muted block">Duration</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Clock className="w-4 h-4 text-brand-accent" />
                  {selectedExam.base_duration_minutes || selectedExam.duration_minutes || 120} minutes
                </span>
              </div>
              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px]">
                <span className="text-xs text-brand-muted block">Enrolled Students</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Users className="w-4 h-4 text-brand-accent" />
                  {selectedExam.enrolled_count ?? selectedExam.enrolled_student_count ?? '—'} students
                </span>
              </div>
            </div>

            {/* Structured Requirements */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Laptop className="w-3.5 h-3.5 text-brand-accent" />
                Room & Equipment Requirements
              </h4>
              {loadingReqs ? (
                <div className="text-xs text-brand-muted py-4 text-center">Loading requirements...</div>
              ) : examReqs.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-xs text-brand-muted text-center">
                  Standard classroom or hall. No specialized equipment needed.
                </div>
              ) : (
                <div className="space-y-2">
                  {examReqs.map((req, idx) => (
                    <div key={idx} className="p-3 bg-brand-surface border border-brand-border rounded-[4px] flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-2 h-2 rounded-full bg-brand-accent shrink-0" />
                        <div>
                          <span className="text-xs font-semibold text-brand-text block">{req.requirement_type}</span>
                          <span className="text-xs text-brand-muted">{req.requirement_value || req.value}</span>
                        </div>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-brand-elevated border border-brand-border text-brand-muted uppercase font-medium">
                        {req.is_mandatory !== false ? 'Mandatory' : 'Optional'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Academic Policies */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5 text-brand-accent" />
                Exam Scheduling Guidelines
              </h4>
              <ul className="text-xs text-brand-muted space-y-1.5 bg-brand-surface border border-brand-border rounded-[4px] p-3 list-disc list-inside">
                <li>No student has two exams scheduled at the same time.</li>
                <li>At least 1 invigilator for every 30 students (1:30 ratio).</li>
                <li>Students with approved support receive extra time and accessible rooms.</li>
              </ul>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
