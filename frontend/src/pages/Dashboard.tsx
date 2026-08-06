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
  MessageSquareText,
  CheckCircle2,
  ArrowUpRight,
  Sparkles,
  Activity,
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
  accent?: string
  delay?: string
}

function StatCard({ label, value, icon: Icon, loading, accent = 'var(--c-accent)', delay = '0s' }: StatCardProps) {
  return (
    <div
      className="cx-card p-4 animate-slide-up"
      style={{ animationDelay: delay }}
    >
      <div className="flex items-center justify-between mb-3">
        <div
          className="flex items-center justify-center w-8 h-8 rounded-lg"
          style={{ background: `${accent}18`, border: `1px solid ${accent}30` }}
        >
          <Icon className="w-4 h-4" style={{ color: accent }} />
        </div>
        <span
          className="text-[10px] font-bold uppercase tracking-widest"
          style={{ color: 'var(--c-mid)' }}
        >
          {label}
        </span>
      </div>
      {loading ? (
        <div className="skeleton h-5 w-24" />
      ) : (
        <p className="text-sm font-bold font-mono" style={{ color: 'var(--c-deep)' }}>
          {value ?? '—'}
        </p>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Provider Badge
// ─────────────────────────────────────────────────────────────────────────────

function ProviderBadge({
  name, model, enabled, delay = '0s'
}: { name: string; model: string; enabled: boolean; delay?: string }) {
  return (
    <div
      className="cx-card p-4 flex items-center gap-3 animate-slide-up"
      style={{ animationDelay: delay }}
    >
      <div
        className="flex items-center justify-center w-10 h-10 rounded-xl font-bold text-sm text-white flex-shrink-0"
        style={{ background: enabled ? 'linear-gradient(135deg, #2196F3, #0D47A1)' : 'rgba(144,202,249,0.35)' }}
      >
        {name[0].toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold capitalize" style={{ color: 'var(--c-deep)' }}>{name}</p>
        <p className="text-xs truncate font-mono" style={{ color: 'var(--c-text-muted)' }}>{model}</p>
      </div>
      <div className={clsx('flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-lg', enabled ? 'cx-badge-green' : 'cx-badge-amber')} style={{ fontSize: '0.7rem' }}>
        {enabled ? (
          <><CheckCircle2 className="w-3 h-3" /> Active</>
        ) : (
          <><Clock className="w-3 h-3" /> No Key</>
        )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Roadmap
// ─────────────────────────────────────────────────────────────────────────────

interface RoadmapItem {
  phase: string
  title: string
  items: string[]
  status: 'done' | 'active' | 'upcoming'
  icon: typeof Layers
}

const roadmap: RoadmapItem[] = [
  {
    phase: 'Phase 1',
    title: 'Foundation',
    items: ['FastAPI + async DB', 'Redis integration', 'Structured logging', 'Dashboard UI'],
    status: 'done',
    icon: Layers,
  },
  {
    phase: 'Phase 2',
    title: 'Multi-LLM Gateway',
    items: ['Groq provider', 'Gemini provider', 'Unified chat API', 'Provider discovery'],
    status: 'active',
    icon: Zap,
  },
  {
    phase: 'Phase 3',
    title: 'Routing & Reliability',
    items: ['Intelligent routing', 'Fallback chains', 'Circuit breakers', 'Retry logic'],
    status: 'upcoming',
    icon: GitBranch,
  },
  {
    phase: 'Phase 4',
    title: 'Auth & Teams',
    items: ['API key management', 'JWT tokens', 'Tenant isolation', 'Budget controls'],
    status: 'upcoming',
    icon: Shield,
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

      {/* ── Hero Banner ──────────────────────────────────────────────────────── */}
      <div
        className="relative overflow-hidden rounded-2xl p-8"
        style={{
          background: 'linear-gradient(135deg, #0D47A1 0%, #1565C0 40%, #2196F3 100%)',
          boxShadow: '0 12px 40px rgba(13,71,161,0.30)',
        }}
      >
        {/* Decorative circles */}
        <div
          className="absolute -top-16 -right-16 w-56 h-56 rounded-full opacity-20 pointer-events-none"
          style={{ background: 'radial-gradient(circle, #90CAF9, transparent)' }}
        />
        <div
          className="absolute -bottom-12 -left-12 w-40 h-40 rounded-full opacity-15 pointer-events-none"
          style={{ background: 'radial-gradient(circle, #E3F2FD, transparent)' }}
        />
        <div
          className="absolute top-1/2 right-1/4 w-24 h-24 rounded-full opacity-10 pointer-events-none"
          style={{ background: 'radial-gradient(circle, #42A5F5, transparent)' }}
        />

        <div className="relative flex items-start justify-between">
          <div>
            {/* Phase Badge */}
            <div className="flex items-center gap-2 mb-4">
              <span
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold"
                style={{
                  background: 'rgba(255,255,255,0.18)',
                  border: '1px solid rgba(255,255,255,0.30)',
                  color: '#E3F2FD',
                }}
              >
                <Sparkles className="w-3 h-3" />
                Phase 2 — Unified Multi-LLM Gateway
              </span>
            </div>

            <h1 className="text-3xl font-extrabold text-white mb-2 tracking-tight">
              Cortex Gateway
            </h1>
            <p className="text-sm max-w-md" style={{ color: 'rgba(227,242,253,0.80)' }}>
              Enterprise AI Infrastructure Platform — route, observe, and control all your LLM
              traffic from a single unified control plane.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-wrap gap-3 mt-6">
              <a
                href="/api/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:scale-105"
                style={{
                  background: 'rgba(255,255,255,0.18)',
                  border: '1px solid rgba(255,255,255,0.35)',
                  backdropFilter: 'blur(8px)',
                }}
              >
                <Globe className="w-4 h-4" />
                Swagger UI
                <ArrowUpRight className="w-3.5 h-3.5 opacity-70" />
              </a>
              <a
                href="/api/health"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 hover:scale-105"
                style={{
                  background: 'rgba(255,255,255,0.12)',
                  border: '1px solid rgba(255,255,255,0.25)',
                  color: 'rgba(227,242,253,0.90)',
                  backdropFilter: 'blur(8px)',
                }}
              >
                <Activity className="w-4 h-4" />
                Health JSON
              </a>
            </div>
          </div>

          {/* Hero icon */}
          <div
            className="hidden md:flex items-center justify-center w-20 h-20 rounded-2xl flex-shrink-0"
            style={{
              background: 'rgba(255,255,255,0.15)',
              border: '1px solid rgba(255,255,255,0.30)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <MessageSquareText className="w-10 h-10 text-white" />
          </div>
        </div>
      </div>

      {/* ── Infrastructure Health ─────────────────────────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold" style={{ color: 'var(--c-deep)' }}>
              Infrastructure Health
            </h2>
            <p className="text-xs mt-0.5" style={{ color: 'var(--c-text-muted)' }}>
              {lastChecked ? `Last checked at ${lastChecked}` : 'Polling every 30 seconds'}
            </p>
          </div>
          <button
            id="refresh-health-btn"
            onClick={() => refetch()}
            disabled={healthLoading}
            className="btn-primary text-xs"
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

      {/* ── Active Providers (Phase 2) ────────────────────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold" style={{ color: 'var(--c-deep)' }}>
              LLM Providers
            </h2>
            <p className="text-xs mt-0.5" style={{ color: 'var(--c-text-muted)' }}>
              Configure API keys in <code className="font-mono text-xs px-1 py-0.5 rounded" style={{ background: 'rgba(144,202,249,0.25)', color: 'var(--c-deep)' }}>.env</code> to activate providers
            </p>
          </div>
          <a
            href="/api/v1/providers"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-xs"
          >
            <Zap className="w-3.5 h-3.5" />
            View All
            <ArrowUpRight className="w-3 h-3 opacity-60" />
          </a>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <ProviderBadge
            name="groq"
            model="llama-3.3-70b-versatile"
            enabled={false}
            delay="0.05s"
          />
          <ProviderBadge
            name="gemini"
            model="gemini-1.5-flash"
            enabled={false}
            delay="0.10s"
          />
        </div>

        {/* Info banner */}
        <div
          className="mt-3 flex items-start gap-3 p-4 rounded-xl animate-fade-in"
          style={{
            background: 'rgba(33,150,243,0.07)',
            border: '1px solid rgba(33,150,243,0.20)',
            animationDelay: '0.15s',
          }}
        >
          <Sparkles className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: 'var(--c-accent)' }} />
          <p className="text-xs" style={{ color: 'var(--c-text-muted)' }}>
            Add <code className="font-mono font-semibold" style={{ color: 'var(--c-deep)' }}>GROQ_API_KEY</code> or{' '}
            <code className="font-mono font-semibold" style={{ color: 'var(--c-deep)' }}>GEMINI_API_KEY</code> to your{' '}
            <code className="font-mono font-semibold" style={{ color: 'var(--c-deep)' }}>.env</code> file and restart the backend to activate providers. Both are free.
          </p>
        </div>
      </section>

      {/* ── System Info ─────────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-bold mb-4" style={{ color: 'var(--c-deep)' }}>
          System Information
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Version"      value={version?.version}     icon={Layers}  loading={versionLoading} delay="0.05s" />
          <StatCard label="Environment"  value={version?.environment}  icon={Globe}   loading={versionLoading} delay="0.10s" accent="#0D47A1" />
          <StatCard label="Python"       value={version?.python_version} icon={Cpu}  loading={versionLoading} delay="0.15s" accent="#1565C0" />
          <StatCard label="Platform"     value={version?.platform}    icon={Server}  loading={versionLoading} delay="0.20s" accent="#2196F3" />
        </div>
      </section>

      {/* ── Roadmap ─────────────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-bold mb-4" style={{ color: 'var(--c-deep)' }}>
          Development Roadmap
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {roadmap.map((item, i) => {
            const Icon = item.icon
            const isDone   = item.status === 'done'
            const isActive = item.status === 'active'

            return (
              <div
                key={item.phase}
                className="cx-card p-5 animate-slide-up"
                style={{
                  animationDelay: `${i * 0.07}s`,
                  borderColor: isDone
                    ? 'rgba(16,185,129,0.30)'
                    : isActive
                    ? 'rgba(33,150,243,0.40)'
                    : 'rgba(144,202,249,0.45)',
                  background: isDone
                    ? 'linear-gradient(160deg, rgba(255,255,255,0.85) 60%, rgba(16,185,129,0.06) 100%)'
                    : isActive
                    ? 'linear-gradient(160deg, rgba(255,255,255,0.85) 60%, rgba(33,150,243,0.06) 100%)'
                    : 'rgba(255,255,255,0.60)',
                }}
              >
                {/* Phase header */}
                <div className="flex items-center gap-2.5 mb-4">
                  <div
                    className="flex items-center justify-center w-9 h-9 rounded-xl"
                    style={{
                      background: isDone
                        ? 'rgba(16,185,129,0.12)'
                        : isActive
                        ? 'rgba(33,150,243,0.15)'
                        : 'rgba(144,202,249,0.25)',
                      border: isDone
                        ? '1px solid rgba(16,185,129,0.25)'
                        : isActive
                        ? '1px solid rgba(33,150,243,0.30)'
                        : '1px solid rgba(144,202,249,0.40)',
                    }}
                  >
                    <Icon
                      className="w-4 h-4"
                      style={{
                        color: isDone ? '#059669' : isActive ? 'var(--c-accent)' : 'var(--c-mid)',
                      }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-[10px] font-bold uppercase tracking-wider"
                      style={{ color: isDone ? '#059669' : isActive ? 'var(--c-accent)' : 'var(--c-mid)' }}
                    >
                      {item.phase}
                    </p>
                    <p className="text-sm font-bold truncate" style={{ color: 'var(--c-deep)' }}>
                      {item.title}
                    </p>
                  </div>
                  {isDone && (
                    <span className="cx-badge cx-badge-green flex-shrink-0" style={{ fontSize: '0.65rem' }}>
                      LIVE
                    </span>
                  )}
                  {isActive && (
                    <span
                      className="cx-badge flex-shrink-0"
                      style={{
                        fontSize: '0.65rem',
                        background: 'rgba(33,150,243,0.15)',
                        color: 'var(--c-accent)',
                        border: '1px solid rgba(33,150,243,0.30)',
                      }}
                    >
                      NOW
                    </span>
                  )}
                </div>

                {/* Feature list */}
                <ul className="space-y-1.5">
                  {item.items.map((feat) => (
                    <li
                      key={feat}
                      className="flex items-center gap-2 text-xs"
                      style={{
                        color: isDone || isActive ? 'var(--c-text)' : 'rgba(21,101,192,0.45)',
                      }}
                    >
                      <span
                        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{
                          background: isDone
                            ? '#059669'
                            : isActive
                            ? 'var(--c-accent)'
                            : 'var(--c-mid)',
                        }}
                      />
                      {feat}
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Quick Links ─────────────────────────────────────────────────────── */}
      <section>
        <h2 className="text-base font-bold mb-4" style={{ color: 'var(--c-deep)' }}>
          Quick Links
        </h2>
        <div className="flex flex-wrap gap-3">
          {[
            { label: 'Swagger UI',      href: '/api/docs',           icon: Globe,           desc: 'Interactive API docs' },
            { label: 'ReDoc',           href: '/api/redoc',          icon: Layers,          desc: 'Full API reference' },
            { label: 'Health JSON',     href: '/api/health',         icon: Activity,        desc: 'System health status' },
            { label: 'Providers API',   href: '/api/v1/providers',   icon: Zap,             desc: 'Provider discovery' },
            { label: 'Chat API',        href: '/api/docs#/Chat',     icon: MessageSquareText, desc: 'Chat completions' },
          ].map(({ label, href, icon: Icon, desc }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="group cx-card p-3.5 flex items-center gap-3 min-w-[160px] no-underline"
              style={{ textDecoration: 'none' }}
            >
              <div
                className="flex items-center justify-center w-8 h-8 rounded-lg flex-shrink-0 transition-all duration-200 group-hover:scale-110"
                style={{
                  background: 'linear-gradient(135deg, rgba(33,150,243,0.15), rgba(13,71,161,0.10))',
                  border: '1px solid rgba(33,150,243,0.25)',
                }}
              >
                <Icon className="w-4 h-4" style={{ color: 'var(--c-accent)' }} />
              </div>
              <div>
                <p className="text-sm font-semibold" style={{ color: 'var(--c-deep)' }}>{label}</p>
                <p className="text-xs" style={{ color: 'var(--c-text-muted)' }}>{desc}</p>
              </div>
              <ArrowUpRight
                className="w-3.5 h-3.5 ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                style={{ color: 'var(--c-accent)' }}
              />
            </a>
          ))}
        </div>
      </section>

    </div>
  )
}
