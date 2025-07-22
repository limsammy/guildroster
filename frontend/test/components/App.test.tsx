import React from 'react'
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import App from '../../app/root.tsx'

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    // The App component renders an Outlet, so we just check it doesn't crash
    expect(document.body).toBeInTheDocument()
  })
}) 