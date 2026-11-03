/**
 * ExamOps Frontend — Enterprise Minimal Login View
 * Centered, minimal enterprise dark-first interface.
 * Supports all 5 primary actors:
 * 1. Academic Administrator (Demo Evaluation Access)
 * 2. Instructor (Demo Evaluation Access)
 * 3. Support Staff (Demo Evaluation Access)
 * 4. Learner (Demo Evaluation Access)
 * 5. Platform Administrator (Protected Credential Authentication)
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ACTOR_ROLES = [
  { id: 'ACADEMIC_ADMINISTRATOR', label: 'Academic Administrator', isDemo: true, defaultPath: '/' },
  { id: 'INSTRUCTOR', label: 'Instructor', isDemo: true, defaultPath: '/' },
  { id: 'SUPPORT_STAFF', label: 'Support Staff', isDemo: true, defaultPath: '/' },
  { id: 'LEARNER', label: 'Learner', isDemo: true, defaultPath: '/' },
  { id: 'PLATFORM_ADMINISTRATOR', label: 'Platform Administrator', isDemo: false, defaultPath: '/admin' },
];

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { demoLogin, login, isAuthenticated } = useAuth();

  const [selectedRoleId, setSelectedRoleId] = useState('ACADEMIC_ADMINISTRATOR');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const selectedRole = ACTOR_ROLES.find((r) => r.id === selectedRoleId) || ACTOR_ROLES[0];

  // If already authenticated, redirect to destination or role default
  if (isAuthenticated) {
    const destination = location.state?.from?.pathname || selectedRole.defaultPath;
    navigate(destination, { replace: true });
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsSubmitting(true);

    try {
      const destination = location.state?.from?.pathname || selectedRole.defaultPath;

      if (selectedRole.isDemo) {
        // Passwordless demo evaluation access for the 4 evaluation roles
        await demoLogin(selectedRole.id);
        navigate(destination, { replace: true });
      } else {
        // Protected credential flow for Platform Administrator
        if (!email.trim() || !password) {
          setErrorMessage('Please enter both your institutional email and password.');
          setIsSubmitting(false);
          return;
        }
        await login(email.trim(), password);
        navigate(destination, { replace: true });
      }
    } catch (err) {
      const msg = err.message || '';
      if (msg.toLowerCase().includes('disabled')) {
        setErrorMessage('Demo evaluation access is currently disabled on the server.');
      } else if (msg.includes('429') || msg.toLowerCase().includes('rate limit')) {
        setErrorMessage('Too many login attempts. Please wait a moment and try again.');
      } else {
        setErrorMessage(msg || 'Authentication failed. Please verify your selection or credentials.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#08090A] text-white flex items-center justify-center p-4 selection:bg-[#B8EF43]/30 selection:text-[#B8EF43]">
      {/* Centered Login Card */}
      <div className="w-full max-w-[420px] bg-[#121212] border border-[#242629] rounded-xl p-8 sm:p-10 shadow-2xl">
        {/* Brand Section */}
        <div className="text-left">
          <h1 className="text-2xl font-bold tracking-tight text-[#B8EF43]">
            ExamOps
          </h1>
          <div className="text-[10px] font-mono tracking-widest text-[#9CA3AF] uppercase font-semibold mt-1">
            EXAMINATION OPERATIONS PLATFORM
          </div>

          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-5">
            Welcome to ExamOps
          </h2>
          <p className="text-xs sm:text-sm text-[#9CA3AF] mt-1.5 leading-relaxed">
            Select a role to explore the platform.
          </p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mt-5 p-3 rounded-[6px] bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-start gap-2.5">
            <AlertCircle size={15} className="shrink-0 mt-0.5" />
            <span className="leading-snug">{errorMessage}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {/* Role Dropdown */}
          <div>
            <label
              htmlFor="role-select"
              className="block text-xs font-semibold uppercase tracking-wider text-gray-300 mb-2"
            >
              Select Role
            </label>
            <select
              id="role-select"
              value={selectedRoleId}
              onChange={(e) => {
                setSelectedRoleId(e.target.value);
                setErrorMessage('');
              }}
              disabled={isSubmitting}
              className="w-full px-3.5 py-3 bg-[#1C1C1C] border border-[#2E3136] rounded-[6px] text-white text-sm font-medium focus:outline-none focus:border-[#B8EF43] focus:ring-1 focus:ring-[#B8EF43] transition-colors cursor-pointer disabled:opacity-50"
            >
              {ACTOR_ROLES.map((role) => (
                <option key={role.id} value={role.id} className="bg-[#1C1C1C] text-white">
                  {role.label}
                </option>
              ))}
            </select>
          </div>

          {/* Conditional Protected Credential Inputs for Platform Administrator */}
          {!selectedRole.isDemo && (
            <div className="space-y-3 pt-2">
              <div>
                <label
                  htmlFor="admin-email"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Institutional Email
                </label>
                <input
                  id="admin-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMessage) setErrorMessage('');
                  }}
                  placeholder="admin@examops.institution.edu"
                  disabled={isSubmitting}
                  className="w-full px-3.5 py-2.5 bg-[#1C1C1C] border border-[#2E3136] rounded-[6px] text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#B8EF43] focus:ring-1 focus:ring-[#B8EF43] transition-colors disabled:opacity-50"
                />
              </div>

              <div>
                <label
                  htmlFor="admin-password"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="admin-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errorMessage) setErrorMessage('');
                    }}
                    placeholder="••••••••••••"
                    disabled={isSubmitting}
                    className="w-full px-3.5 py-2.5 pr-10 bg-[#1C1C1C] border border-[#2E3136] rounded-[6px] text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#B8EF43] focus:ring-1 focus:ring-[#B8EF43] transition-colors disabled:opacity-50 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white transition-colors"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Dynamic Lime-Green Action Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-6 py-3.5 px-4 bg-[#B8EF43] hover:bg-[#BEF264] active:bg-[#A6DF30] text-black font-semibold text-sm rounded-[6px] transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <span className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Login as {selectedRole.label}</span>
            )}
          </button>

          {/* Minimal Card Footer */}
          <div className="text-center text-xs text-[#6B7280] pt-2 font-normal">
            {selectedRole.isDemo ? (
              <span>Demo access · No password required</span>
            ) : (
              <span>Protected access · Institutional credentials required</span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
