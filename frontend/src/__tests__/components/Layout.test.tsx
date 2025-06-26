import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../../components/Layout';

// Mock the useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { client_id: 'testuser' },
    logout: jest.fn(),
  }),
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Outlet: () => <div data-testid="outlet">Outlet Content</div>,
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

describe('Layout Component', () => {
  test('renders header with title', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );
    
    expect(screen.getByText('News Analyzer')).toBeInTheDocument();
  });

  test('renders sidebar navigation', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Business Interest')).toBeInTheDocument();
    expect(screen.getByText('Sources')).toBeInTheDocument();
    expect(screen.getByText('Analysis')).toBeInTheDocument();
  });

  test('renders user info in header', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );
    
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  test('renders outlet content', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });

  test('renders sign out button', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Sign Out')).toBeInTheDocument();
  });
}); 