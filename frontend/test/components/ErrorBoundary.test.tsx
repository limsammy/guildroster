import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '../../app/root.tsx'

describe('ErrorBoundary', () => {
  it('renders error message when error occurs', () => {
    const error = new Error('Test error')
    render(<ErrorBoundary error={error} />)
    
    expect(screen.getByText('Oops!')).toBeInTheDocument()
    expect(screen.getByText('Test error')).toBeInTheDocument()
  })

  it('renders main element with proper styling', () => {
    const error = new Error('Test error')
    render(<ErrorBoundary error={error} />)
    
    const mainElement = screen.getByRole('main')
    expect(mainElement).toBeInTheDocument()
    expect(mainElement).toHaveClass('pt-16', 'p-4', 'container', 'mx-auto')
  })
}) 