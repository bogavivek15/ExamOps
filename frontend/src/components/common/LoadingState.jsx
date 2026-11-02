import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading records...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center bg-brand-surface border border-brand-border rounded-[4px] min-h-[200px]">
      <Loader2 className="animate-spin text-brand-accent mb-3" size={24} />
      <span className="text-xs text-brand-muted">{message}</span>
    </div>
  );
}
