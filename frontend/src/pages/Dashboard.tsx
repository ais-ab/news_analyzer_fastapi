import React from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import { 
  BarChart3, 
  FileText, 
  Globe, 
  ArrowRight
} from 'lucide-react';
import { format } from 'date-fns';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery(
    'dashboard',
    analysisAPI.getDashboard
  );

  const isLoading = dashboardLoading;

  const quickActions = [
    {
      title: 'Set Business Interest',
      description: 'Define what news topics interest you',
      icon: FileText,
      href: '/business-interest',
      color: 'bg-blue-500',
    },
    {
      title: 'Manage Sources',
      description: 'Add or remove news sources',
      icon: Globe,
      href: '/sources',
      color: 'bg-green-500',
    },
    {
      title: 'Run Analysis',
      description: 'Analyze news based on your interests',
      icon: BarChart3,
      href: '/analysis',
      color: 'bg-purple-500',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to your personalized news analysis dashboard
        </p>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action) => (
            <button
              key={action.title}
              onClick={() => navigate(action.href)}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow text-left group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg ${action.color}`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {action.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {action.description}
                    </p>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Business Interests</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          {dashboardData?.recent_interests && dashboardData.recent_interests.length > 0 ? (
            <div className="space-y-3">
              {dashboardData.recent_interests.map((interest) => (
                <div key={interest.id} className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-900 line-clamp-2">
                    {interest.interest_text}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {format(new Date(interest.created_at), 'MMM dd, yyyy')}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No business interests yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 