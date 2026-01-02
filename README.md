# LLM Classifier Testing Framework

A modern, comprehensive Streamlit-based testing framework for evaluating LLM-based email classification systems. This application allows you to run batch classification tests, track results, and analyze performance metrics with an intuitive UI.

## Features

- **🎨 Modern UI**: Clean, professional interface built with Streamlit
- **📊 Rich Visualizations**: Interactive charts and graphs using Plotly
- **⚙️ Flexible Testing**: Configure classification modes (SR, QF, or both)
- **🔧 Advanced Options**: Control filters, async processing, and concurrency
- **📈 Detailed Analytics**: View comprehensive breakdowns of classification outcomes
- **📚 Test History**: Browse and manage all past test results
- **💾 Persistent Storage**: JSON-based storage for test history

## Project Structure

```
classifier-app/
├── Home.py                  # Main landing page
├── pages/
│   ├── 1_📝_New_Test.py    # Test creation form
│   ├── 2_📚_Test_History.py # Test history browser
│   └── 3_📊_Test_Results.py # Results viewer with charts
├── utils/
│   ├── classifier.py        # Classifier integration (TODO: add your code)
│   ├── config.py           # Configuration loader
│   ├── models.py           # Data models
│   └── storage.py          # Test result storage
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── data/                   # Test history storage (auto-created)
├── config.json             # Global app configuration
└── requirements.txt        # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Integrate Your Classifier

Open `utils/classifier.py` and replace the `run_classifier` function with your actual implementation:

```python
def run_classifier(
    source_path: str,
    out_path: str,
    mode: Literal['sr', 'qf', 'both'] = 'both',
    use_filter: bool = True,
    async_mode: bool = True,
    max_concurrency: int = 20
) -> dict:
    # Your implementation here
    # ...

    return {
        'total_emails': 100,
        'processed_emails': 100,
        'sr_positive': 35,  # if mode is 'sr' or 'both'
        'sr_negative': 65,  # if mode is 'sr' or 'both'
        'category_breakdown': {  # if mode is 'qf' or 'both'
            'Category 1': 25,
            'Category 2': 30,
            # ...
        }
    }
```

### 3. Run the Application

```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`

## Configuration

Edit `config.json` to customize:

```json
{
  "app": {
    "name": "LLM Classifier Testing Framework",
    "version": "1.0.0"
  },
  "classifier": {
    "default_mode": "both",
    "default_use_filter": true,
    "default_async_mode": true,
    "default_max_concurrency": 20,
    "max_concurrency_limit": 50,
    "allowed_file_types": [".csv", ".xlsx"],
    "output_directory": "./results"
  },
  "storage": {
    "test_history_file": "./data/test_history.json",
    "max_history_items": 100
  }
}
```

## Usage

### Running a New Test

1. Navigate to **📝 New Test** page
2. Enter the source path (file or folder containing emails)
3. Enter the output path for results
4. Select classification mode:
   - **Both**: SR + Category classification
   - **SR Only**: Service Request detection
   - **QF Only**: Category classification
5. Configure advanced options:
   - **Use Aggressive Filters**: Apply data preprocessing
   - **Async Mode**: Enable parallel processing
   - **Max Concurrency**: Set number of parallel predictions (1-50)
6. Click **🚀 Start Test**

### Viewing Results

1. Navigate to **📚 Test History**
2. Browse all past tests with filtering options
3. Click **👁️ View** on any test to see detailed results
4. View interactive charts and metrics:
   - Email processing statistics
   - SR positive/negative distribution (pie chart)
   - Category breakdown (bar chart)
   - Detailed percentages and counts

### Managing Tests

- **Filter tests**: By status (pending, running, completed, failed) or mode
- **Delete tests**: Remove old or unwanted test records
- **Auto-refresh**: History page auto-updates for running tests
- **Quick stats**: View total, completed, running, and failed tests

## Classification Modes

- **sr**: Service Request classifier only
- **qf**: Category/Question Form classifier only
- **both**: Run both SR and category classification (recommended)

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_path` | string | Path to input file (.csv, .xlsx) or folder |
| `out_path` | string | Path where results will be saved |
| `mode` | string | Classification mode (sr/qf/both) |
| `use_filter` | boolean | Apply aggressive data filtering |
| `async_mode` | boolean | Enable parallel processing |
| `max_concurrency` | integer | Number of parallel requests (1-50) |

## Data Storage

- Test history is stored in `./data/test_history.json` (configurable)
- Maximum 100 tests kept in history by default (configurable)
- Results persist across app restarts
- Clean JSON format for easy inspection

## Theme Customization

Edit `.streamlit/config.toml` to customize colors and appearance:

```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor = "#1e293b"
```

## Integrating Your Classifier

The framework expects your `run_classifier` function to:

1. **Accept these parameters**:
   - `source_path`: Path to data
   - `out_path`: Where to save results
   - `mode`: 'sr', 'qf', or 'both'
   - `use_filter`: boolean
   - `async_mode`: boolean
   - `max_concurrency`: integer

2. **Return a dictionary** with:
   - `total_emails`: Total number of emails processed
   - `processed_emails`: Successfully processed emails
   - `sr_positive`: Count of SR positive (if mode includes SR)
   - `sr_negative`: Count of SR negative (if mode includes SR)
   - `category_breakdown`: Dict of category counts (if mode includes QF)

Example integration in `utils/classifier.py`:

```python
from your_module import your_classifier_function

def run_classifier(source_path, out_path, mode='both', use_filter=True,
                   async_mode=True, max_concurrency=20):
    # Call your actual classifier
    results = your_classifier_function(
        source_path=source_path,
        out_path=out_path,
        mode=mode,
        use_filter=use_filter,
        async_mode=async_mode,
        max_concurrency=max_concurrency
    )

    # Return in expected format
    return {
        'total_emails': results['total'],
        'processed_emails': results['processed'],
        'sr_positive': results['sr_pos'],
        'sr_negative': results['sr_neg'],
        'category_breakdown': results['categories']
    }
```

## Troubleshooting

**App won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

**Tests not appearing:**
- Check `data/test_history.json` exists and is valid JSON
- Ensure write permissions in the data directory

**Visualizations not showing:**
- Verify Plotly is installed: `pip install plotly`
- Check browser console for JavaScript errors

## Development

Built with:
- **Streamlit** 1.40.0 - Web framework
- **Pandas** 2.2.0 - Data manipulation
- **Plotly** 5.24.0 - Interactive visualizations
- **Python** 3.8+

## License

MIT License - Feel free to modify and use for your needs.

## Support

For issues or questions, please check the documentation or create an issue in the project repository.
