import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'max-w-lg',
  actions = null,
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
    <div
      className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-3 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog */}
      <div
        className={`relative w-full ${maxWidth} max-h-[92vh] flex flex-col bg-brand-surface border border-brand-border rounded-[6px] shadow-2xl overflow-hidden z-10`}
      >
        {/* Header */}
        <div className="px-4 sm:px-6 py-4 border-b border-brand-border flex items-center justify-between bg-brand-sidebar shrink-0">
          <div className="pr-2 truncate">
            <h3 className="text-xs sm:text-sm font-semibold text-brand-text tracking-wide truncate">{title}</h3>
            {subtitle && <p className="text-xs text-brand-muted mt-0.5 truncate">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-brand-muted hover:text-brand-text hover:bg-brand-elevated transition-colors shrink-0"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6 text-xs text-slate-300 overflow-y-auto flex-1">{children}</div>

        {/* Footer Actions */}
        {actions && (
          <div className="px-4 sm:px-6 py-3 border-t border-brand-border bg-brand-sidebar/50 flex items-center justify-end gap-2.5 shrink-0 flex-wrap">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
