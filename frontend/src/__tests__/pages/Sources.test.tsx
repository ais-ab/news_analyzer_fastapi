import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Sources from '../../pages/Sources';

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
      sources: [
        { id: 1, url: 'https://example.com', name: 'Example News', is_active: true },
        { id: 2, url: 'https://test.com', name: 'Test News', is_active: false },
      ],
      popular_sources: [
        { url: 'https://cnn.com', name: 'CNN' },
        { url: 'https://bbc.com', name: 'BBC' },
      ],
    },
    isLoading: false,
    error: null,
  }),
  useMutation: () => ({
    mutate: jest.fn(),
    isLoading: false,
    error: null,
  }),
}));

describe('Sources Page', () => {
  test('renders sources page title', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Manage Sources')).toBeInTheDocument();
  });

  test('renders add source form', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    expect(screen.getByLabelText('Source URL')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add Source' })).toBeInTheDocument();
  });

  test('renders current sources list', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Example News')).toBeInTheDocument();
    expect(screen.getByText('Test News')).toBeInTheDocument();
    expect(screen.getByText('https://example.com')).toBeInTheDocument();
    expect(screen.getByText('https://test.com')).toBeInTheDocument();
  });

  test('renders popular sources section', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Popular Sources')).toBeInTheDocument();
    expect(screen.getByText('CNN')).toBeInTheDocument();
    expect(screen.getByText('BBC')).toBeInTheDocument();
  });

  test('can input source URL', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    const urlInput = screen.getByLabelText('Source URL');
    fireEvent.change(urlInput, { target: { value: 'https://news.com' } });
    
    expect(urlInput).toHaveValue('https://news.com');
  });

  test('shows active/inactive status for sources', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    // Should show active status for first source
    expect(screen.getByText('Active')).toBeInTheDocument();
    // Should show inactive status for second source
    expect(screen.getByText('Inactive')).toBeInTheDocument();
  });

  test('renders remove buttons for sources', () => {
    render(
      <BrowserRouter>
        <Sources />
      </BrowserRouter>
    );
    
    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    expect(removeButtons.length).toBeGreaterThan(0);
  });
}); 