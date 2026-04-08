import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  LayoutDashboard, TestTubes, FlaskConical, FileText, ClipboardList,
  Users, Settings, LogOut, Menu, X, Beaker
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/samples', icon: TestTubes, label: 'Samples' },
  { to: '/tests', icon: FlaskConical, label: 'Tests' },
  { to: '/results', icon: ClipboardList, label: 'Results Entry' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/patients', icon: Users, label: 'Patients' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('labsync_user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('labsync_token');
    localStorage.removeItem('labsync_user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-primary-600 text-white transform transition-transform lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center gap-3 px-6 py-5 border-b border-primary-500">
          <Beaker className="w-8 h-8 text-accent-400" />
          <div>
            <h1 className="text-xl font-bold">LabSync</h1>
            <p className="text-xs text-primary-200">Lab Report Management</p>
          </div>
        </div>
        <nav className="mt-4 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-primary-700 text-accent-400' : 'text-primary-100 hover:bg-primary-500'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-primary-500">
          <div className="flex items-center justify-between">
            <div className="truncate">
              <p className="text-sm font-medium">{user.name || 'User'}</p>
              <p className="text-xs text-primary-300">{user.email}</p>
            </div>
            <button onClick={handleLogout} className="text-primary-200 hover:text-white p-1">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 lg:hidden">
          <button onClick={() => setSidebarOpen(true)} className="text-gray-600">
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-semibold text-primary-600">LabSync</h1>
        </header>
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
