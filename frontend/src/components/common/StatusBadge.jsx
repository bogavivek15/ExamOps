import React from 'react';

const STATUS_STYLES = {
  // Scheduling Runs
  DRAFT: 'bg-white/10 text-slate-300 border-white/20',
  SCHEDULING: 'bg-brand-accent/20 text-brand-accent border-brand-accent/40 animate-pulse',
  REVIEW_REQUIRED: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  APPROVED: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  PUBLISHED: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30',
  SUPERSEDED: 'bg-white/5 text-slate-400 border-white/10',
  CANCELLED: 'bg-rose-500/15 text-rose-400 border-rose-500/30',

  // Master Data
  ACTIVE: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30',
  AVAILABLE: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30',
  CONFIRMED: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30',
  READY: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  INACTIVE: 'bg-white/5 text-slate-400 border-white/10',
  SUSPENDED: 'bg-rose-500/15 text-rose-400 border-rose-500/30',

  // Severity
  INFO: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  WARNING: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  ERROR: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
  BLOCKER: 'bg-rose-600/25 text-rose-200 border-rose-500 font-semibold',
};

export default function StatusBadge({ status, size = 'sm', className = '' }) {
  const normalized = (status || '').toUpperCase().trim();
  const style = STATUS_STYLES[normalized] || 'bg-white/10 text-slate-400 border-white/15';

  const sizeClasses = size === 'xs' 
    ? 'px-1.5 py-0.5 text-[10px]' 
    : 'px-2.5 py-0.5 text-xs';

  return (
    <span
      className={`inline-flex items-center font-medium rounded-[4px] border ${sizeClasses} ${style} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-90" />
      {normalized}
    </span>
  );
}
