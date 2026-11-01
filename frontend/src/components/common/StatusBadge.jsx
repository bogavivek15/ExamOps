import React from 'react';

const STATUS_STYLES = {
  // Scheduling Runs
  DRAFT: 'bg-slate-800 text-slate-300 border-slate-700',
  SCHEDULING: 'bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse',
  REVIEW_REQUIRED: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  APPROVED: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  PUBLISHED: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  SUPERSEDED: 'bg-slate-800/80 text-slate-400 border-slate-700',
  CANCELLED: 'bg-rose-500/15 text-rose-400 border-rose-500/30',

  // Master Data
  ACTIVE: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  AVAILABLE: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
  CONFIRMED: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  READY: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  INACTIVE: 'bg-slate-800 text-slate-400 border-slate-700',
  SUSPENDED: 'bg-rose-500/15 text-rose-400 border-rose-500/30',

  // Severity
  INFO: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  WARNING: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  ERROR: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
  BLOCKER: 'bg-rose-600/25 text-rose-200 border-rose-500 font-semibold',
};

export default function StatusBadge({ status, size = 'sm', className = '' }) {
  const normalized = (status || '').toUpperCase().trim();
  const style = STATUS_STYLES[normalized] || 'bg-slate-800 text-slate-400 border-slate-700';

  const sizeClasses = size === 'xs' 
    ? 'px-1.5 py-0.5 text-[10px]' 
    : 'px-2.5 py-0.5 text-xs';

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${sizeClasses} ${style} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      {normalized}
    </span>
  );
}
