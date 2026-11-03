import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';
import LoadingState from './components/common/LoadingState';

// Auth Login View
const Login = lazy(() => import('./views/Login'));

// All 12 Operational Product Modules — Lazy-loaded for optimized startup & route splitting
const OverviewDashboard = lazy(() => import('./views/OverviewDashboard'));
const SchedulingWorkspace = lazy(() => import('./views/SchedulingWorkspace'));
const ExamManagement = lazy(() => import('./views/ExamManagement'));
const StudentManagement = lazy(() => import('./views/StudentManagement'));
const CourseManagement = lazy(() => import('./views/CourseManagement'));
const RoomManagement = lazy(() => import('./views/RoomManagement'));
const InvigilatorManagement = lazy(() => import('./views/InvigilatorManagement'));
const AccommodationManagement = lazy(() => import('./views/AccommodationManagement'));
const ExceptionCenter = lazy(() => import('./views/ExceptionCenter'));
const AnalyticsReports = lazy(() => import('./views/AnalyticsReports'));
const AuditActivity = lazy(() => import('./views/AuditActivity'));
const Administration = lazy(() => import('./views/Administration'));

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingState message="Verifying session credentials..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingState message="Checking active session..." />;
  }

  if (isAuthenticated) {
    const dest = location.state?.from?.pathname || '/';
    return <Navigate to={dest} replace />;
  }

  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<LoadingState message="Loading ExamOps module..." />}>
          <Routes>
            {/* Public Login Route */}
            <Route
              path="/login"
              element={
                <PublicOnlyRoute>
                  <Login />
                </PublicOnlyRoute>
              }
            />

            {/* Authenticated Application Shell & 12 Operational Modules */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              {/* Module 1: Overview Dashboard */}
              <Route index element={<OverviewDashboard />} />

              {/* Module 2: Scheduling Operations Center */}
              <Route path="scheduling" element={<SchedulingWorkspace />} />

              {/* Module 3: Examination Management */}
              <Route path="exams" element={<ExamManagement />} />

              {/* Module 4: Student Management */}
              <Route path="students" element={<StudentManagement />} />

              {/* Module 5: Course & Enrollment Management */}
              <Route path="courses" element={<CourseManagement />} />

              {/* Module 6: Room & Facilities Management */}
              <Route path="rooms" element={<RoomManagement />} />

              {/* Module 7: Invigilator Management */}
              <Route path="invigilators" element={<InvigilatorManagement />} />

              {/* Module 8: Accommodation Management */}
              <Route path="accommodations" element={<AccommodationManagement />} />

              {/* Module 9: Exception Center */}
              <Route path="exceptions" element={<ExceptionCenter />} />

              {/* Module 10: Analytics & Reports */}
              <Route path="analytics" element={<AnalyticsReports />} />

              {/* Module 11: Audit & Activity */}
              <Route path="audit" element={<AuditActivity />} />

              {/* Module 12: Administration & Policies */}
              <Route path="admin" element={<Administration />} />

              {/* Fallback route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}
