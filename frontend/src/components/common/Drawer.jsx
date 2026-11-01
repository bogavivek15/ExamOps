import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Drawer({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = 'max-w-xl',
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div
          className={`w-screen ${width} bg-brand-surface border-l border-brand-border shadow-2xl flex flex-col`}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-brand-border flex items-center justify-between bg-brand-sidebar">
            <div>
              <h2 className="text-sm font-semibold text-brand-text uppercase tracking-wider">
                {title}
              </h2>
              {subtitle && <p className="text-xs text-brand-muted mt-0.5">{subtitle}</p>}
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-brand-muted hover:text-brand-text hover:bg-brand-elevated transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-slate-300">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

