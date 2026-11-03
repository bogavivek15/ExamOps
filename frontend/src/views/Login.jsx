/**
 * ExamOps Frontend — Enterprise Role-Based Demo Login View
 * Designed for external evaluators, administrators, and operations staff.
 * Provides protected role-based demo session access with backend cryptographic verification
 * alongside normal authenticated password login for Platform Administrators and staff.
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Shield,
  ShieldCheck,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock,
  User,
  GraduationCap,
  Sparkles,
  Lock,
  Mail,
  Eye,
  EyeOff,
  Key,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const DEMO_ROLE_PROFILES = {
  ACADEMIC_ADMINISTRATOR: {
    id: 'ACADEMIC_ADMINISTRATOR',
    label: 'Academic Administrator (Exam Officer)',
    shortLabel: 'Academic Administrator',
    badge: 'Recommended for Evaluation',
    badgeClass: 'bg-brand-accent/20 text-brand-accent border-brand-accent/40',
    accountName: 'ExamOps Evaluator',
    accountEmail: 'evaluator@examops.edu',
    description:
      'Full operational authority: timetable scheduling, room allocation, solver execution, conflict graph inspection, exception triage, and final schedule publication.',
    capabilities: [
      'Run deterministic heuristic scheduling solver',
      'Inspect decision telemetry & constraint graphs',
      'Approve and publish institutional timetables',
      'Audit unassigned exams in Exception Center',
    ],
  },
  INSTRUCTOR: {
    id: 'INSTRUCTOR',
    label: 'Course Instructor',
    shortLabel: 'Course Instructor',
    badge: 'Academic Perspective',
    badgeClass: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
    accountName: 'Prof. Kapoor (Computer Science)',
    accountEmail: 'head.computer@faculty.institution.edu',
    description:
      'Faculty perspective: review departmental course schedules, student cohorts, and exam details with role-based clinical note redaction.',
    capabilities: [
      'View departmental examination schedules',
      'Inspect student cohort enrollments',
      'Redacted clinical accommodation notes',
    ],
  },
  SUPPORT_STAFF: {
    id: 'SUPPORT_STAFF',
    label: 'Support Staff / Invigilator',
    shortLabel: 'Support Staff',
    badge: 'Operations & Facilities',
    badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    accountName: 'Disability & Facilities Lead 1',
    accountEmail: 'facilities.lead.1@examops.institution.edu',
    description:
      'Staff perspective: manage invigilator duties, venue accessibility features, proctor availability, and room seating layouts.',
    capabilities: [
      'View proctoring assignments and work shifts',
      'Inspect room accessibility & equipment features',
      'Check venue capacities & maintenance closures',
    ],
  },
  LEARNER: {
    id: 'LEARNER',
    label: 'Student / Learner',
    shortLabel: 'Student / Learner',
    badge: 'Student Portal',
    badgeClass: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30',
    accountName: 'Carlos Garcia',
    accountEmail: 'carlos.garcia.0008@student.institution.edu',
    description:
      'Student perspective: personalized examination timetable, venue locations, and registered accommodations (administrative actions restricted).',
    capabilities: [
      'View personal examination timetable',
      'View assigned venue & seat allocations',
      'Verify registered disability accommodations',
    ],
  },
};

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { demoLogin, login, isAuthenticated } = useAuth();

  const searchParams = new URLSearchParams(location.search);
  const isSessionExpired = searchParams.get('session_expired') === 'true';

  const [activeTab, setActiveTab] = useState('demo'); // 'demo' | 'password'
  const [selectedRole, setSelectedRole] = useState('ACADEMIC_ADMINISTRATOR');
  const [demoAccessKey, setDemoAccessKey] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // If already authenticated, redirect to destination or dashboard
  const destination = location.state?.from?.pathname || '/';
  if (isAuthenticated) {
    navigate(destination, { replace: true });
    return null;
  }

  const activeProfile = DEMO_ROLE_PROFILES[selectedRole] || DEMO_ROLE_PROFILES.ACADEMIC_ADMINISTRATOR;

  const handleDemoSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setErrorMessage('');
      await demoLogin(selectedRole, demoAccessKey.trim() || null);
      navigate(destination, { replace: true });
    } catch (err) {
      const msg = err.message || '';
      if (msg.toLowerCase().includes('disabled')) {
        setErrorMessage('Demo evaluation access is currently disabled by institutional security policy.');
      } else if (msg.toLowerCase().includes('access key') || msg.includes('403')) {
        setErrorMessage('Invalid or missing Demo Access Key. A valid DEMO_ACCESS_KEY is required to enter.');
      } else {
        setErrorMessage(msg || 'Unable to establish demo session. Please try selecting a role again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
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
      setErrorMessage(err.message || 'Invalid credentials or inactive user profile.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-brand-bg text-brand-text flex flex-col justify-between selection:bg-brand-accent/30 selection:text-brand-accent">
      {/* Top Subtle Brand Bar */}
      <header className="h-16 border-b border-brand-border bg-brand-surface/90 backdrop-blur-md px-4 sm:px-10 flex items-center justify-between">
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
          <span className="font-bold text-sm tracking-wider text-white">ExamOps</span>
          <span className="text-[10px] px-2 py-0.5 rounded-[2px] bg-brand-accent/15 text-brand-accent border border-brand-accent/40 font-mono font-semibold uppercase">
            Operations Platform
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-brand-muted">
          <span className="inline-block w-2 h-2 rounded-full bg-brand-accent animate-pulse" />
          <span className="hidden sm:inline">Operations Engine Online</span>
        </div>
      </header>

      {/* Main Login Card Area */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 md:p-10">
        <div className="w-full max-w-lg space-y-6">
          {/* Header Title */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome to ExamOps
            </h1>
            <p className="text-xs sm:text-sm text-brand-muted max-w-md mx-auto leading-relaxed">
              Examination Operations & Intelligent Scheduling Platform
            </p>
          </div>

          {/* Session Expired Banner */}
          {isSessionExpired && (
            <div className="p-3 rounded-[4px] bg-brand-warning/10 border border-brand-warning/30 text-brand-warning text-xs flex items-center gap-2.5">
              <Clock size={16} className="shrink-0" />
              <span>Your evaluation session has ended. Please authenticate to re-enter.</span>
            </div>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3.5 rounded-[4px] bg-brand-danger/10 border border-brand-danger/30 text-brand-danger text-xs flex items-start gap-2.5">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span className="leading-snug">{errorMessage}</span>
            </div>
          )}

          {/* Form Card */}
          <div className="bg-brand-surface border border-brand-border rounded-[6px] p-6 sm:p-8 shadow-2xl space-y-6">
            {/* Mode Switcher Tabs */}
            <div className="flex border-b border-brand-border pb-3 gap-4 text-xs font-semibold">
              <button
                type="button"
                onClick={() => {
                  setActiveTab('demo');
                  setErrorMessage('');
                }}
                className={`pb-1 transition-colors flex items-center gap-1.5 cursor-pointer ${
                  activeTab === 'demo'
                    ? 'text-brand-accent border-b-2 border-brand-accent'
                    : 'text-brand-muted hover:text-white'
                }`}
              >
                <Sparkles size={14} />
                Demo Evaluation Access
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveTab('password');
                  setErrorMessage('');
                }}
                className={`pb-1 transition-colors flex items-center gap-1.5 cursor-pointer ${
                  activeTab === 'password'
                    ? 'text-brand-accent border-b-2 border-brand-accent'
                    : 'text-brand-muted hover:text-white'
                }`}
              >
                <Lock size={14} />
                Platform Administrator Login
              </button>
            </div>

            {activeTab === 'demo' ? (
              <>
                <div className="space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-brand-accent flex items-center gap-1.5">
                    <Sparkles size={13} />
                    Instant Demonstration Access
                  </span>
                  <p className="text-xs text-brand-muted">
                    Select an authorized institutional role to enter the platform. Sessions are validated and cryptographically signed by the backend.
                  </p>
                </div>

                <form onSubmit={handleDemoSubmit} className="space-y-5">
                  {/* Role Dropdown (Platform Administrator removed) */}
                  <div className="space-y-2">
                    <label
                      htmlFor="demo-role-select"
                      className="block text-xs font-semibold uppercase tracking-wider text-brand-muted"
                    >
                      Select Role
                    </label>
                    <div className="relative">
                      <select
                        id="demo-role-select"
                        value={selectedRole}
                        onChange={(e) => {
                          setSelectedRole(e.target.value);
                          if (errorMessage) setErrorMessage('');
                        }}
                        disabled={isSubmitting}
                        className="w-full px-3.5 py-2.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs sm:text-sm text-brand-text focus:outline-none focus:border-brand-accent focus:ring-1 focus:ring-brand-accent/40 font-medium transition-colors cursor-pointer disabled:opacity-50"
                      >
                        <option value="ACADEMIC_ADMINISTRATOR">
                          Academic Administrator (Exam Officer) — Recommended
                        </option>
                        <option value="INSTRUCTOR">Course Instructor</option>
                        <option value="SUPPORT_STAFF">Support Staff / Invigilator</option>
                        <option value="LEARNER">Student / Learner</option>
                      </select>
                    </div>
                  </div>

                  {/* Demo Access Key Input */}
                  <div className="space-y-1.5">
                    <label
                      htmlFor="demo-access-key"
                      className="block text-xs font-semibold uppercase tracking-wider text-brand-muted flex items-center justify-between"
                    >
                      <span>Demo Access Key</span>
                      <span className="text-[10px] text-brand-muted/70 font-normal lowercase">Required if server-protected</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-brand-muted">
                        <Key size={15} />
                      </div>
                      <input
                        id="demo-access-key"
                        type="password"
                        value={demoAccessKey}
                        onChange={(e) => {
                          setDemoAccessKey(e.target.value);
                          if (errorMessage) setErrorMessage('');
                        }}
                        placeholder="Enter authorized demo access key"
                        disabled={isSubmitting}
                        className="w-full pl-10 pr-3.5 py-2.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs sm:text-sm text-brand-text placeholder-brand-muted/40 focus:outline-none focus:border-brand-accent focus:ring-1 focus:ring-brand-accent/40 font-mono transition-colors disabled:opacity-50"
                      />
                    </div>
                  </div>

                  {/* Selected Role Interactive Preview Card */}
                  <div className="bg-brand-panel border border-brand-border rounded-[4px] p-4 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-brand-border">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-7 h-7 rounded-[4px] bg-brand-elevated border border-white/10 flex items-center justify-center text-brand-accent shrink-0">
                          <User size={14} />
                        </div>
                        <div className="truncate">
                          <span className="font-semibold text-xs text-white block truncate">
                            {activeProfile.accountName}
                          </span>
                          <span className="font-mono text-[10px] text-brand-muted block truncate">
                            {activeProfile.accountEmail}
                          </span>
                        </div>
                      </div>

                      <span
                        className={`text-[10px] font-medium px-2 py-0.5 rounded-[3px] border self-start sm:self-auto shrink-0 ${activeProfile.badgeClass}`}
                      >
                        {activeProfile.badge}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      {activeProfile.description}
                    </p>

                    <div className="space-y-1.5 pt-1">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-brand-muted block">
                        Available Capabilities:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px] text-slate-300">
                        {activeProfile.capabilities.map((cap, i) => (
                          <div key={i} className="flex items-start gap-1.5">
                            <CheckCircle2 size={12} className="text-brand-accent shrink-0 mt-0.5" />
                            <span className="leading-snug">{cap}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Dynamic Submit Button */}
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full mt-2 py-3 px-4 bg-brand-accent hover:bg-brand-accent-hover active:bg-brand-accent-active text-black font-semibold text-xs sm:text-sm rounded-[4px] transition-all flex items-center justify-center gap-2 shadow-[0_2px_10px_rgba(184,239,67,0.2)] disabled:opacity-50 disabled:cursor-not-allowed border border-[#62626266]/40 cursor-pointer"
                  >
                    {isSubmitting ? (
                      <>
                        <span className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                        <span>Initiating Demo Session...</span>
                      </>
                    ) : (
                      <>
                        <span>Login as {activeProfile.shortLabel}</span>
                        <ArrowRight size={16} />
                      </>
                    )}
                  </button>
                </form>
              </>
            ) : (
              /* Standard Credentials Form for Platform Administrator and Staff */
              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <div className="space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                    <Shield size={13} className="text-purple-400" />
                    Protected Account Authentication
                  </span>
                  <p className="text-xs text-brand-muted">
                    Sign in with your verified institutional administrator or staff credentials.
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-brand-muted">
                    Institutional Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-brand-muted">
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
                      placeholder="admin@examops.institution.edu"
                      disabled={isSubmitting}
                      className="w-full pl-10 pr-3.5 py-2.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs sm:text-sm text-brand-text placeholder-brand-muted/40 focus:outline-none focus:border-brand-accent focus:ring-1 focus:ring-brand-accent/40 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-brand-muted">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-brand-muted">
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
                      className="w-full pl-10 pr-10 py-2.5 bg-brand-elevated border border-brand-border rounded-[4px] text-xs sm:text-sm text-brand-text placeholder-brand-muted/40 focus:outline-none focus:border-brand-accent focus:ring-1 focus:ring-brand-accent/40 transition-colors disabled:opacity-50 font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-brand-muted hover:text-white transition-colors"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full mt-2 py-3 px-4 bg-brand-accent hover:bg-brand-accent-hover active:bg-brand-accent-active text-black font-semibold text-xs sm:text-sm rounded-[4px] transition-all flex items-center justify-center gap-2 shadow-[0_2px_10px_rgba(184,239,67,0.2)] disabled:opacity-50 disabled:cursor-not-allowed border border-[#62626266]/40 cursor-pointer"
                >
                  {isSubmitting ? (
                    <>
                      <span className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                      <span>Verifying Credentials...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In with Credentials</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </form>
            )}
          </div>

          {/* Evaluator Access Callout Card */}
          <div className="bg-brand-panel border border-brand-border rounded-[4px] p-4 sm:p-5 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-brand-accent">
              <ShieldCheck size={16} />
              <span>Role-Based Access Control (RBAC) Notice</span>
            </div>
            <p className="text-[11px] sm:text-xs text-brand-muted leading-relaxed">
              Sessions are issued via cryptographic JWT Bearer tokens resolved to active synthetic database profiles in PostgreSQL. Switching roles lets you verify authentic institutional security boundaries: administrative operations are strictly forbidden to learners and instructors. Platform Administrator privileges require standard credential authentication.
            </p>
            <div className="pt-2 border-t border-brand-border flex items-center justify-between text-[11px] text-brand-muted">
              <span>Security: <strong className="text-white">PostgreSQL Profile Authorization</strong></span>
              <span className="text-brand-accent font-medium flex items-center gap-1">
                <CheckCircle2 size={12} /> Profile Enforced
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="h-14 border-t border-brand-border bg-brand-surface/40 px-4 sm:px-10 flex items-center justify-between text-[11px] text-brand-muted">
        <span>ExamOps Platform v1.0 • Enterprise Edition</span>
        <span>DEMO ACCESS • Database Role Enforced</span>
      </footer>
    </div>
  );
}
