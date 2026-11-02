import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({
  title = 'No records found',
  description = 'There are no active records matching this view.',
  icon: Icon = Inbox,
  action = null,
  actionLabel = null,
  onAction = null,
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center bg-brand-surface border border-brand-border rounded-[4px]">
      <div className="p-3 bg-brand-elevated text-brand-muted rounded-full mb-3">
        <Icon size={22} className="text-brand-accent" />
      </div>
      <h4 className="text-xs sm:text-sm font-semibold text-brand-text mb-1">{title}</h4>
      <p className="text-xs text-brand-muted max-w-sm mb-4">{description}</p>
      {action ? (
        <div>{action}</div>
      ) : actionLabel && onAction ? (
        <button
          onClick={onAction}
          className="px-3.5 py-1.5 bg-brand-elevated hover:bg-brand-border border border-brand-border rounded text-xs text-brand-text hover:text-white transition-colors"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
