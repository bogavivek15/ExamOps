import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Search, Filter, Users, Calendar, Layers,
  CheckCircle2, AlertTriangle, Eye
} from 'lucide-react';
import { api } from '../services/api';
import useDebounce from '../hooks/useDebounce';
import DataTable from '../components/ui/DataTable';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function CourseManagement() {
  const [courses, setCourses] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Enrollments Drawer
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [enrollments, setEnrollments] = useState([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(false);

  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    loadCourses();
  }, [page, pageSize, debouncedSearch, deptFilter]);

  async function loadCourses() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listCourses({
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        department: deptFilter || undefined,
      });
      setCourses(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load course catalog.');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(course) {
    setSelectedCourse(course);
    setDrawerOpen(true);
    setLoadingEnrollments(true);
    try {
      const res = await api.listEnrollments({ course_id: course.id, page_size: 50 });
      setEnrollments(res.items || []);
    } catch (err) {
      console.error('Failed to load course enrollments:', err);
      setEnrollments([]);
    } finally {
      setLoadingEnrollments(false);
    }
  }

  const columns = [
    {
      header: 'Course Code',
      accessor: 'course_code',
      className: 'font-mono text-brand-accent font-semibold',
    },
    {
      header: 'Course Title',
      cell: (row) => row.name || row.title || 'Course Unit',
      className: 'text-brand-text font-medium truncate max-w-[240px]',
    },
    {
      header: 'Department',
      accessor: 'department',
      className: 'text-brand-text truncate max-w-[160px]',
    },
    {
      header: 'Credits',
      cell: (row) => (
        <span className="text-xs text-brand-muted font-mono">{row.credits || 3} Credits</span>
      ),
    },
    {
      header: 'Enrolled Students',
      cell: (row) => (
        <span className="flex items-center gap-1.5 font-medium text-brand-text">
          <Users className="w-3.5 h-3.5 text-brand-muted" />
          {row.enrolled_count ?? row.enrollment_count ?? '—'}
        </span>
      ),
    },
    {
      header: 'Actions',
      cell: (row) => (
        <button
          onClick={() => handleOpenDetail(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label={`View enrolled students for ${row.course_code}`}
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          View Enrollments
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
            <BookOpen className="w-5 h-5 text-brand-accent" />
            Courses & Enrollments
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Browse academic courses, student enrollments, and department offerings.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Courses"
          value={total}
          subtext="Active in Fall 2026"
          icon={BookOpen}
        />
        <MetricDisplay
          label="Academic Term"
          value="FALL-2026"
          subtext="Standard semester"
          icon={Calendar}
        />
        <MetricDisplay
          label="Class Size Distribution"
          value="High"
          subtext="Across all departments"
          icon={Layers}
        />
        <MetricDisplay
          label="Roster Status"
          value="Ready"
          subtext="Course list confirmed for scheduling"
          icon={CheckCircle2}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-full sm:max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search course code, title, department..."
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
          Showing <span className="font-semibold text-brand-text">{courses.length}</span> of {total} courses
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading course catalog..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Courses"
          description={error}
          actionLabel="Try Again"
          onAction={loadCourses}
        />
      ) : courses.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No Courses Found"
          description="No course records match your filter criteria."
        />
      ) : (
        <DataTable
          columns={columns}
          data={courses}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Course Enrollments Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Course: ${selectedCourse?.course_code || ''}`}
        size="lg"
      >
        {selectedCourse && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-2">
              <span className="text-xs font-mono text-brand-accent uppercase tracking-wider font-semibold">
                {selectedCourse.course_code}
              </span>
              <h3 className="text-base font-bold text-brand-text">{selectedCourse.title || selectedCourse.name}</h3>
              <p className="text-xs text-brand-muted">
                Department: <strong className="text-brand-text">{selectedCourse.department}</strong> • Credits: <strong className="text-brand-text">{selectedCourse.credits || 3}</strong>
              </p>
            </div>

            {/* Enrollments List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-brand-accent" />
                  Enrolled Students ({enrollments.length})
                </h4>
              </div>

              {loadingEnrollments ? (
                <div className="text-xs text-brand-muted py-6 text-center">Loading enrollments...</div>
              ) : enrollments.length === 0 ? (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-center text-xs text-brand-muted">
                  No students currently enrolled in this course.
                </div>
              ) : (
                <div className="max-h-[460px] overflow-y-auto space-y-2 pr-1">
                  {enrollments.map((enr, idx) => (
                    <div key={idx} className="p-2.5 bg-brand-surface border border-brand-border rounded-[4px] flex items-center justify-between text-xs">
                      <div>
                        <span className="font-mono text-brand-accent font-semibold mr-2">{enr.student_number || enr.student_code}</span>
                        <span className="text-brand-text font-medium">{enr.student_name || `${enr.first_name || ''} ${enr.last_name || ''}`}</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-brand-elevated text-brand-muted uppercase font-medium">
                        {enr.enrollment_status || 'Enrolled'}
                      </span>
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
