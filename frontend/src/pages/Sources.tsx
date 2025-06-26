import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { sourcesAPI } from '../services/api';
import { toast } from 'react-hot-toast';
import { 
  Globe, 
  Plus, 
  Trash2, 
  ExternalLink, 
  Loader, 
  CheckCircle,
  AlertCircle,
  ArrowRight
} from 'lucide-react';

const Sources: React.FC = () => {
  const [newSourceUrl, setNewSourceUrl] = useState('');
  const [isAddingSource, setIsAddingSource] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch sources
  const { data: sourcesData, isLoading: sourcesLoading } = useQuery(
    'sources',
    sourcesAPI.getAll
  );

  // Fetch popular sources
  const { data: popularSources, isLoading: popularLoading } = useQuery(
    'popular-sources',
    sourcesAPI.getPopular
  );

  // Add source mutation
  const addSourceMutation = useMutation(
    sourcesAPI.add,
    {
      onSuccess: (data) => {
        console.log('Mutation success:', data);
        toast.success('Source added successfully!');
        setNewSourceUrl('');
        queryClient.invalidateQueries('sources');
      },
      onError: (error: any) => {
        console.error('Mutation error:', error);
        toast.error(error.response?.data?.detail || 'Failed to add source');
      },
    }
  );

  // Remove source mutation
  const removeSourceMutation = useMutation(
    sourcesAPI.remove,
    {
      onSuccess: () => {
        toast.success('Source removed successfully!');
        queryClient.invalidateQueries('sources');
      },
      onError: (error: any) => {
        toast.error('Failed to remove source');
      },
    }
  );

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('handleAddSource called with URL:', newSourceUrl);
    console.log('Form event:', e);
    
    if (!newSourceUrl.trim()) {
      toast.error('Please enter a source URL');
      return;
    }

    // Validate URL format
    let url = newSourceUrl.trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }

    try {
      new URL(url); // This will throw an error if URL is invalid
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }

    setIsAddingSource(true);
    try {
      console.log('Attempting to add source:', { source_url: url });
      await addSourceMutation.mutateAsync({ source_url: url });
      console.log('Source added successfully');
    } catch (error) {
      console.error('Error adding source:', error);
    } finally {
      setIsAddingSource(false);
    }
  };

  const handleAddPopularSource = async (url: string) => {
    setIsAddingSource(true);
    try {
      await addSourceMutation.mutateAsync({ source_url: url });
    } finally {
      setIsAddingSource(false);
    }
  };

  const handleRemoveSource = async (sourceId: number) => {
    if (window.confirm('Are you sure you want to remove this source?')) {
      await removeSourceMutation.mutateAsync(sourceId);
    }
  };

  const getDomainFromUrl = (url: string) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  if (sourcesLoading || popularLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="animate-spin h-8 w-8 text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="mx-auto h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <Globe className="h-8 w-8 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">News Sources</h1>
        <p className="mt-2 text-gray-600">
          Manage your news sources and add new ones
        </p>
      </div>

      {/* Statistics */}
      {sourcesData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Globe className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sources</p>
                <p className="text-2xl font-bold text-gray-900">
                  {sourcesData.total_count}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-gray-900">
                  {sourcesData.total_count}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Plus className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ready to Add</p>
                <p className="text-2xl font-bold text-gray-900">
                  {popularSources ? Object.values(popularSources).flat().length : 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Popular Sources */}
      {popularSources && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Popular Sources</h2>
          <div className="space-y-4">
            {Object.entries(popularSources).map(([category, urls]) => (
              <div key={category}>
                <h3 className="text-lg font-medium text-gray-800 mb-2">{category}</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {urls.map((url) => {
                    const domain = getDomainFromUrl(url);
                    const isAlreadyAdded = sourcesData?.sources.some(
                      (source) => source.source_url === url
                    );
                    
                    return (
                      <button
                        key={url}
                        onClick={() => !isAlreadyAdded && handleAddPopularSource(url)}
                        disabled={isAlreadyAdded || isAddingSource}
                        className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                          isAlreadyAdded
                            ? 'bg-gray-50 border-gray-200 text-gray-500 cursor-not-allowed'
                            : 'bg-white border-gray-300 hover:border-green-500 hover:bg-green-50'
                        }`}
                      >
                        <div className="flex items-center">
                          <Globe className="h-4 w-4 mr-2" />
                          <span className="text-sm font-medium">{domain}</span>
                        </div>
                        {isAlreadyAdded ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <Plus className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add New Source */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Add New Source</h2>
        <form onSubmit={handleAddSource} className="space-y-4">
          <div>
            <label htmlFor="source-url" className="block text-sm font-medium text-gray-700 mb-2">
              Website URL
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                id="source-url"
                value={newSourceUrl}
                onChange={(e) => {
                  console.log('Input changed:', e.target.value);
                  setNewSourceUrl(e.target.value);
                }}
                placeholder="https://example.com"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
              <button
                type="submit"
                onClick={() => console.log('Submit button clicked!')}
                disabled={isAddingSource || !newSourceUrl.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAddingSource ? (
                  <>
                    <Loader className="animate-spin -ml-1 mr-2 h-4 w-4" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="-ml-1 mr-2 h-4 w-4" />
                    Add Source
                  </>
                )}
              </button>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Enter the full URL including https://
            </p>
          </div>
        </form>
      </div>

      {/* Current Sources */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Your Sources</h2>
          {sourcesData?.total_count === 0 && (
            <span className="text-sm text-gray-500">No sources added yet</span>
          )}
        </div>

        {sourcesData?.sources && sourcesData.sources.length > 0 ? (
          <div className="space-y-3">
            {sourcesData.sources.map((source) => (
              <div
                key={source.source_id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <Globe className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {getDomainFromUrl(source.source_url)}
                    </p>
                    <p className="text-xs text-gray-500">{source.source_url}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <a
                    href={source.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                  <button
                    onClick={() => handleRemoveSource(source.source_id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    title="Remove source"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No sources</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding some news sources above.
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={() => navigate('/business-interest')}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          ← Back to Business Interest
        </button>
        <button
          onClick={() => navigate('/analysis')}
          disabled={!sourcesData || sourcesData.total_count === 0}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue to Analysis
          <ArrowRight className="ml-2 h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default Sources; 