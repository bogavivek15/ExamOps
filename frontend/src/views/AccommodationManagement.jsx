import React, { useState, useEffect } from 'react';
import { 
  Shield, Search, Filter, Clock, Accessibility, Eye, Lock,
  AlertTriangle, CheckCircle2, FileText, User, Calendar
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
  const { role } = useAuth();
  const [accommodations, setAccommodations] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
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
  }, [page, pageSize, search, typeFilter]);

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
      setError(err.message || 'Failed to load accommodations');
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
      setClinicalNotes(notesData);
    } catch (err) {
      console.error('Failed to load clinical notes:', err);
      setClinicalNotes({ documentation: 'Failed to retrieve notes or unauthorized.' });
    } finally {
      setLoadingNotes(false);
    }
  }

  const columns = [
    {
      header: 'Student',
      cell: (row) => (
        <div>
          <span className="font-mono text-brand-accent font-semibold block">{row.student_number}</span>
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
          {row.numeric_value ? `+${row.numeric_value} ${row.unit || 'min'}` : (row.feature_requirement || 'Compliant venue requirement')}
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
      header: 'Verification Status',
      cell: (row) => <StatusBadge status={row.status || 'ACTIVE'} />,
    },
    {
      header: 'Clinical Documentation',
      cell: (row) => (
        <button
          onClick={() => handleOpenNotes(row)}
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1.5"
        >
          <Lock className="w-3 h-3 text-brand-warning" />
          Inspect Notes
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
            <Shield className="w-5 h-5 text-brand-accent" />
            Accommodation Management
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Governance of student accessibility services, extra-time multipliers, and privacy-shielded clinical records.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Registered Accommodations"
          value={total}
          subtext="Active in Fall 2026"
          icon={Shield}
        />
        <MetricDisplay
          label="Extended Duration"
          value="45%"
          subtext="+25% or +50% time quota"
          icon={Clock}
        />
        <MetricDisplay
          label="Step-Free Access"
          value="35%"
          subtext="Assigned to accessible rooms"
          icon={Accessibility}
        />
        <MetricDisplay
          label="Privacy Protection"
          value="Active (FERPA)"
          subtext="Redacted for non-admin roles"
          icon={Lock}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-brand-muted" />
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setPage(1);
              }}
              className="bg-brand-elevated border border-brand-border rounded px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            >
              <option value="">All Accommodation Types</option>
              <option value="EXTENDED_TIME">Extended Time</option>
              <option value="ACCESSIBLE_ROOM">Accessible Room</option>
              <option value="SEPARATE_ROOM">Separate / Low Distraction</option>
              <option value="SPECIAL_EQUIPMENT">Special Equipment</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted">
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
          actionLabel="Retry"
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
        title="Accessibility Documentation"
        size="md"
      >
        {selectedAcc && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-lg p-4 space-y-2">
              <span className="text-xs font-mono text-brand-accent uppercase tracking-wider">
                {selectedAcc.student_number}
              </span>
              <h3 className="text-base font-bold text-brand-text">{selectedAcc.student_name}</h3>
              <p className="text-xs text-brand-muted">
                Type: <strong className="text-brand-text">{selectedAcc.accommodation_type}</strong>
              </p>
            </div>

            {/* Privacy Redaction Warning Banner */}
            <div className="p-3 bg-brand-warning/10 border border-brand-warning/30 rounded-lg flex items-start gap-3">
              <Lock className="w-5 h-5 text-brand-warning flex-shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <span className="font-bold text-brand-warning block">Confidential Accessibility Information</span>
                <span className="text-brand-muted block">
                  Pursuant to privacy regulations and academic ethics, medical and psychological evaluations are strictly restricted to authorized Academic Administrators.
                </span>
                <span className="text-[11px] font-mono text-brand-accent block mt-1">
                  Active Simulation Role: {role}
                </span>
              </div>
            </div>

            {/* Clinical Notes Body */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-brand-accent" />
                Physician & Accessibility Specialist Assessment
              </h4>

              {loadingNotes ? (
                <div className="text-xs text-brand-muted py-6 text-center">Decrypting authorization token...</div>
              ) : (
                <div className="p-4 bg-brand-surface border border-brand-border rounded-lg text-xs font-mono leading-relaxed text-brand-text">
                  {clinicalNotes?.clinical_notes || clinicalNotes?.notes || clinicalNotes?.documentation || (
                    <span className="text-brand-muted italic">
                      [REDACTED FOR PRIVACY - AUTHORIZED PERSONNEL ONLY]
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Invariant Note */}
            <div className="p-3 bg-brand-surface border border-brand-border rounded text-xs text-brand-muted space-y-1">
              <span className="font-semibold text-brand-text block">Scheduling Engine Guarantee</span>
              <p>
                The deterministic solver guarantees that any candidate with this accommodation is scheduled with adequate room capacity, required accessibility features, and required extra minutes.
              </p>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

