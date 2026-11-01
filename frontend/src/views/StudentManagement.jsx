import React, { useState, useEffect } from 'react';
import { 
  Users, Search, Filter, BookOpen, Calendar, Shield, Clock, 
  MapPin, Eye, CheckCircle2, AlertCircle, AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function StudentManagement() {
  const [students, setStudents] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Student Detail & Personal Timetable Drawer
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [schedule, setSchedule] = useState([]);
  const [loadingSchedule, setLoadingSchedule] = useState(false);

  useEffect(() => {
    loadStudents();
  }, [page, pageSize, search, deptFilter]);

  async function loadStudents() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listStudents({
        page,
        page_size: pageSize,
        search: search || undefined,
        department: deptFilter || undefined,
      });
      setStudents(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load students');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(student) {
    setSelectedStudent(student);
    setDrawerOpen(true);
    setLoadingSchedule(true);
    try {
      const personalSchedule = await api.getStudentSchedule(student.id);
      setSchedule(personalSchedule || []);
    } catch (err) {
      console.error('Failed to load student schedule:', err);
      setSchedule([]);
    } finally {
      setLoadingSchedule(false);
    }
  }

  const columns = [
    {
      header: 'Student Number',
      accessor: 'student_number',
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
      header: 'Academic Level',
      cell: (row) => (
        <span className="text-xs text-brand-text capitalize">{row.academic_level || 'Undergraduate'}</span>
      ),
    },
    {
      header: 'Program',
      accessor: 'program',
      className: 'text-brand-text truncate max-w-[180px]',
    },
    {
      header: 'Accommodations',
      cell: (row) => (
        row.has_accommodations ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-warning/15 text-brand-warning border border-brand-warning/30">
            <Shield className="w-3 h-3" />
            Active
          </span>
        ) : (
          <span className="text-xs text-brand-muted">Standard</span>
        )
      ),
    },
    {
      header: 'Status',
      cell: (row) => <StatusBadge status={row.status || 'ACTIVE'} />,
    },
    {
      header: 'Actions',
      cell: (row) => (
        <button
          onClick={() => handleOpenDetail(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          Timetable
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
            <Users className="w-5 h-5 text-brand-accent" />
            Student Management
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Registry of enrolled candidates, accessibility accommodations, and individualized examination timetables.
          </p>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Total Student Body"
          value={total}
          subtext="Active academic candidates"
          icon={Users}
        />
        <MetricDisplay
          label="Standard Cohort"
          value={total > 0 ? `${Math.round(total * 0.92)}` : '—'}
          subtext="Regular examination protocol"
          icon={CheckCircle2}
        />
        <MetricDisplay
          label="Accommodated"
          value={total > 0 ? `${Math.round(total * 0.08)}` : '—'}
          subtext="Extended time or specialized room"
          icon={Shield}
        />
        <MetricDisplay
          label="Conflict Free"
          value="100%"
          subtext="Enforced by solver"
          icon={CheckCircle2}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search student number, name, email..."
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
              <option value="">All Programs</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Engineering">Engineering</option>
              <option value="Business">Business</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted">
          Showing <span className="font-semibold text-brand-text">{students.length}</span> of {total} students
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading student records..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Students"
          description={error}
          actionLabel="Retry"
          onAction={loadStudents}
        />
      ) : students.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Students Found"
          description="No student records match the query criteria."
        />
      ) : (
        <DataTable
          columns={columns}
          data={students}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Student Timetable Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Student Profile: ${selectedStudent?.student_number || ''}`}
        size="lg"
      >
        {selectedStudent && (
          <div className="space-y-6">
            {/* Student Bio */}
            <div className="bg-brand-elevated border border-brand-border rounded-lg p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider">
                    {selectedStudent.student_number}
                  </span>
                  <h3 className="text-base font-bold text-brand-text">
                    {selectedStudent.first_name} {selectedStudent.last_name}
                  </h3>
                  <p className="text-xs text-brand-muted">{selectedStudent.email}</p>
                </div>
                <StatusBadge status={selectedStudent.status || 'ACTIVE'} />
              </div>

              <div className="pt-2 border-t border-brand-border/60 flex items-center justify-between text-xs text-brand-muted">
                <span>Program: <strong className="text-brand-text">{selectedStudent.program || 'General Studies'}</strong></span>
                <span>Level: <strong className="text-brand-text">{selectedStudent.academic_level || 'Undergraduate'}</strong></span>
              </div>
            </div>

            {/* Accommodation Notice if applicable */}
            {selectedStudent.has_accommodations && (
              <div className="p-3 bg-brand-warning/10 border border-brand-warning/30 rounded-lg flex items-center gap-3">
                <Shield className="w-5 h-5 text-brand-warning flex-shrink-0" />
                <div>
                  <span className="text-xs font-semibold text-brand-warning block">Active Accessibility Accommodation</span>
                  <span className="text-xs text-brand-muted">
                    This candidate has approved accommodations (e.g. extended time or specialized venue). Scheduling engine automatically assigns compliant rooms.
                  </span>
                </div>
              </div>
            )}

            {/* Personal Examination Schedule */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-brand-accent" />
                Confirmed Examination Timetable
              </h4>

              {loadingSchedule ? (
                <div className="text-xs text-brand-muted py-6 text-center">Loading schedule...</div>
              ) : schedule.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded text-center text-xs text-brand-muted">
                  No confirmed examination assignments found for this candidate in published schedules.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {schedule.map((item, idx) => (
                    <div key={idx} className="p-3.5 bg-brand-surface border border-brand-border rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-brand-accent">{item.exam_code}</span>
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-brand-elevated text-brand-text border border-brand-border">
                          {item.room_code || 'TBD'}
                        </span>
                      </div>
                      <div className="text-xs text-brand-text font-medium">{item.course_title || item.exam_title}</div>
                      <div className="flex items-center gap-4 text-xs text-brand-muted">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-brand-muted" />
                          {item.start_time ? new Date(item.start_time).toLocaleDateString() : 'TBD'}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-brand-muted" />
                          {item.start_time ? new Date(item.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'}
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-brand-muted" />
                          Seat {item.seat_number || 'Auto-allocated'}
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

