import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const ROLES = [
  { id: 'ACADEMIC_ADMINISTRATOR', label: 'Academic Administrator (Exam Officer)', badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  { id: 'PLATFORM_ADMINISTRATOR', label: 'Platform Administrator', badge: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  { id: 'INSTRUCTOR', label: 'Course Instructor', badge: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  { id: 'SUPPORT_STAFF', label: 'Support / Invigilator', badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  { id: 'LEARNER', label: 'Student / Learner', badge: 'bg-teal-500/20 text-teal-400 border-teal-500/30' },
];

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(api.currentUser);
  const [currentRole, setCurrentRole] = useState(api.getActiveRole());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setLoading(true);
      // If token already exists, verify via /auth/me
      if (api.getToken()) {
        const user = await api.getMe();
        setCurrentUser(user);
        setCurrentRole(user.role);
        api.setSession(api.getToken(), user);
      } else {
        // Initialize default operator session: Academic Administrator / Exam Officer
        const data = await api.devSwitchRole('ACADEMIC_ADMINISTRATOR');
        setCurrentUser(data.user);
        setCurrentRole(data.user.role);
      }
    } catch (err) {
      console.warn('Initial session establishment failed, falling back to operator login:', err);
      try {
        const data = await api.devSwitchRole('ACADEMIC_ADMINISTRATOR');
        setCurrentUser(data.user);
        setCurrentRole(data.user.role);
      } catch (fallbackErr) {
        console.error('Critical auth fallback failed:', fallbackErr);
      }
    } finally {
      setLoading(false);
    }
  };

  const switchRole = async (role) => {
    try {
      setLoading(true);
      const data = await api.devSwitchRole(role);
      setCurrentUser(data.user);
      setCurrentRole(data.user.role);
      return data.user;
    } catch (err) {
      console.error('Role switch failed:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        currentRole,
        currentUser,
        switchRole,
        availableRoles: ROLES,
        loading,
        isAdmin: ['ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR', 'EXAM_OFFICER'].includes(currentRole),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
