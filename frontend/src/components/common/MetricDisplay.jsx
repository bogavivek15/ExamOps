import React from 'react';

export default function MetricDisplay({
  label,
  value,
  secondary,
  subtext,
  icon: Icon,
  trend,
  trendPositive = true,
  className = '',
}) {
  const subtitle = secondary || subtext;

  return (
    <div
      className={`bg-brand-surface border border-brand-border rounded-[4px] p-3.5 sm:p-5 flex flex-col justify-between hover:border-brand-accent/40 transition-colors ${className}`}
    >
      <div className="flex items-center justify-between text-brand-muted mb-2 gap-2">
        <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-slate-400 truncate">
          {label}
        </span>
        {Icon && (
          <div className="p-1.5 sm:p-2 rounded-[4px] bg-brand-elevated text-brand-accent shrink-0">
            <Icon size={16} />
          </div>
        )}
      </div>

      <div className="mt-1">
        <div className="text-xl sm:text-2xl font-bold tracking-tight text-white font-mono truncate">
          {value !== undefined && value !== null ? value : '—'}
        </div>

        {(subtitle || trend) && (
          <div className="mt-1.5 sm:mt-2 flex items-center gap-1.5 text-[11px] sm:text-xs">
            {trend && (
              <span
                className={`font-medium ${
                  trendPositive ? 'text-brand-success' : 'text-brand-danger'
                }`}
              >
                {trend}
              </span>
            )}
            {subtitle && <span className="text-brand-muted truncate">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
