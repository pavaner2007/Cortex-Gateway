import {
  Database,
  Server,
  RefreshCw,
  Cpu,
  Globe,
  Clock,
  Layers,
  Zap,
  GitBranch,
  Shield,
} from 'lucide-react'
import clsx from 'clsx'
import { useHealth, useVersion } from '@/api/health'
import HealthCard from '@/components/HealthCard'

// ─────────────────────────────────────────────────────────────────────────────
// Stat Card
// ─────────────────────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string
  value: string | undefined
  icon: typeof Cpu
  loading?: boolean
}

function StatCard({ label, value, icon: Icon, loading }: StatCardProps) {
  return (
    <div className="glass-card p-4 border border-white/5 animate-fade-in">
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-3.5 h-3.5 text-slate-500" />
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</p>
      </div>
      {loading ? (
        <div className="h-5 w-24 bg-cortex-700 rounded animate-pulse" />
      ) : (
        <p className="text-sm font-semibold text-white font-mono">{value ?? '—'}</p>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Roadmap Item
// ─────────────────────────────────────────────────────────────────────────────

interface RoadmapItem {
  phase: string
  title: string
  items: string[]
  status: 'done' | 'upcoming'
  icon: typeof Layers
}

const roadmap: RoadmapItem[] = [
  {
    phase: 'Phase 1',
    title: 'Foundation',
    items: ['FastAPI + async DB', 'Redis integration', 'Structured logging', 'Dashboard'],
    status: 'done',
    icon: Layers,
  },
  {
    phase: 'Phase 2',
    title: 'Authentication',
    items: ['API key management', 'JWT tokens', 'Tenant isolation'],
    status: 'upcoming',
    icon: Shield,
  },
  {
    phase: 'Phase 3',
    title: 'Providers',
    items: ['OpenAI', 'Gemini', 'Anthropic', 'Groq', 'Ollama'],
    status: 'upcoming',
    icon: Zap,
  },
  {
    phase: 'Phase 4',
    title: 'Routing',
    items: ['Intelligent selection', 'Fallback chains', 'Cost optimisation'],
    status: 'upcoming',
    icon: GitBranch,
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard Page
// ─────────────────────────────────────────────────────────────────────────────

export default function Dashboard() {
  const { data: health, isLoading: healthLoading, isError: healthError, refetch } = useHealth()
  const { data: version, isLoading: versionLoading } = useVersion()

  const lastChecked = health?.timestamp
    ? new Date(health.timestamp).toLocaleTimeString()
    : null

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto animate-fade-in">

      {/* ── Hero Banner ──────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden glass-card border border-white/5 p-8 rounded-2xl">
        {/* Background mesh */}
        <div className="absolute inset-0 bg-mesh-gradient opacity-60 pointer-events-none" />
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-primary-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-accent-cyan/8 rounded-full blur-2xl pointer-events-none" />

        <div className="relative flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary-600/20 border border-primary-500/30 text-xs font-semibold text-primary-400">
                <span className="w-1.5 h-1.5 rounded-full bg-primary-400" />
                Phase 1 — Foundation
              </span>
            </div>

            <h1 className="text-3xl font-bold text-gradient mb-2">
              Cortex Gateway
            </h1>
            <p className="text-slate-400 text-sm max-w-md">
              Enterprise AI Infrastructure Platform — route, observe, and control all your
              LLM traffic from a single unified control plane.
            </p>
          </div>

          <div className="hidden md:flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-violet shadow-glow-md">
            <Cpu className="w-8 h-8 text-white" />
          </div>
        </div>
      </div>

      {/* ── Infrastructure Health ─────────────────────────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Infrastructure Health</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              {lastChecked ? `Last checked at ${lastChecked}` : 'Polling every 30 seconds'}
            </p>
          </div>
          <button
            id="refresh-health-btn"
            onClick={() => refetch()}
            disabled={healthLoading}
            className="btn-primary text-xs"
            title="Refresh health status"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', healthLoading && 'animate-spin')} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <HealthCard
            title="PostgreSQL"
            description="Primary database"
            icon={Database}
            status={healthError ? 'disconnected' : health?.database}
            isLoading={healthLoading}
            detail="asyncpg · SQLAlchemy 2.x"
          />
          <HealthCard
            title="Redis"
            description="Cache & session store"
            icon={Server}
            status={healthError ? 'disconnected' : health?.redis}
            isLoading={healthLoading}
            detail="redis.asyncio"
          />
          <HealthCard
            title="API Backend"
            description="FastAPI application"
            icon={Globe}
            status={healthError ? 'disconnected' : (health ? 'connected' : undefined)}
            isLoading={healthLoading}
            detail={`v${health?.version ?? '…'} · Uvicorn`}
          />
        </div>
      </section>

      {/* ── System Info ───────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-semibold text-white mb-4">System Information</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <StatCard
            label="Version"
            value={version?.version}
            icon={Layers}
            loading={versionLoading}
          />
          <StatCard
            label="Environment"
            value={version?.environment}
            icon={Globe}
            loading={versionLoading}
          />
          <StatCard
            label="Python"
            value={version?.python_version}
            icon={Cpu}
            loading={versionLoading}
          />
          <StatCard
            label="Platform"
            value={version?.platform}
            icon={Server}
            loading={versionLoading}
          />
        </div>
      </section>

      {/* ── Roadmap ───────────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-semibold text-white mb-4">Development Roadmap</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {roadmap.map((item) => {
            const Icon = item.icon
            const isDone = item.status === 'done'

            return (
              <div
                key={item.phase}
                className={clsx(
                  'glass-card p-5 border animate-slide-up',
                  isDone
                    ? 'border-primary-500/30 bg-primary-600/5'
                    : 'border-white/5',
                )}
              >
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className={clsx(
                      'flex items-center justify-center w-8 h-8 rounded-lg',
                      isDone
                        ? 'bg-primary-600/30 text-primary-400'
                        : 'bg-white/5 text-slate-500',
                    )}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <p className={clsx('text-xs font-medium', isDone ? 'text-primary-400' : 'text-slate-500')}>
                      {item.phase}
                    </p>
                    <p className={clsx('text-sm font-semibold', isDone ? 'text-white' : 'text-slate-400')}>
                      {item.title}
                    </p>
                  </div>
                  {isDone && (
                    <span className="ml-auto px-1.5 py-0.5 rounded text-[9px] font-bold bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/20">
                      LIVE
                    </span>
                  )}
                </div>

                <ul className="space-y-1">
                  {item.items.map((feat) => (
                    <li
                      key={feat}
                      className={clsx(
                        'flex items-center gap-1.5 text-xs',
                        isDone ? 'text-slate-300' : 'text-slate-600',
                      )}
                    >
                      <span className={clsx('w-1 h-1 rounded-full flex-shrink-0', isDone ? 'bg-primary-400' : 'bg-slate-700')} />
                      {feat}
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Quick Links ───────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-semibold text-white mb-4">Quick Links</h2>
        <div className="flex flex-wrap gap-3">
          {[
            { label: 'Swagger UI',  href: '/api/docs',    icon: Globe },
            { label: 'ReDoc',       href: '/api/redoc',   icon: Layers },
            { label: 'Health JSON', href: '/api/health',  icon: Clock },
          ].map(({ label, href, icon: Icon }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </a>
          ))}
        </div>
      </section>

    </div>
  )
}
