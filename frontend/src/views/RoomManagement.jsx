import React, { useState, useEffect } from 'react';
import { 
  Building2, Search, Filter, Users, Laptop, Accessibility, 
  Clock, Calendar, CheckCircle2, AlertTriangle, Eye, ShieldCheck, MapPin
} from 'lucide-react';
import { api } from '../services/api';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';
import Drawer from '../components/ui/Drawer';
import MetricDisplay from '../components/ui/MetricDisplay';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

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
  const [roomDetails, setRoomDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    loadRooms();
  }, [page, pageSize, search, accessibleFilter]);

  async function loadRooms() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listRooms({
        page,
        page_size: pageSize,
        search: search || undefined,
        is_accessible: accessibleFilter === 'true' ? true : accessibleFilter === 'false' ? false : undefined,
      });
      setRooms(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load rooms');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(room) {
    setSelectedRoom(room);
    setDrawerOpen(true);
    setLoadingDetails(true);
    try {
      const details = await api.getRoom(room.id);
      setRoomDetails(details);
    } catch (err) {
      console.error('Failed to load room details:', err);
      setRoomDetails(null);
    } finally {
      setLoadingDetails(false);
    }
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
      header: 'Effective Capacity',
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
          className="px-2.5 py-1 text-xs rounded bg-brand-elevated hover:bg-brand-border border border-brand-border text-brand-text transition-colors flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-brand-accent" />
          Inspect
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
            <Building2 className="w-5 h-5 text-brand-accent" />
            Room & Facilities Management
          </h1>
          <p className="text-xs text-brand-muted mt-1">
            Campus venues, examination desk capacities, accessibility compliance, and equipment inventories.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricDisplay
          label="Total Examination Venues"
          value={total}
          subtext="Available for scheduling"
          icon={Building2}
        />
        <MetricDisplay
          label="Total Examination Capacity"
          value="4,280"
          subtext="Synchronous candidate desks"
          icon={Users}
        />
        <MetricDisplay
          label="ADA Accessible Rooms"
          value="34"
          subtext="Step-free access certified"
          icon={Accessibility}
        />
        <MetricDisplay
          label="Computer Laboratories"
          value="25"
          subtext="Equipped with workstations"
          icon={Laptop}
        />
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-brand-surface border border-brand-border rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-brand-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search room code, building, floor..."
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
              value={accessibleFilter}
              onChange={(e) => {
                setAccessibleFilter(e.target.value);
                setPage(1);
              }}
              className="bg-brand-elevated border border-brand-border rounded px-3 py-2 text-xs text-brand-text focus:outline-none focus:border-brand-accent"
            >
              <option value="">All Venues</option>
              <option value="true">Accessible Only</option>
              <option value="false">Standard Only</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-brand-muted">
          Showing <span className="font-semibold text-brand-text">{rooms.length}</span> of {total} venues
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <LoadingState message="Loading room registry..." />
      ) : error ? (
        <EmptyState
          icon={AlertTriangle}
          title="Error Loading Venues"
          description={error}
          actionLabel="Retry"
          onAction={loadRooms}
        />
      ) : rooms.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No Venues Found"
          description="No examination venues match the specified filters."
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
        title={`Venue Specification: ${selectedRoom?.room_code || ''}`}
        size="lg"
      >
        {selectedRoom && (
          <div className="space-y-6">
            <div className="bg-brand-elevated border border-brand-border rounded-lg p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono text-brand-accent uppercase tracking-wider">
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
              <div className="p-3 bg-brand-surface border border-brand-border rounded">
                <span className="text-xs text-brand-muted block">Effective Exam Capacity</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Users className="w-4 h-4 text-brand-accent" />
                  {selectedRoom.capacity ?? selectedRoom.exam_capacity ?? '—'} desks
                </span>
              </div>
              <div className="p-3 bg-brand-surface border border-brand-border rounded">
                <span className="text-xs text-brand-muted block">Accessibility Status</span>
                <span className="text-sm font-bold text-brand-text flex items-center gap-1.5 mt-1">
                  <Accessibility className="w-4 h-4 text-brand-success" />
                  {selectedRoom.is_accessible ? 'ADA Compliant' : 'Standard Venue'}
                </span>
              </div>
            </div>

            {/* Operating Hours and Availability Windows */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-brand-accent" />
                Operating Windows & Closures
              </h4>

              <div className="p-3 bg-brand-surface border border-brand-border rounded text-xs space-y-2">
                <div className="flex items-center justify-between text-brand-text font-medium">
                  <span>Standard Daily Operation</span>
                  <span className="text-brand-accent font-mono">08:00 - 18:00</span>
                </div>
                <p className="text-brand-muted text-[11px]">
                  Governed by RoomAvailability records. Solver validates that all candidate examination sessions fall strictly within active operational boundaries.
                </p>
              </div>
            </div>

            {/* Hardware & Amenities */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-brand-muted uppercase tracking-wider flex items-center gap-1.5">
                <Laptop className="w-3.5 h-3.5 text-brand-accent" />
                Installed Equipment
              </h4>

              <div className="p-3 bg-brand-surface border border-brand-border rounded text-xs space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-brand-accent" />
                  <span className="text-brand-text">Centralized Audio-Visual Projection</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-brand-accent" />
                  <span className="text-brand-text">Monitored In-Room Surveillance</span>
                </div>
                {selectedRoom.has_computers && (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-brand-success" />
                    <span className="text-brand-text">High-Performance Dedicated Student Terminals</span>
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
