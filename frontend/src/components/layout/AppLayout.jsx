import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import AppSidebar from './AppSidebar';
import TopNavigation from './TopNavigation';

export default function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-brand-bg text-brand-text">
      {/* Left Sidebar */}
      <AppSidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopNavigation />

        <main className="flex-1 overflow-y-auto p-6 bg-brand-bg">
          <div className="max-w-7xl mx-auto space-y-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

