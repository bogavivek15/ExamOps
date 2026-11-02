import React, { useState, useEffect } from 'react';
import {
  Shield, Filter, Clock, Accessibility, Lock,
  AlertTriangle, FileText
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function AccommodationManagement() {
  const { currentRole } = useAuth();
  const [accommodations, setAccommodations] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Notes inspection drawer
  const [selectedAcc, setSelectedAcc] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [clinicalNotes, setClinicalNotes] = useState(null);
  const [loadingNotes, setLoadingNotes] = useState(false);

  useEffect(() => {
    loadAccommodations();
  }, [page, pageSize, typeFilter]);

  async function loadAccommodations() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listAccommodations({
        page,
        page_size: pageSize,
        accommodation_type: typeFilter || undefined,
      });
      setAccommodations(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load accommodations.');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenNotes(acc) {
    setSelectedAcc(acc);
    setDrawerOpen(true);
    setLoadingNotes(true);
    try {
      const notesData = await api.getAccommodationNotes(acc.id);
      const noteItem = Array.isArray(notesData) ? (notesData[0] || {}) : (notesData || {});
      setClinicalNotes(noteItem);
    } catch (err) {
      console.error('Failed to load notes:', err);
      setClinicalNotes({ documentation: 'Unable to retrieve notes or unauthorized.' });
    } finally {
      setLoadingNotes(false);
    }
  }

  const columns = [
    {
      header: 'Student',
      cell: (row) => (
        <div>
          <span className="font-mono text-brand-accent font-semibold block">{row.student_number || row.student_code}</span>
          <span className="text-xs text-brand-text font-medium">{row.student_name}</span>
        </div>
      ),
    },
    {
      header: 'Accommodation Type',
      cell: (row) => (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-semibold bg-brand-elevated border border-brand-border text-brand-text">
          <Shield className="w-3.5 h-3.5 text-brand-accent" />
          {row.accommodation_type?.replace(/_/g, ' ')}
        </span>
      ),
    },
    {
      header: 'Specification',
      cell: (row) => (
        <span className="text-xs text-brand-text font-medium">
          {row.numeric_value ? `+${row.numeric_value} ${row.unit || 'min'}` : (row.feature_requirement || 'Accessible venue requirement')}
        </span>
      ),
    },
    {
      header: 'Effective Period',
      cell: (row) => (
        <span className="text-xs text-brand-muted font-mono">
          {row.effective_start ? new Date(row.effective_start).toLocaleDateString() : 'Continuous'}
        </span>
      ),
    },
    {
      header: 'Status',
      cell: (row) => <StatusBadge status={row.status || 'ACTIVE'} />,
    },
    {
      header: 'Confidential Notes',
      cell: (row) => (
        <button
          onClick={() => handleOpenNotes(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1.5"
          aria-label={`View confidential notes for ${row.student_name}`}
        >
          <Lock className="w-3 h-3 text-brand-warning" />
          View Notes
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
            <Shield className="w-5 h-5 text-brand-accent" />
            Student Accommodations & Support
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Manage student accessibility needs, exam extra time, and specialized room support.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Active Accommodations"
          value={total}
          subtext="Fall 2026 Term"
          icon={Shield}
        />
        <MetricDisplay
          label="Extra Time Requests"
          value="45%"
          subtext="+25% or +50% extra minutes"
          icon={Clock}
        />
        <MetricDisplay
          label="Accessible Seating"
          value="35%"
          subtext="Ground-floor or elevator access"
          icon={Accessibility}
        />
        <MetricDisplay
          label="Privacy Shield"
          value="Active"
          subtext="Medical notes protected"
          icon={Lock}
        />
      </div>

      {/* Filter Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-brand-muted shrink-0" />
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
            className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            aria-label="Filter by accommodation type"
          >
            <option value="">All Accommodation Types</option>
            <option value="EXTENDED_TIME">Extended Time</option>
            <option value="ACCESSIBLE_ROOM">Accessible Room</option>
            <option value="SEPARATE_ROOM">Separate / Low Distraction</option>
            <option value="SPECIAL_EQUIPMENT">Special Equipment</option>
          </select>
        </div>

        <div className="text-xs text-brand-muted text-right">
          Showing <span className="font-semibold text-brand-text">{accommodations.length}</span> of {total} records
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading accommodation records..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Accommodations"
          description={error}
          actionLabel="Try Again"
          onAction={loadAccommodations}
        />
      ) : accommodations.length === 0 ? (
        <EmptyState
          icon={Shield}
          title="No Accommodations Found"
          description="No accessibility accommodation records found matching the filter."
        />
      ) : (
        <DataTable
          columns={columns}
          data={accommodations}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}

      {/* Clinical Notes Drawer */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Accessibility Support Details"
        size="md"
      >
        {selectedAcc && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-2">
              <span className="text-xs font-mono text-brand-accent uppercase tracking-wider font-semibold">
                {selectedAcc.student_number || selectedAcc.student_code}
              </span>
              <h3 className="text-base font-bold text-brand-text">{selectedAcc.student_name}</h3>
              <p className="text-xs text-brand-muted">
                Type: <strong className="text-brand-text">{selectedAcc.accommodation_type}</strong>
              </p>
            </div>

            {/* Privacy Redaction Warning Banner */}
            <div className="p-3 bg-brand-warning/10 border border-brand-warning/30 rounded-[4px] flex items-start gap-3">
              <Lock className="w-5 h-5 text-brand-warning shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <span className="font-bold text-brand-warning block">Confidential Information</span>
                <span className="text-brand-muted block">
                  Medical and support details are confidential and visible only to authorized administrators.
                </span>
                <span className="text-[11px] font-mono text-brand-accent block mt-1">
                  Current Role: {currentRole}
                </span>
              </div>
            </div>

            {/* Clinical Notes Body */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-brand-accent" />
                Confidential Support Notes
              </h4>

              {loadingNotes ? (
                <div className="text-xs text-brand-muted py-6 text-center">Loading confidential notes...</div>
              ) : (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-[4px] text-xs font-mono leading-relaxed text-brand-text overflow-x-auto">
                  {clinicalNotes?.clinical_notes || clinicalNotes?.notes || clinicalNotes?.documentation || (
                    <span className="text-brand-muted italic">
                      [Restricted for Privacy: Only Administrators can view medical details]
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Invariant Note */}
            <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px] text-xs text-brand-muted space-y-1">
              <span className="font-semibold text-brand-text block">Timetable Guarantee</span>
              <p>
                The scheduler guarantees students receive extra time and accessible rooms automatically.
              </p>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
