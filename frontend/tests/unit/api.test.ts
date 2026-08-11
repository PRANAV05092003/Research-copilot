import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '../../src/lib/api'

// Mock axios methods
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: vi.fn(), eject: vi.fn() }
        },
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
      }))
    }
  }
})

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('creates an axios instance', () => {
    expect(api).toBeDefined()
  })
})
