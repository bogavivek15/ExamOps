import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const ROLES = [
  { id: 'ACADEMIC_ADMINISTRATOR', label: 'Academic Administrator', badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  { id: 'PLATFORM_ADMINISTRATOR', label: 'Platform Administrator', badge: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  { id: 'INSTRUCTOR', label: 'Course Instructor', badge: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  { id: 'SUPPORT_STAFF', label: 'Support / Invigilator', badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  { id: 'LEARNER', label: 'Student / Learner', badge: 'bg-teal-500/20 text-teal-400 border-teal-500/30' },
];

export function AuthProvider({ children }) {
  const [currentRole, setCurrentRole] = useState(api.getActiveRole());
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, [currentRole]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const user = await api.getMe();
      setCurrentUser(user);
    } catch (err) {
      console.warn('Could not fetch active profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const switchRole = (role) => {
    api.setActiveRole(role);
    setCurrentRole(role);
  };

  return (
    <AuthContext.Provider
      value={{
        currentRole,
        currentUser,
        switchRole,
        availableRoles: ROLES,
        loading,
        isAdmin: ['ACADEMIC_ADMINISTRATOR', 'PLATFORM_ADMINISTRATOR'].includes(currentRole),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

