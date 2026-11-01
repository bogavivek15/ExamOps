import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';

// All 12 Operational Product Modules
import OverviewDashboard from './views/OverviewDashboard';
import SchedulingWorkspace from './views/SchedulingWorkspace';
import ExamManagement from './views/ExamManagement';
import StudentManagement from './views/StudentManagement';
import CourseManagement from './views/CourseManagement';
import RoomManagement from './views/RoomManagement';
import InvigilatorManagement from './views/InvigilatorManagement';
import AccommodationManagement from './views/AccommodationManagement';
import ExceptionCenter from './views/ExceptionCenter';
import AnalyticsReports from './views/AnalyticsReports';
import AuditActivity from './views/AuditActivity';
import Administration from './views/Administration';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
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
      </BrowserRouter>
    </AuthProvider>
  );
}
