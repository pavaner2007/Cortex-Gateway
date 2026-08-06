import { type LucideIcon, CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import type { ServiceStatus } from '@/types'

interface HealthCardProps {
  title: string
  status: ServiceStatus | undefined
  icon: LucideIcon
  isLoading?: boolean
  description?: string
  detail?: string
}

const statusConfig = {
  connected: {
    label:      'Connected',
    dotClass:   'connected',
    labelColor: '#059669',
    borderColor:'rgba(16,185,129,0.30)',
    bgColor:    'rgba(16,185,129,0.06)',
    Icon:       CheckCircle2,
    iconColor:  '#059669',
  },
  disconnected: {
    label:      'Disconnected',
    dotClass:   'disconnected',
    labelColor: '#DC2626',
    borderColor:'rgba(239,68,68,0.30)',
    bgColor:    'rgba(239,68,68,0.06)',
    Icon:       XCircle,
    iconColor:  '#DC2626',
  },
  degraded: {
    label:      'Degraded',
    dotClass:   'degraded',
    labelColor: '#B45309',
    borderColor:'rgba(245,158,11,0.30)',
    bgColor:    'rgba(245,158,11,0.06)',
    Icon:       AlertCircle,
    iconColor:  '#B45309',
  },
} as const

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
      className="relative overflow-hidden cx-card p-5 animate-slide-up group"
      style={{
        borderColor: config ? config.borderColor : 'rgba(144,202,249,0.55)',
        background: config
          ? `linear-gradient(160deg, rgba(255,255,255,0.85) 60%, ${config.bgColor} 100%)`
          : 'rgba(255,255,255,0.72)',
      }}
    >
      {/* Watermark icon — top right */}
      <div
        className="absolute top-3 right-3 transition-opacity duration-300 opacity-10 group-hover:opacity-18"
        style={{ color: config?.labelColor ?? 'var(--c-accent)' }}
      >
        <ServiceIcon className="w-12 h-12" />
      </div>

      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div
          className="flex items-center justify-center w-10 h-10 rounded-xl flex-shrink-0"
          style={{
            background: 'linear-gradient(135deg, rgba(33,150,243,0.15), rgba(13,71,161,0.10))',
            border: '1px solid rgba(33,150,243,0.25)',
          }}
        >
          <ServiceIcon className="w-5 h-5" style={{ color: 'var(--c-accent)' }} />
        </div>
        <div>
          <p className="text-sm font-bold" style={{ color: 'var(--c-deep)' }}>{title}</p>
          {description && (
            <p className="text-xs mt-0.5" style={{ color: 'var(--c-text-muted)' }}>{description}</p>
          )}
        </div>
      </div>

      {/* Status */}
      {isLoading ? (
        <div className="flex items-center gap-2" style={{ color: 'var(--c-text-muted)' }}>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm font-medium">Checking…</span>
        </div>
      ) : config ? (
        <div className="flex items-center gap-2">
          <span className={clsx('status-dot', config.dotClass)} />
          <span className="text-sm font-semibold" style={{ color: config.labelColor }}>
            {config.label}
          </span>
          {StatusIcon && (
            <StatusIcon className="w-4 h-4 ml-auto" style={{ color: config.iconColor }} />
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2" style={{ color: 'var(--c-text-muted)' }}>
          <span className="w-2 h-2 rounded-full inline-block" style={{ background: 'var(--c-mid)' }} />
          <span className="text-sm font-medium">Unknown</span>
        </div>
      )}

      {/* Detail */}
      {detail && (
        <p
          className="mt-3 text-xs font-mono truncate px-2 py-1 rounded-lg"
          style={{
            color: 'var(--c-text-muted)',
            background: 'rgba(144,202,249,0.18)',
          }}
        >
          {detail}
        </p>
      )}
    </div>
  )
}
