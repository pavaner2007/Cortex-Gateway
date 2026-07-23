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
import { useHealth } from '@/api/health'

// ─────────────────────────────────────────────────────────────────────────────
// Navigation config
// ─────────────────────────────────────────────────────────────────────────────

const navItems = [
  { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, disabled: false },
  { id: 'routing',   label: 'Routing',   path: '/routing',   icon: GitBranch,        disabled: true,  badge: 'Phase 2' },
  { id: 'providers', label: 'Providers', path: '/providers', icon: Zap,              disabled: true,  badge: 'Phase 3' },
  { id: 'analytics', label: 'Analytics', path: '/analytics', icon: BarChart3,        disabled: true,  badge: 'Phase 6' },
  { id: 'auth',      label: 'Auth',      path: '/auth',      icon: Shield,           disabled: true,  badge: 'Phase 2' },
  { id: 'settings',  label: 'Settings',  path: '/settings',  icon: Settings,         disabled: true  },
]

// ─────────────────────────────────────────────────────────────────────────────
// System status badge (top-level)
// ─────────────────────────────────────────────────────────────────────────────

function SystemStatusBadge() {
  const { data, isLoading, isError } = useHealth()

  if (isLoading) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-slate-400">
        <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-pulse" />
        Checking…
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-accent-rose">
        <div className="status-dot disconnected" />
        Unreachable
      </div>
    )
  }

  const color =
    data.status === 'healthy'   ? 'text-accent-emerald' :
    data.status === 'degraded'  ? 'text-accent-amber'   : 'text-accent-rose'

  return (
    <div className={clsx('flex items-center gap-1.5 text-xs font-medium', color)}>
      <div className={clsx('status-dot', data.status === 'healthy' ? 'connected' : data.status === 'degraded' ? 'degraded' : 'disconnected')} />
      {data.status === 'healthy' ? 'All Systems Operational' : data.status === 'degraded' ? 'Partially Degraded' : 'System Unhealthy'}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Layout Component
// ─────────────────────────────────────────────────────────────────────────────

export default function Layout() {
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden bg-cortex-950">
      {/* ── Sidebar ────────────────────────────────────────────────────────── */}
      <aside className="relative flex flex-col w-64 bg-cortex-900/80 border-r border-white/5 backdrop-blur-sm flex-shrink-0">
        {/* Subtle gradient top-left */}
        <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-br from-primary-600/10 to-transparent pointer-events-none" />

        {/* Logo */}
        <div className="relative flex items-center gap-3 px-5 h-16 border-b border-white/5">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-violet shadow-glow-sm flex-shrink-0">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white tracking-tight">Cortex</p>
            <p className="text-xs text-slate-500 font-medium">Gateway</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="relative flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
            Navigation
          </p>

          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            if (item.disabled) {
              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-600 cursor-not-allowed select-none"
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-cortex-700 text-slate-500">
                      {item.badge}
                    </span>
                  )}
                </div>
              )
            }

            return (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) =>
                  clsx('nav-item group', isActive && 'active')
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="flex-1">{item.label}</span>
                {isActive && <ChevronRight className="w-3 h-3 opacity-50" />}
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="relative px-4 py-4 border-t border-white/5 space-y-3">
          <SystemStatusBadge />
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <Activity className="w-3 h-3" />
            <span>v1.0.0 · Phase 1</span>
          </div>
        </div>
      </aside>

      {/* ── Main Content Area ─────────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 h-16 bg-cortex-900/40 border-b border-white/5 backdrop-blur-sm flex-shrink-0">
          <div className="flex items-center gap-2">
            {navItems.find((n) => location.pathname.startsWith(n.path) && !n.disabled) && (
              <span className="text-sm text-slate-400">
                {navItems.find((n) => location.pathname.startsWith(n.path))?.label}
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <SystemStatusBadge />
            <div className="w-px h-4 bg-white/10" />
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cortex-700 text-xs font-semibold text-slate-300">
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
