interface NavigationProps {
  currentView: 'home' | 'new-test' | 'history' | 'results';
  onViewChange: (view: 'home' | 'new-test' | 'history' | 'results') => void;
  selectedTestId?: string;
}

export default function Navigation({ currentView, onViewChange, selectedTestId }: NavigationProps) {
  return (
    <nav className="bg-slate-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold">LLM Classifier Testing</h1>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={() => onViewChange('home')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentView === 'home'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onViewChange('new-test')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentView === 'new-test'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              New Test
            </button>
            <button
              onClick={() => onViewChange('history')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentView === 'history'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              History
            </button>
            {selectedTestId && (
              <button
                onClick={() => onViewChange('results')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'results'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                View Results
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
