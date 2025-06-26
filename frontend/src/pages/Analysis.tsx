import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { sourcesAPI, businessInterestAPI, newsAPI } from '../services/api';
import { toast } from 'react-hot-toast';
import { 
  Search, 
  Globe, 
  CheckCircle, 
  Loader, 
  ArrowRight,
  ArrowLeft,
  Target,
  BarChart3,
  Clock,
  ExternalLink,
  Calendar
} from 'lucide-react';

const Analysis: React.FC = () => {
  const [selectedSources, setSelectedSources] = useState<number[]>([]);
  const [selectedBusinessInterest, setSelectedBusinessInterest] = useState<number | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch sources
  const { data: sourcesData, isLoading: sourcesLoading } = useQuery(
    'sources',
    sourcesAPI.getAll
  );

  // Fetch business interests
  const { data: businessInterests, isLoading: interestsLoading } = useQuery(
    'business-interests',
    businessInterestAPI.getAll
  );

  // Fetch latest analysis session
  const { data: latestSession } = useQuery(
    'latest-session',
    async () => {
      const sessions = await newsAPI.getSessions();
      return sessions.length > 0 ? sessions[0] : null;
    },
    {
      refetchInterval: 5000, // Refetch every 5 seconds to check for new results
    }
  );

  // Fetch latest results if session exists
  const { data: latestResults } = useQuery(
    ['latest-results', latestSession?.id],
    () => latestSession ? newsAPI.getSession(latestSession.id) : null,
    {
      enabled: !!latestSession,
      refetchInterval: 5000,
    }
  );

  // Analysis mutation
  const analysisMutation = useMutation(
    newsAPI.analyze,
    {
      onSuccess: (data) => {
        console.log('Analysis completed:', data);
        toast.success('Analysis completed successfully!');
        // Navigate to results page with session ID
        navigate(`/results/${data.session_id}`);
      },
      onError: (error: any) => {
        console.error('Analysis error:', error);
        toast.error(error.response?.data?.detail || 'Failed to complete analysis');
      },
    }
  );

  const handleSourceToggle = (sourceId: number) => {
    setSelectedSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  const handleSelectAllSources = () => {
    if (sourcesData?.sources) {
      setSelectedSources(sourcesData.sources.map(s => s.source_id));
    }
  };

  const handleDeselectAllSources = () => {
    setSelectedSources([]);
  };

  const handleStartAnalysis = async () => {
    if (selectedSources.length === 0) {
      toast.error('Please select at least one source');
      return;
    }

    if (!selectedBusinessInterest) {
      toast.error('Please select a business interest');
      return;
    }

    const selectedBusinessInterestData = businessInterests?.find(
      interest => interest.id === selectedBusinessInterest
    );

    if (!selectedBusinessInterestData) {
      toast.error('Selected business interest not found');
      return;
    }

    const selectedSourceUrls = sourcesData?.sources
      .filter(source => selectedSources.includes(source.source_id))
      .map(source => source.source_url) || [];

    setIsAnalyzing(true);
    try {
      await analysisMutation.mutateAsync({
        business_interest: selectedBusinessInterestData.interest_text,
        sources: selectedSourceUrls
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getDomainFromUrl = (url: string) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  if (sourcesLoading || interestsLoading) {
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
        <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <Search className="h-8 w-8 text-blue-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">News Analysis</h1>
        <p className="mt-2 text-gray-600">
          Select your sources and business interest to analyze news
        </p>
      </div>

      {/* Business Interest Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="h-5 w-5 mr-2" />
          Business Interest
        </h2>
        
        {businessInterests && businessInterests.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {businessInterests.map((interest) => (
              <button
                key={interest.id}
                onClick={() => setSelectedBusinessInterest(interest.id)}
                className={`p-4 rounded-lg border transition-colors text-left ${
                  selectedBusinessInterest === interest.id
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{interest.interest_text}</span>
                  {selectedBusinessInterest === interest.id && (
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                  )}
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No business interests found</p>
            <button
              onClick={() => navigate('/business-interest')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              Add Business Interest
            </button>
          </div>
        )}
      </div>

      {/* Source Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            News Sources ({selectedSources.length} selected)
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={handleSelectAllSources}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Select All
            </button>
            <button
              onClick={handleDeselectAllSources}
              className="text-sm text-gray-600 hover:text-gray-700"
            >
              Deselect All
            </button>
          </div>
        </div>

        {sourcesData && sourcesData.sources.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {sourcesData.sources.map((source) => (
              <button
                key={source.source_id}
                onClick={() => handleSourceToggle(source.source_id)}
                className={`p-4 rounded-lg border transition-colors text-left ${
                  selectedSources.includes(source.source_id)
                    ? 'border-green-500 bg-green-50 text-green-900'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">
                      {getDomainFromUrl(source.source_url)}
                    </div>
                    <div className="text-sm text-gray-500 truncate">
                      {source.source_url}
                    </div>
                  </div>
                  {selectedSources.includes(source.source_id) && (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  )}
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No sources found</p>
            <button
              onClick={() => navigate('/sources')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
            >
              Add Sources
            </button>
          </div>
        )}
      </div>

      {/* Analysis Summary */}
      {(selectedSources.length > 0 || selectedBusinessInterest) && (
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Analysis Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <Target className="h-5 w-5 text-blue-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Business Interest</p>
                  <p className="font-medium">
                    {selectedBusinessInterest 
                      ? businessInterests?.find(i => i.id === selectedBusinessInterest)?.interest_text
                      : 'Not selected'
                    }
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-green-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Sources Selected</p>
                  <p className="font-medium">{selectedSources.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-purple-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Estimated Time</p>
                  <p className="font-medium">2-5 minutes</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Latest Results */}
      {latestResults && (
        <div className="bg-green-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Latest Analysis Results
          </h3>
          
          {/* Summary Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <BarChart3 className="h-4 w-4 text-blue-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-600">Total Articles</p>
                  <p className="text-lg font-bold text-gray-900">
                    {latestResults.total_articles}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-600">Relevant Articles</p>
                  <p className="text-lg font-bold text-gray-900">
                    {latestResults.relevant_articles}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Clock className="h-4 w-4 text-purple-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-600">Analysis Date</p>
                  <p className="text-sm font-bold text-gray-900">
                    {new Date(latestResults.analysis_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Calendar className="h-4 w-4 text-orange-600" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-600">Session ID</p>
                  <p className="text-sm font-bold text-gray-900">
                    #{latestSession?.id}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Sample Articles */}
          {latestResults.articles && latestResults.articles.length > 0 && (
            <div className="mb-4">
              <h4 className="text-md font-semibold text-green-800 mb-3">Sample Articles</h4>
              <div className="space-y-3">
                {latestResults.articles.slice(0, 3).map((article, index) => (
                  <div
                    key={index}
                    className="bg-white p-4 rounded-lg border border-green-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900 mb-1">
                          {article.title}
                        </h5>
                        <p className="text-sm text-gray-600 mb-2">
                          {article.content.substring(0, 150)}...
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {article.published_date || 'Date not available'}
                          </span>
                          <span className="font-medium text-gray-700">{article.source}</span>
                        </div>
                      </div>
                      {article.url && (
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-4 p-2 text-gray-400 hover:text-green-600 transition-colors"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={() => navigate(`/results/${latestSession?.id}`)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <BarChart3 className="mr-2 h-4 w-4" />
              View Full Results
            </button>
            <button
              onClick={() => queryClient.invalidateQueries(['latest-results', latestSession?.id])}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <ArrowRight className="mr-2 h-4 w-4" />
              Refresh Results
            </button>
          </div>
        </div>
      )}

      {/* Navigation and Actions */}
      <div className="flex justify-between">
        <button
          onClick={() => navigate('/sources')}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Sources
        </button>
        <button
          onClick={handleStartAnalysis}
          disabled={isAnalyzing || selectedSources.length === 0 || !selectedBusinessInterest}
          className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? (
            <>
              <Loader className="animate-spin -ml-1 mr-2 h-4 w-4" />
              Analyzing...
            </>
          ) : (
            <>
              Start Analysis
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default Analysis; 