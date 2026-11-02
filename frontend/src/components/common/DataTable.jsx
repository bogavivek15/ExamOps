import React, { useState, useMemo } from 'react';
import { Search, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

export default function DataTable({
  columns = [],
  data = [],
  keyField = 'id',
  searchable = true,
  searchPlaceholder = 'Search records...',
  loading = false,
  actions = null,
  emptyMessage = 'No records found matching your search.',
  pageSize = 15,
  total = null,
  page = null,
  onPageChange = null,
  _onPageSizeChange = null,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [internalPage, setInternalPage] = useState(1);

  const isServerPaginated = onPageChange !== null && total !== null;
  const currentPage = isServerPaginated ? (page || 1) : internalPage;

  // Filter
  const filteredData = useMemo(() => {
    if (isServerPaginated || !searchTerm.trim()) return data;
    const term = searchTerm.toLowerCase();
    return data.filter((row) =>
      columns.some((col) => {
        const val = row[col.accessor];
        return val !== undefined && val !== null && String(val).toLowerCase().includes(term);
      })
    );
  }, [data, columns, searchTerm, isServerPaginated]);

  // Sort
  const sortedData = useMemo(() => {
    if (isServerPaginated || !sortField) return filteredData;
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      const res = aVal > bVal ? 1 : -1;
      return sortDirection === 'asc' ? res : -res;
    });
  }, [filteredData, sortField, sortDirection, isServerPaginated]);

  // Pagination
  const totalCount = isServerPaginated ? total : sortedData.length;
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const paginatedData = useMemo(() => {
    if (isServerPaginated) return sortedData;
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize, isServerPaginated]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handlePageChange = (newPage) => {
    const clamped = Math.max(1, Math.min(totalPages, newPage));
    if (isServerPaginated) {
      onPageChange(clamped);
    } else {
      setInternalPage(clamped);
    }
  };

  return (
    <div className="bg-brand-surface border border-brand-border rounded-lg overflow-hidden flex flex-col w-full shadow-sm">
      {/* Table Toolbar */}
      {(searchable || actions) && (
        <div className="p-3 sm:p-4 border-b border-brand-border flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-brand-surface">
          {searchable && (
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-muted" size={16} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  if (!isServerPaginated) setInternalPage(1);
                }}
                placeholder={searchPlaceholder}
                className="w-full pl-9 pr-4 py-2 sm:py-1.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs text-brand-text placeholder-brand-muted focus:outline-none focus:border-brand-accent transition-colors"
              />
            </div>
          )}
          {actions && (
            <div className="flex items-center gap-2 w-full sm:w-auto justify-end flex-wrap">
              {actions}
            </div>
          )}
        </div>
      )}

      {/* Table Container with Horizontal Scroll */}
      <div className="overflow-x-auto w-full">
        <table className="w-full text-left text-xs border-collapse min-w-[600px] sm:min-w-full">
          <thead>
            <tr className="border-b border-brand-border bg-brand-sidebar/80 text-slate-400 uppercase font-semibold tracking-wider text-[11px]">
              {columns.map((col) => (
                <th
                  key={col.accessor || col.header}
                  onClick={() => col.sortable !== false && col.accessor && handleSort(col.accessor)}
                  className={`px-4 py-3 whitespace-nowrap ${col.className || ''} ${
                    col.sortable !== false && col.accessor ? 'cursor-pointer select-none hover:text-brand-text' : ''
                  }`}
                  style={{ width: col.width }}
                >
                  <div className="flex items-center gap-1.5">
                    <span>{col.header}</span>
                    {col.sortable !== false && col.accessor && (
                      <span className="text-slate-500">
                        {sortField === col.accessor ? (
                          sortDirection === 'asc' ? (
                            <ArrowUp size={12} className="text-brand-accent" />
                          ) : (
                            <ArrowDown size={12} className="text-brand-accent" />
                          )
                        ) : (
                          <ArrowUpDown size={12} className="opacity-40" />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-border/60">
            {loading ? (
              Array.from({ length: 5 }).map((_, rIdx) => (
                <tr key={rIdx} className="animate-pulse">
                  {columns.map((c, cIdx) => (
                    <td key={cIdx} className="px-4 py-3">
                      <div className="h-4 bg-brand-elevated rounded w-3/4" />
                    </td>
                  ))}
                </tr>
              ))
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-brand-muted">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => (
                <tr
                  key={row[keyField] || idx}
                  className="hover:bg-white/[0.03] transition-colors text-slate-200"
                >
                  {columns.map((col) => (
                    <td key={col.accessor || col.header} className={`px-4 py-3 ${col.className || ''}`}>
                      {col.cell
                        ? col.cell(row)
                        : col.render
                        ? col.render(row[col.accessor], row)
                        : row[col.accessor] ?? '—'}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {!loading && totalCount > 0 && (
        <div className="px-4 py-3 border-t border-brand-border bg-brand-sidebar/40 flex flex-col sm:flex-row items-center justify-between gap-2.5 text-xs text-brand-muted">
          <div className="text-center sm:text-left">
            Showing <span className="font-mono text-brand-text">{(currentPage - 1) * pageSize + 1}</span> to{' '}
            <span className="font-mono text-brand-text">
              {Math.min(currentPage * pageSize, totalCount)}
            </span>{' '}
            of <span className="font-mono text-brand-text">{totalCount}</span> records
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-[4px] bg-brand-elevated border border-brand-border disabled:opacity-30 hover:border-brand-accent transition-colors"
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="font-mono px-2 text-brand-text">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-[4px] bg-brand-elevated border border-brand-border disabled:opacity-30 hover:border-brand-accent transition-colors"
              aria-label="Next page"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
