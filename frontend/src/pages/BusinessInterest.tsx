import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from 'react-query';
import { businessInterestAPI } from '../services/api';
import { toast } from 'react-hot-toast';
import { FileText, ArrowRight, Loader } from 'lucide-react';

const BusinessInterest: React.FC = () => {
  const [interestText, setInterestText] = useState('');
  const navigate = useNavigate();

  const createInterestMutation = useMutation(
    businessInterestAPI.create,
    {
      onSuccess: () => {
        toast.success('Business interest saved successfully!');
        navigate('/sources');
      },
      onError: (error) => {
        toast.error('Failed to save business interest. Please try again.');
        console.error('Error:', error);
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!interestText.trim()) {
      toast.error('Please enter your business interest');
      return;
    }
    
    createInterestMutation.mutate({ interest_text: interestText.trim() });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <FileText className="h-8 w-8 text-blue-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Business Interest</h1>
        <p className="mt-2 text-gray-600">
          Describe what news topics and areas interest you most
        </p>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="interest" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your business interest
            </label>
            <textarea
              id="interest"
              rows={6}
              value={interestText}
              onChange={(e) => setInterestText(e.target.value)}
              placeholder="e.g., I'm interested in stock market trends, tech company earnings, cryptocurrency news, and economic policy changes..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              maxLength={500}
            />
            <div className="mt-2 flex justify-between text-sm text-gray-500">
              <span>Be specific about topics, industries, or regions you're interested in</span>
              <span>{interestText.length}/500</span>
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createInterestMutation.isLoading || !interestText.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createInterestMutation.isLoading ? (
                <>
                  <Loader className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Saving...
                </>
              ) : (
                <>
                  Save & Continue
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BusinessInterest; 