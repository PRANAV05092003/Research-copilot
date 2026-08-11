import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../../src/App'
import React from 'react'

describe('App Routing', () => {
  it('renders the App component without crashing', () => {
    render(<App />)
    // The App component will redirect to login by default because AuthProvider is not authenticated
    // Wait for the login screen to appear
    expect(screen.getByText(/Research Copilot/i)).toBeInTheDocument()
  })
})
