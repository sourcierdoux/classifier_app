interface HomePageProps {
  onNavigate: (view: 'new-test' | 'history') => void;
}

export default function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-slate-800 mb-4">
          Welcome to LLM Classifier Testing Framework
        </h2>
        <p className="text-lg text-slate-600">
          Manage and analyze your email classification tests with ease
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div
          onClick={() => onNavigate('new-test')}
          className="bg-white rounded-lg shadow-md p-8 cursor-pointer hover:shadow-xl transition-shadow border-2 border-transparent hover:border-blue-500"
        >
          <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </div>
          <h3 className="text-2xl font-semibold text-slate-800 mb-2">
            Launch New Test
          </h3>
          <p className="text-slate-600">
            Start a new classification test with custom parameters and source files
          </p>
        </div>

        <div
          onClick={() => onNavigate('history')}
          className="bg-white rounded-lg shadow-md p-8 cursor-pointer hover:shadow-xl transition-shadow border-2 border-transparent hover:border-green-500"
        >
          <div className="flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>
          <h3 className="text-2xl font-semibold text-slate-800 mb-2">
            View Test History
          </h3>
          <p className="text-slate-600">
            Browse previous tests and analyze their results
          </p>
        </div>
      </div>

      <div className="mt-12 bg-blue-50 rounded-lg p-6 border border-blue-200">
        <h4 className="text-lg font-semibold text-slate-800 mb-3">
          Classification Modes
        </h4>
        <div className="space-y-2 text-slate-700">
          <div className="flex items-start">
            <span className="font-medium min-w-24">SR Mode:</span>
            <span>Service Request classification only</span>
          </div>
          <div className="flex items-start">
            <span className="font-medium min-w-24">QF Mode:</span>
            <span>Category/Question Form classification only</span>
          </div>
          <div className="flex items-start">
            <span className="font-medium min-w-24">Both Mode:</span>
            <span>Complete classification with SR and category detection</span>
          </div>
        </div>
      </div>
    </div>
  );
}
