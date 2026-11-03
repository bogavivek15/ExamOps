/**
 * ExamOps Frontend — Enterprise Login View
 * Designed for Academic Administrators, Evaluators, and Operations Staff.
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Lock,
  Mail,
  Eye,
  EyeOff,
  ShieldCheck,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Check for session_expired query parameter
  const searchParams = new URLSearchParams(location.search);
  const isSessionExpired = searchParams.get('session_expired') === 'true';

  // If already authenticated, redirect to destination or dashboard
  const destination = location.state?.from?.pathname || '/';
  if (isAuthenticated) {
    navigate(destination, { replace: true });
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setErrorMessage('Please enter both your institutional email and password.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage('');
      await login(email.trim(), password);
      navigate(destination, { replace: true });
    } catch (err) {
      setErrorMessage(
        err.message || 'Invalid credentials or inactive user profile. Please verify your details.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#0B1118] text-[#E8EEF5] flex flex-col justify-between selection:bg-[#56D6C2]/30 selection:text-white">
      {/* Top Subtle Brand Bar */}
      <header className="h-16 border-b border-[#263442]/60 px-6 sm:px-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Bespoke ExamOps Calendar Shield Icon */}
          <div
            className="w-8 h-8 rounded-[4px] bg-[#141414] border border-white/20 flex items-center justify-center shrink-0 shadow-sm p-1"
            title="ExamOps"
          >
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="7" y="2.5" width="3.5" height="4.5" rx="1.5" fill="#B8EF43" />
              <rect x="21.5" y="2.5" width="3.5" height="4.5" rx="1.5" fill="#B8EF43" />
              <rect
                x="3"
                y="4.5"
                width="26"
                height="24.5"
                rx="4.5"
                fill="#141414"
                stroke="rgba(255, 255, 255, 0.24)"
                strokeWidth="1.2"
              />
              <line x1="3" y1="10.5" x2="29" y2="10.5" stroke="rgba(255, 255, 255, 0.16)" strokeWidth="1" />
              <rect x="6.5" y="13" width="2.5" height="13" rx="1.25" fill="#FFFFFF" />
              <rect x="11" y="13" width="9.5" height="3" rx="1.5" fill="#FFFFFF" />
              <circle cx="23.5" cy="14.5" r="1.5" fill="#FCF7F3" fillOpacity="0.8" />
              <rect x="11" y="18" width="14" height="3" rx="1.5" fill="#B8EF43" />
              <circle cx="21.5" cy="19.5" r="0.75" fill="#000000" />
              <rect x="11" y="23" width="10.5" height="3" rx="1.5" fill="#FFFFFF" fillOpacity="0.85" />
              <circle cx="24.5" cy="24.5" r="1.5" fill="#FCF7F3" fillOpacity="0.8" />
            </svg>
          </div>
          <span className="font-bold text-sm tracking-wider text-[#E8EEF5]">ExamOps</span>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-[#9AAABA]">
          <span className="inline-block w-2 h-2 rounded-full bg-[#57BE93]" />
          <span>Operations Engine Online</span>
        </div>
      </header>

      {/* Main Login Card Area */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 md:p-10">
        <div className="w-full max-w-md space-y-6">
          {/* Header Title */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#E8EEF5] tracking-tight">
              Welcome to ExamOps
            </h1>
            <p className="text-xs sm:text-sm text-[#9AAABA] max-w-sm mx-auto leading-relaxed">
              Examination Operations & Intelligent Scheduling Platform
            </p>
          </div>

          {/* Session Expired Banner */}
          {isSessionExpired && (
            <div className="p-3 rounded-[4px] bg-[#E8B66D]/15 border border-[#E8B66D]/40 text-[#E8B66D] text-xs flex items-center gap-2.5">
              <Clock size={16} className="shrink-0" />
              <span>Your session has expired. Please sign in again to continue.</span>
            </div>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3.5 rounded-[4px] bg-[#E87979]/15 border border-[#E87979]/40 text-[#E87979] text-xs flex items-start gap-2.5">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span className="leading-snug">{errorMessage}</span>
            </div>
          )}

          {/* Form Card */}
          <div className="bg-[#121C26] border border-[#263442] rounded-lg p-6 sm:p-8 shadow-2xl space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email Input */}
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#9AAABA]">
                  Institutional Email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#9AAABA]">
                    <Mail size={16} />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (errorMessage) setErrorMessage('');
                    }}
                    placeholder="evaluator@examops.edu"
                    disabled={isSubmitting}
                    className="w-full pl-10 pr-3.5 py-2.5 bg-[#0E151D] border border-[#263442] rounded-[4px] text-xs sm:text-sm text-[#E8EEF5] placeholder-[#9AAABA]/50 focus:outline-none focus:border-[#56D6C2] focus:ring-1 focus:ring-[#56D6C2] transition-colors disabled:opacity-50"
                  />
                </div>
              </div>

              {/* Password Input with Show/Hide Toggle */}
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#9AAABA]">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#9AAABA]">
                    <Lock size={16} />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errorMessage) setErrorMessage('');
                    }}
                    placeholder="••••••••••••"
                    disabled={isSubmitting}
                    className="w-full pl-10 pr-10 py-2.5 bg-[#0E151D] border border-[#263442] rounded-[4px] text-xs sm:text-sm text-[#E8EEF5] placeholder-[#9AAABA]/50 focus:outline-none focus:border-[#56D6C2] focus:ring-1 focus:ring-[#56D6C2] transition-colors disabled:opacity-50 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#9AAABA] hover:text-[#E8EEF5] transition-colors"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-2 py-2.5 px-4 bg-[#56D6C2] hover:bg-[#56D6C2]/90 active:bg-[#56D6C2]/80 text-[#0B1118] font-semibold text-xs sm:text-sm rounded-[4px] transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(86,214,194,0.25)] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-[#0B1118] border-t-transparent rounded-full animate-spin" />
                    <span>Verifying Credentials...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Evaluator Access Callout Card */}
          <div className="bg-[#172330]/60 border border-[#263442] rounded-lg p-4 sm:p-5 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#56D6C2]">
              <ShieldCheck size={16} />
              <span>Evaluator Access</span>
            </div>
            <p className="text-[11px] sm:text-xs text-[#9AAABA] leading-relaxed">
              External project evaluators can sign in using their assigned demonstration account to explore the complete Academic Administrator operations dashboard, 12 modules, and scheduling engine.
            </p>
            <div className="pt-2 border-t border-[#263442]/60 flex items-center justify-between text-[11px] text-[#9AAABA]">
              <span>Role: <strong className="text-white">Academic Administrator</strong></span>
              <span className="text-[#57BE93] font-medium flex items-center gap-1">
                <CheckCircle2 size={12} /> RBAC Verified
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="h-14 border-t border-[#263442]/60 px-6 sm:px-10 flex items-center justify-between text-[11px] text-[#9AAABA]">
        <span>ExamOps Platform v1.0 • Enterprise Edition</span>
        <span>Secured via Supabase Auth</span>
      </footer>
    </div>
  );
}
