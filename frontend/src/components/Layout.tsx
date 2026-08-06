import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Activity,
  Zap,
  Shield,
  Settings,
  GitBranch,
  BarChart3,
  ChevronRight,
  Cpu,
} from 'lucide-react'
import clsx from 'clsx'
import { useHealth, useVersion } from '@/api/health'

// ─────────────────────────────────────────────────────────────────────────────
// Navigation config
// ─────────────────────────────────────────────────────────────────────────────

const navItems = [
  { id: 'dashboard', label: 'Dashboard',   path: '/dashboard', icon: LayoutDashboard, disabled: false },
  { id: 'providers', label: 'Providers',   path: '/providers', icon: Zap,             disabled: true,  badge: 'Phase 3' },
  { id: 'routing',   label: 'Routing',     path: '/routing',   icon: GitBranch,       disabled: true,  badge: 'Phase 3' },
  { id: 'analytics', label: 'Analytics',   path: '/analytics', icon: BarChart3,       disabled: true,  badge: 'Phase 5' },
  { id: 'auth',      label: 'Auth',        path: '/auth',      icon: Shield,          disabled: true,  badge: 'Phase 4' },
  { id: 'settings',  label: 'Settings',    path: '/settings',  icon: Settings,        disabled: true  },
]

// ─────────────────────────────────────────────────────────────────────────────
// System status badge
// ─────────────────────────────────────────────────────────────────────────────

function SystemStatusBadge({ compact = false }: { compact?: boolean }) {
  const { data, isLoading, isError } = useHealth()

  if (isLoading) {
    return (
      <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--c-text-muted)' }}>
        <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--c-mid)' }} />
        {!compact && 'Checking…'}
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: '#EF4444' }}>
        <div className="status-dot disconnected" />
        {!compact && 'Unreachable'}
      </div>
    )
  }

  const isHealthy  = data.status === 'healthy'
  const isDegraded = data.status === 'degraded'

  return (
    <div
      className="flex items-center gap-1.5 text-xs font-semibold"
      style={{ color: isHealthy ? '#059669' : isDegraded ? '#B45309' : '#EF4444' }}
    >
      <div className={clsx('status-dot', isHealthy ? 'connected' : isDegraded ? 'degraded' : 'disconnected')} />
      {!compact && (isHealthy ? 'All Systems Operational' : isDegraded ? 'Partially Degraded' : 'System Unhealthy')}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Layout
// ─────────────────────────────────────────────────────────────────────────────

export default function Layout() {
  const location = useLocation()
  const { data: version } = useVersion()

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--c-bg)' }}>

      {/* ── Sidebar ──────────────────────────────────────────────────────────── */}
      <aside
        className="relative flex flex-col w-64 flex-shrink-0 border-r cx-surface animate-fade-in"
        style={{ borderColor: 'rgba(144,202,249,0.45)' }}
      >
        {/* Decorative top gradient */}
        <div
          className="absolute top-0 left-0 right-0 h-40 pointer-events-none"
          style={{ background: 'linear-gradient(180deg, rgba(33,150,243,0.07) 0%, transparent 100%)' }}
        />

        {/* Logo */}
        <div
          className="relative flex items-center gap-3 px-5 h-16 flex-shrink-0"
          style={{ borderBottom: '1px solid rgba(144,202,249,0.45)' }}
        >
          <div
            className="flex items-center justify-center w-9 h-9 rounded-xl flex-shrink-0 shadow-glow"
            style={{ background: 'linear-gradient(135deg, #2196F3, #0D47A1)' }}
          >
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold" style={{ color: 'var(--c-deep)' }}>Cortex</p>
            <p className="text-xs font-medium" style={{ color: 'var(--c-text-muted)' }}>Gateway</p>
          </div>
          {/* Live indicator */}
          <div className="ml-auto flex items-center gap-1">
            <div className="status-dot connected" />
          </div>
        </div>

        {/* Navigation */}
        <nav className="relative flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          <p
            className="px-3 mb-3 text-[10px] font-bold uppercase tracking-widest"
            style={{ color: 'var(--c-mid)', letterSpacing: '0.12em' }}
          >
            Navigation
          </p>

          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            if (item.disabled) {
              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm cursor-not-allowed select-none"
                  style={{ color: 'rgba(21,101,192,0.40)' }}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span className="cx-pill text-[9px]">{item.badge}</span>
                  )}
                </div>
              )
            }

            return (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) => clsx('nav-item', isActive && 'active')}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="flex-1">{item.label}</span>
                {isActive && <ChevronRight className="w-3.5 h-3.5 opacity-40" />}
              </NavLink>
            )
          })}
        </nav>

        {/* Sidebar Footer */}
        <div
          className="relative px-4 py-4 space-y-2.5"
          style={{ borderTop: '1px solid rgba(144,202,249,0.45)' }}
        >
          <SystemStatusBadge />
          <div
            className="flex items-center gap-2 text-xs font-medium"
            style={{ color: 'var(--c-text-muted)' }}
          >
            <Activity className="w-3 h-3" />
            <span>v{version?.version ?? '2.0.0'} · Phase 2</span>
          </div>
        </div>
      </aside>

      {/* ── Main Area ────────────────────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 overflow-hidden">

        {/* Top Header */}
        <header
          className="flex items-center justify-between px-6 h-16 flex-shrink-0 cx-surface"
          style={{ borderBottom: '1px solid rgba(144,202,249,0.45)' }}
        >
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm font-medium" style={{ color: 'var(--c-text-muted)' }}>
            <span style={{ color: 'var(--c-deep)' }}>Cortex Gateway</span>
            <ChevronRight className="w-3.5 h-3.5 opacity-40" />
            <span style={{ color: 'var(--c-accent)' }}>
              {navItems.find((n) => location.pathname.startsWith(n.path))?.label ?? 'Dashboard'}
            </span>
          </div>

          {/* Header right */}
          <div className="flex items-center gap-4">
            <SystemStatusBadge />
            <div style={{ width: 1, height: 20, background: 'rgba(144,202,249,0.55)' }} />
            {/* Phase badge */}
            <span className="cx-badge cx-badge-blue">Phase 2 · Multi-LLM</span>
            <div
              className="flex items-center justify-center w-8 h-8 rounded-lg text-xs font-bold text-white"
              style={{ background: 'linear-gradient(135deg, #2196F3, #0D47A1)' }}
            >
              CG
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
