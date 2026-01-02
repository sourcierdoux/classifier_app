import { useState, useEffect } from 'react';
import type { TestResult } from '../types';
import { apiClient } from '../api/client';

interface TestResultsPageProps {
  testId: string;
}

export default function TestResultsPage({ testId }: TestResultsPageProps) {
  const [test, setTest] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTest();
    // Poll for updates if test is still running
    const interval = setInterval(() => {
      if (test && (test.status === 'pending' || test.status === 'running')) {
        loadTest();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [testId]);

  const loadTest = async () => {
    try {
      const data = await apiClient.getTest(testId);
      setTest(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load test');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !test) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          {error || 'Test not found'}
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      running: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200',
      failed: 'bg-red-100 text-red-800 border-red-200',
    };
    return badges[status as keyof typeof badges] || badges.pending;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const calculateDuration = () => {
    if (!test.started_at) return 'N/A';
    const end = test.completed_at ? new Date(test.completed_at) : new Date();
    const start = new Date(test.started_at);
    const seconds = Math.floor((end.getTime() - start.getTime()) / 1000);
    return `${seconds}s`;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-slate-800">Test Results</h2>
        <span
          className={`px-4 py-2 rounded-full text-sm font-semibold border ${getStatusBadge(
            test.status
          )}`}
        >
          {test.status.toUpperCase()}
        </span>
      </div>

      {/* Test Information */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold text-slate-800 mb-4">Test Information</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-slate-500">Test ID</p>
            <p className="font-mono text-sm text-slate-800">{test.test_id}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Mode</p>
            <p className="font-semibold text-slate-800">{test.mode.toUpperCase()}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Source Path</p>
            <p className="text-sm text-slate-800 break-all">{test.source_path}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Output Path</p>
            <p className="text-sm text-slate-800 break-all">{test.out_path}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Created At</p>
            <p className="text-sm text-slate-800">{formatDate(test.created_at)}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Duration</p>
            <p className="text-sm text-slate-800">{calculateDuration()}</p>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold text-slate-800 mb-4">Configuration</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <span className="text-sm text-slate-500 mr-2">Filters:</span>
            <span
              className={`px-2 py-1 rounded text-xs font-semibold ${
                test.use_filter ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}
            >
              {test.use_filter ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div className="flex items-center">
            <span className="text-sm text-slate-500 mr-2">Async Mode:</span>
            <span
              className={`px-2 py-1 rounded text-xs font-semibold ${
                test.async_mode ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}
            >
              {test.async_mode ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div>
            <span className="text-sm text-slate-500 mr-2">Max Concurrency:</span>
            <span className="text-sm font-semibold text-slate-800">{test.max_concurrency}</span>
          </div>
        </div>
      </div>

      {/* Results */}
      {test.status === 'completed' && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Results</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-slate-600 mb-1">Total Emails</p>
              <p className="text-3xl font-bold text-blue-600">{test.total_emails || 0}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-slate-600 mb-1">Processed</p>
              <p className="text-3xl font-bold text-purple-600">{test.processed_emails || 0}</p>
            </div>
          </div>

          {(test.mode === 'sr' || test.mode === 'both') && (
            <div className="mt-6">
              <h4 className="font-semibold text-slate-800 mb-3">Service Request Classification</h4>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-slate-600 mb-1">SR Positive</p>
                  <p className="text-2xl font-bold text-green-600">{test.sr_positive || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {test.total_emails
                      ? `${((test.sr_positive || 0) / test.total_emails * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <p className="text-sm text-slate-600 mb-1">SR Negative</p>
                  <p className="text-2xl font-bold text-red-600">{test.sr_negative || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {test.total_emails
                      ? `${((test.sr_negative || 0) / test.total_emails * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {test.category_breakdown && Object.keys(test.category_breakdown).length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-slate-800 mb-3">Category Breakdown</h4>
              <div className="bg-slate-50 rounded-lg p-4">
                {Object.entries(test.category_breakdown).map(([category, count]) => (
                  <div key={category} className="flex justify-between items-center py-2 border-b last:border-b-0">
                    <span className="text-sm text-slate-700">{category}</span>
                    <span className="font-semibold text-slate-800">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {test.status === 'failed' && test.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-red-800 mb-2">Error</h3>
          <p className="text-sm text-red-700">{test.error_message}</p>
        </div>
      )}

      {/* Running Indicator */}
      {(test.status === 'pending' || test.status === 'running') && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 flex items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div>
          <div>
            <p className="font-semibold text-blue-800">Test in progress...</p>
            <p className="text-sm text-blue-600">This page will update automatically</p>
          </div>
        </div>
      )}
    </div>
  );
}
