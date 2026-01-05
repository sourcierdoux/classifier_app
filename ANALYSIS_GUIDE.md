# Analysis Module Guide

## Overview

The analysis module provides comprehensive, file-by-file analysis of email classification predictions. It automatically runs after your `run_classifier` completes and calculates detailed KPIs from the prediction results.

## How It Works

### Workflow

1. **Run Test**: User configures and runs a classification test
2. **Classification**: Your `run_classifier` method processes emails and saves results to `out_path`
3. **Automatic Analysis**: The analyzer reads each `*_result.csv/xlsx` file
4. **Calculate KPIs**: Per-file analysis with precision, accuracy, confusion matrices
5. **Store Results**: Analysis saved with test for viewing in the UI
6. **Display**: Rich visualizations and metrics in the Test Results page

### File-by-File Processing

Each input file is analyzed independently, so you get:
- **Desk-level insights**: Since each file represents a desk
- **Individual metrics**: Separate KPIs for each file
- **Aggregated view**: Overall statistics across all files

## Analysis Components

### 1. Basic File Statistics

For each file, we calculate:
- **Total Emails**: Count of all emails in the file
- **GT SR Creations**: Emails with `sr_id != 0` and not NaN (ground truth)
- **GT Archives**: Emails with `sr_id == 0` or NaN (ground truth)

### 2. SR Opening Analysis

**Prediction Counts**:
- Predicted SR Creation (`predicted_opening == "SR"`)
- Predicted Archive (`predicted_opening == "Archive"`)
- Predicted Review (`predicted_opening == "Review"`)

**Precision Metrics**:
- **SR Creation Precision**: Of all predicted as SR, how many are actually SR?
  - `correct_sr / total_predicted_sr`
- **Archive Precision**: Of all predicted as Archive, how many are actually Archive?
  - `correct_archive / total_predicted_archive`
- **Overall Accuracy**: Accuracy excluding Review predictions (no ground truth for Review)
  - `correct_predictions / total_non_review_predictions`

**Visualizations**:
- Pie chart showing distribution of SR/Archive/Review predictions

### 3. Quickfill Analysis

**Distribution**:
- Value counts of all predicted quickfills
- Special focus on configured quickfills (e.g., "AFFIRMATION / TRADE RECOGNITION")

**Accuracy**:
- Calculated only for ground truth SR creation cases
- Compares `predicted_quickfill` vs `sr_quick_fulfillment`
- Excludes NaN values

**Confusion Matrix**:
- Ground truth quickfills (rows) vs Predicted quickfills (columns)
- Only for emails where ground truth SR creation exists
- Heatmap visualization + table view
- Shows which categories are confused with each other

**Visualizations**:
- Bar chart of quickfill distribution
- Confusion matrix heatmap
- Confusion matrix table

## Configuration

### config.json

```json
{
  "analysis": {
    "sr_id_column": "sr_id",
    "ground_truth_quickfill_column": "sr_quick_fulfillment",
    "predicted_opening_column": "predicted_opening",
    "predicted_quickfill_column": "predicted_quickfill",
    "sr_labels": {
      "creation": "SR",
      "archive": "Archive",
      "review": "Review"
    },
    "special_quickfills": ["AFFIRMATION / TRADE RECOGNITION"]
  }
}
```

**Configurable Fields**:
- Column names (customize for your data schema)
- SR label names (what values indicate SR/Archive/Review)
- Special quickfills to highlight

## Expected Data Format

### Input Files
Your `run_classifier` should process files and save results with these columns:

**Required Columns**:
- `sr_id`: Ground truth SR ID (0 or NaN = Archive, other = SR Creation)
- `predicted_opening`: Your prediction ("SR", "Archive", or "Review")
- `predicted_quickfill`: Predicted quickfill category (only when `predicted_opening == "SR"`)
- `sr_quick_fulfillment`: Ground truth quickfill (present for SR creation cases)

**Example**:
```csv
email_id,sr_id,sr_quick_fulfillment,predicted_opening,predicted_quickfill
1,12345,BILLING INQUIRY,SR,BILLING INQUIRY
2,0,,Archive,
3,67890,AFFIRMATION / TRADE RECOGNITION,SR,AFFIRMATION / TRADE RECOGNITION
4,,,,Review,
```

### Output Files Naming
The analyzer looks for files ending with `_result.csv` or `_result.xlsx` in the `out_path`.

Example:
- Input: `desk_A.csv` → Output: `desk_A_result.csv`
- Input: `desk_B.xlsx` → Output: `desk_B_result.xlsx`

## Integrating with Your Classifier

### What You Need to Return

Your `run_classifier` function can return basic stats (optional):

```python
def run_classifier(source_path, out_path, mode, use_filter, async_mode, max_concurrency):
    # Your classification logic here
    # Save results to out_path with _result suffix

    # Optional: return basic stats for UI
    return {
        'total_emails': 500,
        'processed_emails': 500,
        'sr_positive': 150,  # if mode includes 'sr'
        'sr_negative': 350,  # if mode includes 'sr'
        # No need to return detailed analysis - analyzer handles it
    }
```

### What the Analyzer Does

The analyzer automatically:
1. Finds all `*_result.csv/xlsx` files in `out_path`
2. Reads each file with pandas
3. Calculates all KPIs per file
4. Returns structured analysis data
5. Stores in test history

**You don't need to**:
- Calculate precision/accuracy
- Create confusion matrices
- Aggregate statistics
- Format data for UI

The analyzer handles all of this!

## UI Display

### Test Results Page

When viewing test results, you'll see:

**Per-File Tabs**:
- Each file gets its own tab
- Complete analysis for that desk

**Basic Statistics**:
- Total emails, GT SR creations, GT archives

**SR Opening Analysis** (if mode includes 'sr'):
- Prediction counts (SR/Archive/Review)
- Precision metrics with percentages
- SR distribution pie chart

**Quickfill Analysis** (if mode includes 'qf' or 'both'):
- Total quickfills predicted
- Quickfill accuracy
- Special quickfill counts
- Distribution bar chart
- Confusion matrix heatmap
- Confusion matrix table

## Customization

### Adding Custom Special Quickfills

Edit `config.json`:

```json
{
  "analysis": {
    "special_quickfills": [
      "AFFIRMATION / TRADE RECOGNITION",
      "YOUR_CUSTOM_CATEGORY",
      "ANOTHER_CATEGORY"
    ]
  }
}
```

These will be highlighted with dedicated metrics in the UI.

### Changing Column Names

If your data uses different column names:

```json
{
  "analysis": {
    "sr_id_column": "service_request_id",
    "ground_truth_quickfill_column": "actual_category",
    "predicted_opening_column": "prediction_sr",
    "predicted_quickfill_column": "prediction_category"
  }
}
```

### Changing SR Labels

If you use different labels for predictions:

```json
{
  "analysis": {
    "sr_labels": {
      "creation": "OPEN_SR",
      "archive": "NO_SR",
      "review": "UNCERTAIN"
    }
  }
}
```

## Error Handling

### Failed Analyses

If analysis fails for a file:
- Error is captured and stored
- Other files continue processing
- Failed files shown in expandable section
- Test still marked as completed

### Missing Columns

If required columns are missing:
- Analysis fails for that file
- Error message indicates which column is missing
- Check your `run_classifier` output format

### Empty Files

If a result file is empty:
- Analysis returns 0 counts
- No errors raised
- Visualizations handle empty data gracefully

## Performance

The analysis is **fast**:
- Runs in parallel with test completion
- Uses pandas for efficient processing
- Typical file (1000 emails): < 1 second
- Multiple files: processed sequentially

## Troubleshooting

### Analysis Not Showing

**Check**:
1. Test status is "completed"
2. Result files exist in `out_path`
3. Files end with `_result.csv` or `_result.xlsx`
4. Required columns present in files

### Incorrect Metrics

**Check**:
1. Column names match config.json
2. SR label names match your predictions
3. Ground truth data is correct format
4. No typos in prediction values

### Confusion Matrix Empty

**Possible reasons**:
1. No ground truth SR creations in file
2. `sr_quick_fulfillment` column all NaN
3. Mode doesn't include 'qf' or 'both'
4. Predicted quickfills don't match SR predictions

## Best Practices

1. **Consistent Naming**: Use `_result` suffix for all output files
2. **Complete Data**: Include all required columns
3. **Validate Predictions**: Ensure prediction values match configured labels
4. **Handle Edge Cases**: Account for NaN values in ground truth
5. **Test Small First**: Run on small dataset to verify integration

## Example: Complete Integration

```python
# In utils/classifier.py

def run_classifier(source_path, out_path, mode='both', use_filter=True,
                   async_mode=True, max_concurrency=20):
    from pathlib import Path
    import pandas as pd

    # Process each file
    source = Path(source_path)
    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if source.is_file():
        files = [source]
    else:
        files = list(source.glob("*.csv")) + list(source.glob("*.xlsx"))

    total_emails = 0
    total_sr = 0

    for file in files:
        # Load data
        if file.suffix == '.csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Your classification logic
        df['predicted_opening'] = your_sr_classifier(df)
        df['predicted_quickfill'] = your_qf_classifier(df[df['predicted_opening'] == 'SR'])

        # Save with _result suffix
        output_file = out_dir / f"{file.stem}_result{file.suffix}"
        if file.suffix == '.csv':
            df.to_csv(output_file, index=False)
        else:
            df.to_excel(output_file, index=False)

        # Track stats
        total_emails += len(df)
        total_sr += (df['predicted_opening'] == 'SR').sum()

    # Return basic stats (detailed analysis happens automatically)
    return {
        'total_emails': total_emails,
        'processed_emails': total_emails,
        'sr_positive': total_sr,
        'sr_negative': total_emails - total_sr,
    }
```

The analyzer will automatically read your `*_result.csv/xlsx` files and generate comprehensive analysis!
