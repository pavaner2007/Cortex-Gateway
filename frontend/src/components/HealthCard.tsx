import { type LucideIcon, CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import type { ServiceStatus } from '@/types'

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

interface HealthCardProps {
  title: string
  status: ServiceStatus | undefined
  icon: LucideIcon
  isLoading?: boolean
  description?: string
  detail?: string
}

// ─────────────────────────────────────────────────────────────────────────────
// Status helpers
// ─────────────────────────────────────────────────────────────────────────────

const statusConfig = {
  connected: {
    label:       'Connected',
    dotClass:    'connected',
    labelClass:  'text-accent-emerald',
    bgGlow:      'before:from-accent-emerald/5',
    borderColor: 'border-accent-emerald/20',
    Icon:        CheckCircle2,
    iconClass:   'text-accent-emerald',
  },
  disconnected: {
    label:       'Disconnected',
    dotClass:    'disconnected',
    labelClass:  'text-accent-rose',
    bgGlow:      'before:from-accent-rose/5',
    borderColor: 'border-accent-rose/20',
    Icon:        XCircle,
    iconClass:   'text-accent-rose',
  },
  degraded: {
    label:       'Degraded',
    dotClass:    'degraded',
    labelClass:  'text-accent-amber',
    bgGlow:      'before:from-accent-amber/5',
    borderColor: 'border-accent-amber/20',
    Icon:        AlertCircle,
    iconClass:   'text-accent-amber',
  },
} as const

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export default function HealthCard({
  title,
  status,
  icon: ServiceIcon,
  isLoading = false,
  description,
  detail,
}: HealthCardProps) {
  const config = status ? statusConfig[status] : null
  const StatusIcon = config?.Icon

  return (
    <div
      className={clsx(
        // Base card
        'relative overflow-hidden glass-card p-5 animate-slide-up',
        'border transition-all duration-300',
        // Dynamic border colour based on status
        config ? config.borderColor : 'border-white/5',
        // Subtle top gradient per status
        'before:absolute before:inset-0 before:bg-gradient-to-br',
        config ? config.bgGlow : 'before:from-white/2',
        'before:to-transparent before:pointer-events-none',
        // Hover lift
        'hover:translate-y-[-2px] hover:shadow-card',
      )}
    >
      {/* Service icon — top right */}
      <div className="absolute top-4 right-4 opacity-10">
        <ServiceIcon className="w-10 h-10 text-white" />
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-white/5 border border-white/10">
            <ServiceIcon className="w-4.5 h-4.5 text-slate-300" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{title}</p>
            {description && (
              <p className="text-xs text-slate-500 mt-0.5">{description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Status */}
      {isLoading ? (
        <div className="flex items-center gap-2 text-slate-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Checking…</span>
        </div>
      ) : config ? (
        <div className="flex items-center gap-2">
          <span className={clsx('status-dot', config.dotClass)} />
          <span className={clsx('text-sm font-semibold', config.labelClass)}>
            {config.label}
          </span>
          {StatusIcon && (
            <StatusIcon className={clsx('w-4 h-4 ml-auto', config.iconClass)} />
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2 text-slate-500">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-600 inline-block" />
          <span className="text-sm">Unknown</span>
        </div>
      )}

      {/* Optional detail line */}
      {detail && (
        <p className="mt-2 text-xs font-mono text-slate-500 truncate">{detail}</p>
      )}
    </div>
  )
}
