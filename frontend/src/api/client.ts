import axios from 'axios'
import type { ApiError } from '@/types'

// ─────────────────────────────────────────────────────────────────────────────
// Axios Instance
// Base URL is empty so that Vite's dev proxy (/api → localhost:8000) works.
// In production, Nginx proxies /api/ to the backend container.
// ─────────────────────────────────────────────────────────────────────────────

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// ── Request Interceptor ───────────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    // Future phases will inject API keys / JWT tokens here
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response Interceptor ──────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalise error shape so callers always get a consistent ApiError object
    const apiError: ApiError = {
      error: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
    }

    if (error.response) {
      // Server returned a structured error
      const data = error.response.data as Partial<ApiError>
      apiError.error   = data.error   ?? error.response.statusText
      apiError.message = data.message ?? apiError.message
      apiError.request_id = data.request_id
      apiError.path    = data.path
      apiError.detail  = data.detail
    } else if (error.request) {
      // No response received (network error / timeout)
      apiError.error   = 'NETWORK_ERROR'
      apiError.message = 'Cannot reach the server. Check your connection.'
    } else {
      apiError.message = error.message
    }

    return Promise.reject(apiError)
  },
)

export default apiClient
