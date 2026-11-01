import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({
  title = 'No records found',
  description = 'There are no active records matching this operational view.',
  icon: Icon = Inbox,
  action = null,
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-brand-surface border border-brand-border rounded-lg">
      <div className="p-3 bg-brand-elevated text-brand-muted rounded-full mb-3">
        <Icon size={24} />
      </div>
      <h4 className="text-sm font-semibold text-brand-text mb-1">{title}</h4>
      <p className="text-xs text-brand-muted max-w-sm mb-4">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
