// ─────────────────────────────────────────────────────────────────────────────
// Cortex Gateway – Shared TypeScript Types
// ─────────────────────────────────────────────────────────────────────────────

// ── Health ────────────────────────────────────────────────────────────────────

export type ServiceStatus = 'connected' | 'disconnected' | 'degraded'
export type OverallStatus = 'healthy' | 'degraded' | 'unhealthy'

export interface HealthResponse {
  status: OverallStatus
  database: ServiceStatus
  redis: ServiceStatus
  version: string
  timestamp: string
}

// ── Version ───────────────────────────────────────────────────────────────────

export interface VersionResponse {
  name: string
  version: string
  environment: string
  python_version: string
  platform: string
  phase: string
}

// ── Root ──────────────────────────────────────────────────────────────────────

export interface RootResponse {
  name: string
  version: string
  description: string
  docs: string
  redoc: string
  health: string
  phase: string
}

// ── Error ─────────────────────────────────────────────────────────────────────

export interface ApiError {
  error: string
  message: string
  request_id?: string
  path?: string
  detail?: unknown
}

// ── Navigation ────────────────────────────────────────────────────────────────

export interface NavItem {
  id: string
  label: string
  path: string
  icon: string
  badge?: string
  disabled?: boolean
}
