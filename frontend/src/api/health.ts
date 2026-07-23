import { useQuery } from '@tanstack/react-query'
import apiClient from './client'
import type { HealthResponse, RootResponse, VersionResponse } from '@/types'

// ─────────────────────────────────────────────────────────────────────────────
// Query Keys
// ─────────────────────────────────────────────────────────────────────────────
export const healthKeys = {
  all:     ['health']     as const,
  root:    ['root']       as const,
  version: ['version']    as const,
}

// ─────────────────────────────────────────────────────────────────────────────
// Fetchers
// ─────────────────────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health')
  return data
}

export async function fetchRoot(): Promise<RootResponse> {
  const { data } = await apiClient.get<RootResponse>('/')
  return data
}

export async function fetchVersion(): Promise<VersionResponse> {
  const { data } = await apiClient.get<VersionResponse>('/version')
  return data
}

// ─────────────────────────────────────────────────────────────────────────────
// React Query Hooks
// ─────────────────────────────────────────────────────────────────────────────

/** Poll /health every 30 seconds. */
export function useHealth() {
  return useQuery({
    queryKey: healthKeys.all,
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    refetchIntervalInBackground: false,
  })
}

/** Fetch version metadata (rarely changes, long stale time). */
export function useVersion() {
  return useQuery({
    queryKey: healthKeys.version,
    queryFn: fetchVersion,
    staleTime: 5 * 60_000,  // 5 minutes
  })
}
