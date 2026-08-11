import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthProvider, useAuth } from '../../src/context/AuthContext'
import React from 'react'
import api from '../../src/lib/api'

vi.mock('../../src/lib/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

const TestComponent = () => {
  const { user, login, logout, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  
  return (
    <div>
      <span data-testid="status">{user ? 'logged-in' : 'logged-out'}</span>
      <button onClick={() => login('mock-token')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('provides logged-out state initially when no token', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(await screen.findByTestId('status')).toHaveTextContent('logged-out')
  })

  it('updates to logged-in when login is called', async () => {
    (api.get as any).mockResolvedValueOnce({ data: { id: '1', email: 'test@test.com', full_name: 'Test User' } })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const loginButton = await screen.findByText('Login')
    act(() => {
      loginButton.click()
    })
    
    expect(await screen.findByTestId('status')).toHaveTextContent('logged-in')
    expect(localStorage.getItem('access_token')).toBe('mock-token')
  })

  it('updates to logged-out when logout is called', async () => {
    (api.get as any).mockResolvedValueOnce({ data: { id: '1', email: 'test@test.com', full_name: 'Test User' } })
    localStorage.setItem('access_token', 'mock-token')
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(await screen.findByTestId('status')).toHaveTextContent('logged-in')
    
    const logoutButton = screen.getByText('Logout')
    act(() => {
      logoutButton.click()
    })
    
    expect(await screen.findByTestId('status')).toHaveTextContent('logged-out')
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})
