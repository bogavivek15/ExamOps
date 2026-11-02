import React, { useState, useEffect } from 'react';
import {
  Building2, Search, Filter, Users, Laptop, Accessibility,
  Clock, CheckCircle2, AlertTriangle, Eye
} from 'lucide-react';
import { api } from '../services/api';
import useDebounce from '../hooks/useDebounce';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Drawer from '../components/common/Drawer';
import MetricDisplay from '../components/common/MetricDisplay';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';

export default function RoomManagement() {
  const [rooms, setRooms] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [accessibleFilter, setAccessibleFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detail Drawer
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    loadRooms();
  }, [page, pageSize, debouncedSearch, accessibleFilter]);

  async function loadRooms() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listRooms({
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        is_accessible: accessibleFilter === 'true' ? true : accessibleFilter === 'false' ? false : undefined,
      });
      setRooms(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Unable to load room directory.');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(room) {
    setSelectedRoom(room);
    setDrawerOpen(true);
  }

  const columns = [
    {
      header: 'Room Code',
      accessor: 'room_code',
      className: 'font-mono text-brand-accent font-semibold',
    },
    {
      header: 'Building & Floor',
      cell: (row) => (
        <div>
          <span className="font-semibold text-brand-text block">{row.building || 'Main Campus'}</span>
          <span className="text-xs text-brand-muted">Floor {row.floor ?? '—'}</span>
        </div>
      ),
    },
    {
      header: 'Exam Capacity',
      cell: (row) => (
        <span className="flex items-center gap-1.5 font-bold text-brand-text">
          <Users className="w-3.5 h-3.5 text-brand-muted" />
          {row.capacity ?? row.exam_capacity ?? '—'} desks
        </span>
      ),
    },
    {
      header: 'Accessibility',
      cell: (row) => (
        row.is_accessible ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-success/15 text-brand-success border border-brand-success/30">
            <Accessibility className="w-3 h-3" />
            Accessible
          </span>
        ) : (
          <span className="text-xs text-brand-muted">Standard</span>
        )
      ),
    },
    {
      header: 'Equipment',
      cell: (row) => (
        <span className="text-xs text-brand-muted flex items-center gap-1">
          <Laptop className="w-3 h-3" />
          {row.has_computers ? 'Computers Installed' : 'Standard Desks'}
        </span>
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
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text hover:text-brand-accent transition-colors flex items-center gap-1"
          aria-label={`View details for ${row.room_code}`}
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
            <Building2 className="w-5 h-5 text-brand-accent" />
            Rooms & Facilities
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Manage examination rooms, desk capacities, accessibility features, and equipment.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricDisplay
          label="Total Rooms"
          value={total}
          subtext="Ready for exams"
          icon={Building2}
        />
        <MetricDisplay
          label="Total Exam Desks"
          value="4,280"
          subtext="Student seating capacity"
          icon={Users}
        />
        <MetricDisplay
          label="Accessible Rooms"
          value="34"
          subtext="Wheelchair & step-free access"
          icon={Accessibility}
        />
        <MetricDisplay
          label="Computer Labs"
          value="25"
          subtext="Workstations installed"
          icon={Laptop}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-[4px] p-3 sm:p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-full sm:max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search room code, building, floor..."
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
              value={accessibleFilter}
              onChange={(e) => {
                setAccessibleFilter(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-auto bg-brand-elevated border border-brand-border rounded-[4px] px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
              aria-label="Filter rooms by accessibility"
            >
              <option value="">All Rooms</option>
              <option value="true">Accessible Only</option>
              <option value="false">Standard Only</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted text-right">
          Showing <span className="font-semibold text-brand-text">{rooms.length}</span> of {total} rooms
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading room directory..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Rooms"
          description={error}
          actionLabel="Try Again"
          onAction={loadRooms}
        />
      ) : rooms.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No Rooms Found"
          description="No examination rooms match your filter criteria."
        />
      ) : (
        <DataTable
          columns={columns}
          data={rooms}
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
        title={`Room Details: ${selectedRoom?.room_code || ''}`}
        size="lg"
      >
        {selectedRoom && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-[4px] p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider font-semibold">
                    {selectedRoom.room_code}
                  </span>
                  <h3 className="text-base font-bold text-brand-text">
                    Building {selectedRoom.building}, Floor {selectedRoom.floor}
                  </h3>
                </div>
                <StatusBadge status={selectedRoom.status || 'ACTIVE'} />
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px]">
                <span className="text-xs text-brand-muted block">Exam Seating Capacity</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Users className="w-4 h-4 text-brand-accent" />
                  {selectedRoom.capacity ?? selectedRoom.exam_capacity ?? '—'} desks
                </span>
              </div>
              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px]">
                <span className="text-xs text-brand-muted block">Accessibility Status</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Accessibility className="w-4 h-4 text-brand-success" />
                  {selectedRoom.is_accessible ? 'Wheelchair Accessible' : 'Standard Room'}
                </span>
              </div>
            </div>

            {/* Operating Hours */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-brand-accent" />
                Operating Hours
              </h4>

              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px] text-xs space-y-2">
                <div className="flex items-center justify-between text-brand-text font-medium">
                  <span>Standard Daily Hours</span>
                  <span className="text-brand-accent font-mono">08:00 - 18:00</span>
                </div>
                <p className="text-brand-muted text-[11px]">
                  Exams are only scheduled in this room during these available hours.
                </p>
              </div>
            </div>

            {/* Hardware & Amenities */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Laptop className="w-3.5 h-3.5 text-brand-accent" />
                Installed Equipment
              </h4>

              <div className="p-3 bg-brand-surface border border-brand-border rounded-[4px] text-xs space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-brand-accent" />
                  <span className="text-brand-text">Projector & Screen</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-brand-accent" />
                  <span className="text-brand-text">Exam Monitoring Cameras</span>
                </div>
                {selectedRoom.has_computers && (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-brand-success" />
                    <span className="text-brand-text">Student Computer Workstations</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
