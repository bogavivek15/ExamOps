import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';

// Module View Stubs (to be populated in Phase 6)
function PlaceholderView({ title, description }) {
  return (
    <div className="bg-brand-surface border border-brand-border rounded-lg p-8 text-center space-y-2">
      <h2 className="text-base font-bold text-brand-text tracking-wide">{title}</h2>
      <p className="text-xs text-brand-muted max-w-md mx-auto">{description}</p>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<PlaceholderView title="Module 1: Overview Dashboard" description="Operational summary metrics, published schedule KPIs, and system telemetry." />} />
            <Route path="scheduling" element={<PlaceholderView title="Module 2: Scheduling Workspace" description="Intelligent timetable operations, solver execution, and conflict resolution." />} />
            <Route path="exceptions" element={<PlaceholderView title="Module 9: Exception Center" description="Detailed inspection and corrective resolution of unassigned exams." />} />
            <Route path="exams" element={<PlaceholderView title="Module 3: Examination Management" description="Course examinations, duration requirements, and equipment profiles." />} />
            <Route path="students" element={<PlaceholderView title="Module 4: Student Management" description="Student registry, course enrollments, and individual exam timetables." />} />
            <Route path="courses" element={<PlaceholderView title="Module 5: Course & Enrollment Management" description="Course catalog and student enrollment mappings." />} />
            <Route path="rooms" element={<PlaceholderView title="Module 6: Room & Facilities Management" description="Venues, examination capacities, accessibility features, and equipment inventory." />} />
            <Route path="invigilators" element={<PlaceholderView title="Module 7: Invigilator Management" description="Invigilator profiles, availability windows, workload tracking, and shift rosters." />} />
            <Route path="accommodations" element={<PlaceholderView title="Module 8: Accommodation Management" description="Student accessibility needs, extra time allocations, and medical note protections." />} />
            <Route path="analytics" element={<PlaceholderView title="Module 10: Analytics & Reports" description="Capacity utilization, invigilator workloads, and CSV/JSON data streams." />} />
            <Route path="audit" element={<PlaceholderView title="Module 11: Audit & Activity" description="Immutable governance log of state changes, approvals, and security events." />} />
            <Route path="admin" element={<PlaceholderView title="Module 12: Administration" description="System configuration, academic period parameters, and user permissions." />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
