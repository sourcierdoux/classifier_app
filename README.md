# LLM Classifier Testing Framework

A comprehensive web-based testing framework for evaluating LLM-based email classification systems. This application allows you to run batch classification tests, track results, and analyze performance metrics.

## Features

- **Intuitive UI**: Clean, modern interface built with React and Tailwind CSS
- **Flexible Testing**: Configure classification modes (SR, QF, or both)
- **Advanced Options**: Control filters, async processing, and concurrency
- **Real-time Updates**: Live status updates for running tests
- **Test History**: Browse and analyze past test results
- **Detailed Results**: View comprehensive breakdowns of classification outcomes

## Project Structure

```
classifier-app/
├── backend/               # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── models.py         # Pydantic models
│   ├── config.py         # Configuration loader
│   ├── storage.py        # Test result storage
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── types/       # TypeScript types
│   └── package.json
└── config.json          # Global app configuration
```

## Setup

### Backend Setup

1. Create a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Important**: Add your existing `run_classifier` function to the backend:
   - Open `backend/main.py`
   - Import your classifier function
   - Replace the TODO section in `run_classifier_background` with your actual implementation

4. Run the backend:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file if you need to customize the API URL:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Configuration

Edit `config.json` in the root directory to customize:

- **Backend settings**: Host, port, CORS origins
- **Classifier defaults**: Mode, filters, concurrency
- **Storage settings**: History file location, max items
- **File types**: Allowed input formats

## Usage

### Running a New Test

1. Click "Launch New Test" from the home page
2. Enter the source path (file or folder containing emails)
3. Enter the output path for results
4. Select classification mode:
   - **Both**: SR + Category classification
   - **SR Only**: Service Request detection
   - **QF Only**: Category classification
5. Configure advanced options:
   - Use Aggressive Filters
   - Async Mode (parallel processing)
   - Max Concurrency (1-50)
6. Click "Start Test"

### Viewing Results

- Navigate to "History" to see all past tests
- Click "View" on any test to see detailed results
- Results update automatically for running tests
- View metrics like:
  - Total emails processed
  - SR positive/negative counts
  - Category breakdowns
  - Processing duration

### Test History

- Browse all previous tests
- Filter by status (pending, running, completed, failed)
- Delete old tests to clean up history
- Auto-refreshes every 5 seconds

## API Endpoints

- `POST /api/tests/run` - Start a new classification test
- `GET /api/tests` - Get all test history
- `GET /api/tests/{test_id}` - Get specific test details
- `DELETE /api/tests/{test_id}` - Delete a test
- `GET /api/config` - Get application configuration
- `GET /health` - Health check endpoint

## Classification Modes

- **sr**: Service Request classifier only
- **qf**: Category/Question Form classifier only
- **both**: Run both SR and category classification

## Parameters

- **source_path**: Path to input file (.csv, .xlsx) or folder
- **out_path**: Path where results will be saved
- **mode**: Classification mode (sr/qf/both)
- **use_filter**: Apply aggressive data filtering (boolean)
- **async_mode**: Enable parallel processing (boolean)
- **max_concurrency**: Number of parallel requests (1-50)

## Development

### Frontend

Built with:
- React 19
- TypeScript
- Tailwind CSS
- Vite

### Backend

Built with:
- FastAPI
- Pydantic
- Python 3.8+

## Notes

- The backend stores test history in a JSON file (configurable in `config.json`)
- Test results are persisted across server restarts
- The UI automatically polls for updates on running tests
- Maximum 100 tests are kept in history by default (configurable)

## Integration with Your Classifier

To integrate your existing `run_classifier` function:

1. Open `backend/main.py`
2. Find the `run_classifier_background` function
3. Replace the TODO section with:

```python
from your_module import run_classifier

results = run_classifier(
    source_path=request.source_path,
    out_path=request.out_path,
    mode=request.mode.value,
    use_filter=request.use_filter,
    async_mode=request.async_mode,
    max_concurrency=request.max_concurrency
)

# Update test with actual results
test.total_emails = results.get('total_emails', 0)
test.processed_emails = results.get('processed_emails', 0)
test.sr_positive = results.get('sr_positive', 0)
test.sr_negative = results.get('sr_negative', 0)
test.category_breakdown = results.get('category_breakdown', {})
```

Make sure your `run_classifier` function returns a dictionary with these keys.
