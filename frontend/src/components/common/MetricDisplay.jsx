import React from 'react';

export default function MetricDisplay({
  label,
  value,
  secondary,
  icon: Icon,
  trend,
  trendPositive = true,
  className = '',
}) {
  return (
    <div
      className={`bg-brand-surface border border-brand-border rounded-lg p-5 flex flex-col justify-between hover:border-brand-accent/40 transition-colors ${className}`}
    >
      <div className="flex items-center justify-between text-brand-muted mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {label}
        </span>
        {Icon && (
          <div className="p-2 rounded-md bg-brand-elevated text-brand-accent">
            <Icon size={18} />
          </div>
        )}
      </div>

      <div className="mt-1">
        <div className="text-2xl font-bold tracking-tight text-brand-text font-mono">
          {value !== undefined && value !== null ? value : '—'}
        </div>

        {(secondary || trend) && (
          <div className="mt-2 flex items-center gap-2 text-xs">
            {trend && (
              <span
                className={`font-medium ${
                  trendPositive ? 'text-brand-success' : 'text-brand-danger'
                }`}
              >
                {trend}
              </span>
            )}
            {secondary && <span className="text-brand-muted">{secondary}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
