import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Welcome } from '../../app/welcome/welcome.tsx'

describe('Welcome', () => {
  it('renders the message prop', () => {
    const testMessage = 'Hello, World!'
    render(<Welcome message={testMessage} />)
    
    expect(screen.getByText(testMessage)).toBeInTheDocument()
  })

  it('renders with proper heading structure', () => {
    render(<Welcome message="Test Message" />)
    
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toBeInTheDocument()
    expect(heading).toHaveTextContent('Test Message')
  })

  it('renders navigation with resources', () => {
    render(<Welcome message="Test Message" />)
    
    expect(screen.getByText("What's next?")).toBeInTheDocument()
    expect(screen.getByText('React Router Docs')).toBeInTheDocument()
    expect(screen.getByText('Join Discord')).toBeInTheDocument()
  })

  it('renders main element with proper styling', () => {
    render(<Welcome message="Test Message" />)
    
    const mainElement = screen.getByRole('main')
    expect(mainElement).toBeInTheDocument()
    expect(mainElement).toHaveClass('flex', 'h-screen', 'items-center', 'justify-center')
  })
}) 