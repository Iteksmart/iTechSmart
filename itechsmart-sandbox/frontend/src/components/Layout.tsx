import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Box,
  Code,
  Activity,
  FileText,
  TestTube,
  Settings,
  Home,
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/sandboxes', icon: Box, label: 'Sandboxes' },
    { path: '/editor', icon: Code, label: 'Code Editor' },
    { path: '/monitoring', icon: Activity, label: 'Monitoring' },
    { path: '/files', icon: FileText, label: 'Files' },
    { path: '/tests', icon: TestTube, label: 'Tests' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside
        style={{
          width: '250px',
          background: 'var(--bg-dark)',
          color: 'var(--text-inverse)',
          padding: 'var(--spacing-lg)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Logo */}
        <div style={{ marginBottom: 'var(--spacing-2xl)' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
            iTechSmart
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: 0 }}>
            Sandbox
          </p>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1 }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);

            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-md)',
                  padding: 'var(--spacing-md)',
                  borderRadius: 'var(--border-radius-sm)',
                  textDecoration: 'none',
                  color: active ? 'var(--text-inverse)' : 'var(--text-tertiary)',
                  background: active ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  marginBottom: 'var(--spacing-xs)',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <Icon size={20} />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div
          style={{
            paddingTop: 'var(--spacing-lg)',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            fontSize: '12px',
            color: 'var(--text-tertiary)',
          }}
        >
          <p style={{ margin: 0 }}>© 2025 iTechSmart Inc.</p>
          <p style={{ margin: 0 }}>Version 1.0.0</p>
        </div>
      </aside>

      {/* Main Content */}
      <main
        style={{
          flex: 1,
          padding: 'var(--spacing-xl)',
          overflowY: 'auto',
        }}
      >
        {children}
      </main>
    </div>
  );
};

export default Layout;