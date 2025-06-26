import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../../pages/Dashboard';

// Mock the useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { client_id: 'testuser' },
  }),
}));

// Mock react-query
jest.mock('react-query', () => ({
  useQuery: () => ({
    data: {
      total_sources: 5,
      total_articles: 150,
      analysis_sessions: 3,
      recent_articles: [
        {
          id: 1,
          title: 'Test Article 1',
          url: 'https://example.com/1',
          source: 'Test Source',
          published_date: '2024-01-01',
        },
        {
          id: 2,
          title: 'Test Article 2',
          url: 'https://example.com/2',
          source: 'Test Source',
          published_date: '2024-01-02',
        },
      ],
    },
    isLoading: false,
    error: null,
  }),
}));

describe('Dashboard Page', () => {
  test('renders dashboard title and welcome message', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Welcome to your personalized news analysis dashboard')).toBeInTheDocument();
  });

  test('renders quick actions', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
    expect(screen.getByText((content) => content.includes('Set Business Interest'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Manage Sources'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Run Analysis'))).toBeInTheDocument();
  });

  test('renders recent business interests section', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
    expect(screen.getByText('Recent Business Interests')).toBeInTheDocument();
    expect(screen.getByText('No business interests yet')).toBeInTheDocument();
  });
}); 