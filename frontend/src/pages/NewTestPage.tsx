import { useState, useEffect } from 'react';
import type { ClassifierMode, AppConfig } from '../types';
import { apiClient } from '../api/client';

interface NewTestPageProps {
  onTestCreated: (testId: string) => void;
}

export default function NewTestPage({ onTestCreated }: NewTestPageProps) {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Form state
  const [sourcePath, setSourcePath] = useState('');
  const [outPath, setOutPath] = useState('');
  const [mode, setMode] = useState<ClassifierMode>('both');
  const [useFilter, setUseFilter] = useState(true);
  const [asyncMode, setAsyncMode] = useState(true);
  const [maxConcurrency, setMaxConcurrency] = useState(20);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const cfg = await apiClient.getConfig();
      setConfig(cfg);
      setMode(cfg.default_mode);
      setUseFilter(cfg.default_use_filter);
      setAsyncMode(cfg.default_async_mode);
      setMaxConcurrency(cfg.default_max_concurrency);
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await apiClient.runTest({
        source_path: sourcePath,
        out_path: outPath,
        mode,
        use_filter: useFilter,
        async_mode: asyncMode,
        max_concurrency: maxConcurrency,
      });

      setSuccess(true);
      setTimeout(() => {
        onTestCreated(result.test_id);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-slate-800 mb-6">Launch New Test</h2>

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded">
          Test created successfully! Redirecting to results...
        </div>
      )}

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Source Path */}
        <div>
          <label htmlFor="sourcePath" className="block text-sm font-medium text-slate-700 mb-2">
            Source Path <span className="text-red-500">*</span>
          </label>
          <input
            id="sourcePath"
            type="text"
            required
            value={sourcePath}
            onChange={(e) => setSourcePath(e.target.value)}
            placeholder="/path/to/emails.csv or /path/to/folder"
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-slate-500">
            Path to source file (.csv, .xlsx) or folder containing dataframes
          </p>
        </div>

        {/* Output Path */}
        <div>
          <label htmlFor="outPath" className="block text-sm font-medium text-slate-700 mb-2">
            Output Path <span className="text-red-500">*</span>
          </label>
          <input
            id="outPath"
            type="text"
            required
            value={outPath}
            onChange={(e) => setOutPath(e.target.value)}
            placeholder="/path/to/output"
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-slate-500">
            Path where results will be saved
          </p>
        </div>

        {/* Mode Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Classification Mode
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                value="both"
                checked={mode === 'both'}
                onChange={(e) => setMode(e.target.value as ClassifierMode)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Both</strong> - SR + Category classification
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="sr"
                checked={mode === 'sr'}
                onChange={(e) => setMode(e.target.value as ClassifierMode)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>SR Only</strong> - Service Request classification
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="qf"
                checked={mode === 'qf'}
                onChange={(e) => setMode(e.target.value as ClassifierMode)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>QF Only</strong> - Category classification
              </span>
            </label>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Advanced Options</h3>

          <div className="space-y-4">
            {/* Use Filter */}
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={useFilter}
                onChange={(e) => setUseFilter(e.target.checked)}
                className="mr-3 h-4 w-4"
              />
              <div>
                <span className="text-sm font-medium text-slate-700">Use Aggressive Filters</span>
                <p className="text-xs text-slate-500">
                  Apply data filtering before classification
                </p>
              </div>
            </label>

            {/* Async Mode */}
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={asyncMode}
                onChange={(e) => setAsyncMode(e.target.checked)}
                className="mr-3 h-4 w-4"
              />
              <div>
                <span className="text-sm font-medium text-slate-700">Async Mode</span>
                <p className="text-xs text-slate-500">
                  Run predictions in parallel for faster processing
                </p>
              </div>
            </label>

            {/* Max Concurrency */}
            <div>
              <label htmlFor="maxConcurrency" className="block text-sm font-medium text-slate-700 mb-2">
                Max Concurrency: {maxConcurrency}
              </label>
              <input
                id="maxConcurrency"
                type="range"
                min="1"
                max={config?.max_concurrency_limit || 50}
                value={maxConcurrency}
                onChange={(e) => setMaxConcurrency(parseInt(e.target.value))}
                disabled={!asyncMode}
                className="w-full"
              />
              <p className="mt-1 text-xs text-slate-500">
                Number of parallel predictions (1-{config?.max_concurrency_limit || 50})
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={loading || !sourcePath || !outPath}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Starting Test...' : 'Start Test'}
          </button>
        </div>
      </form>
    </div>
  );
}
