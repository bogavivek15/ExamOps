/**
 * ExamOps Frontend — Authentication Context
 * Manages Supabase Auth credentials, session restoration, and database-authoritative role access.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { supabase, isSupabaseConfigured } from '../services/supabaseClient';

const AuthContext = createContext();

export const ROLES = [
  { id: 'ACADEMIC_ADMINISTRATOR', label: 'Academic Administrator (Exam Officer)', badge: 'bg-brand-accent/20 text-brand-accent border-brand-accent/40' },
  { id: 'PLATFORM_ADMINISTRATOR', label: 'Platform Administrator', badge: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  { id: 'INSTRUCTOR', label: 'Course Instructor', badge: 'bg-sky-500/20 text-sky-300 border-sky-500/30' },
  { id: 'SUPPORT_STAFF', label: 'Support / Invigilator', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  { id: 'LEARNER', label: 'Student / Learner', badge: 'bg-brand-accent/15 text-brand-accent border-brand-accent/30' },
];

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(api.currentUser);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    let unsubscribe = null;

    const initAuth = async () => {
      try {
        setLoading(true);

        if (isSupabaseConfigured && supabase) {
          // 1. Check existing Supabase session from localStorage
          const { data: { session }, error } = await supabase.auth.getSession();
          if (session?.access_token && !error) {
            try {
              api.setSession(session.access_token, null);
              const profile = await api.getMe();
              api.setSession(session.access_token, profile);
              setCurrentUser(profile);
            } catch (err) {
              console.warn('Backend profile verification failed for Supabase session:', err);
              api.clearSession();
              setCurrentUser(null);
            }
          } else {
            api.clearSession();
            setCurrentUser(null);
          }

          // 2. Subscribe to auth changes (token refresh, logout)
          const { data: listener } = supabase.auth.onAuthStateChange(async (event, session) => {
            if (event === 'SIGNED_OUT' || !session) {
              api.clearSession();
              setCurrentUser(null);
            } else if (event === 'TOKEN_REFRESHED' && session) {
              api.setSession(session.access_token, currentUser);
            }
          });
          unsubscribe = listener?.subscription?.unsubscribe;
        } else {
          // Standalone backend token verification fallback
          const existingToken = api.getToken();
          if (existingToken) {
            try {
              const profile = await api.getMe();
              api.setSession(existingToken, profile);
              setCurrentUser(profile);
            } catch (err) {
              console.warn('Backend token expired or invalid:', err);
              api.clearSession();
              setCurrentUser(null);
            }
          } else {
            api.clearSession();
            setCurrentUser(null);
          }
        }
      } catch (err) {
        console.error('Session initialization error:', err);
        api.clearSession();
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []);

  const demoLogin = async (role, accessKey = null) => {
    try {
      setLoading(true);
      setAuthError(null);
      const data = await api.demoLogin(role, accessKey);
      setCurrentUser(data.user);
      return data.user;
    } catch (err) {
      const msg = err.message || 'Demo session initialization failed. Please try again.';
      setAuthError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      setAuthError(null);

      if (isSupabaseConfigured && supabase) {
        // Authenticate directly through Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password: password,
        });

        if (error) {
          throw new Error(error.message || 'Invalid email or password.');
        }

        const token = data.session?.access_token;
        if (!token) {
          throw new Error('Authentication failed: no access token returned.');
        }

        api.setSession(token, null);
        const profile = await api.getMe();
        api.setSession(token, profile);
        setCurrentUser(profile);
        return profile;
      } else {
        // Authenticate via backend verified login
        const data = await api.login(email.trim(), password);
        setCurrentUser(data.user);
        return data.user;
      }
    } catch (err) {
      const msg = err.message || 'Authentication failed. Please verify your credentials.';
      setAuthError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (isSupabaseConfigured && supabase) {
        await supabase.auth.signOut();
      }
    } catch (err) {
      console.warn('Supabase signOut error:', err);
    } finally {
      api.clearSession();
      setCurrentUser(null);
    }
  };

  const currentRole = currentUser?.role || null;
  const isAuthenticated = Boolean(currentUser);
  const isAdmin = ['ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR', 'EXAM_OFFICER'].includes(currentRole);

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        currentRole,
        isAuthenticated,
        isAdmin,
        loading,
        authError,
        login,
        demoLogin,
        logout,
        availableRoles: ROLES,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
