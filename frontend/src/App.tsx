import { useState } from 'react';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import NewTestPage from './pages/NewTestPage';
import TestHistoryPage from './pages/TestHistoryPage';
import TestResultsPage from './pages/TestResultsPage';

type View = 'home' | 'new-test' | 'history' | 'results';

function App() {
  const [currentView, setCurrentView] = useState<View>('home');
  const [selectedTestId, setSelectedTestId] = useState<string | undefined>();

  const handleViewChange = (view: View) => {
    setCurrentView(view);
  };

  const handleTestCreated = (testId: string) => {
    setSelectedTestId(testId);
    setCurrentView('results');
  };

  const handleViewResults = (testId: string) => {
    setSelectedTestId(testId);
    setCurrentView('results');
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Navigation
        currentView={currentView}
        onViewChange={handleViewChange}
        selectedTestId={selectedTestId}
      />

      <main className="py-8 px-4 sm:px-6 lg:px-8">
        {currentView === 'home' && <HomePage onNavigate={handleViewChange} />}

        {currentView === 'new-test' && <NewTestPage onTestCreated={handleTestCreated} />}

        {currentView === 'history' && <TestHistoryPage onViewResults={handleViewResults} />}

        {currentView === 'results' && selectedTestId && (
          <TestResultsPage testId={selectedTestId} />
        )}
      </main>
    </div>
  );
}

export default App;
