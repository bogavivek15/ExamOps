import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading institutional operations data...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center text-brand-muted">
      <Loader2 className="animate-spin text-brand-accent mb-3" size={28} />
      <p className="text-xs uppercase tracking-wider font-mono text-slate-400">{message}</p>
    </div>
  );
}

