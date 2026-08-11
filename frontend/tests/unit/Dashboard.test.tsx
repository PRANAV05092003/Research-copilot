import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Dashboard from '../../src/pages/Dashboard'
import React from 'react'

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => <a href={to}>{children}</a>
}))

describe('Dashboard Component', () => {
  it('renders overview widgets and recent activity', () => {
    render(<Dashboard />)
    
    // Check for overview cards
    expect(screen.getByText('Total Papers')).toBeInTheDocument()
    expect(screen.getByText('Active Chats')).toBeInTheDocument()
    expect(screen.getByText('Research Jobs')).toBeInTheDocument()
    
    // Check for recent activity list
    expect(screen.getByText('Recent Activity')).toBeInTheDocument()
  })
})
