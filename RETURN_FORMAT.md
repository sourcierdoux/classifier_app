# Return Format for `run_classifier`

## What You MUST Return

Your `run_classifier` function **must** return a dictionary with this exact structure:

```python
{
    'total_emails': int,           # Total ORIGINAL emails (before filtering)
    'processed_emails': int,       # Total FILTERED emails (after filtering)
    'sr_positive': int,           # Optional: total SR predictions
    'sr_negative': int,           # Optional: total Archive predictions
    'file_stats': [               # REQUIRED: per-file original stats
        {
            'source_file': str,           # e.g., 'desk_A.csv'
            'original_total': int,        # Before filtering
            'original_sr_count': int,     # SR creations before filtering
            'original_archive_count': int,# Archives before filtering
            'filtered_total': int,        # After filtering
        },
        # ... one dict per file processed
    ]
}
```

## Why `file_stats` is Required

Since your classifier applies **aggressive filtering** (removing duplicate sr_id, specific senders, etc.), we need **both**:

1. **Original file statistics** (before filtering) - from `file_stats`
2. **Filtered file statistics** (after filtering) - calculated by analyzer from result files

The UI will show:
- **Original File**: 1000 emails, 200 SRs, 800 Archives
- **After Filtering**: 400 emails (-600 removed), 150 SRs, 250 Archives
- **Predictions**: Based on the 400 filtered emails

## Progress Tracking (Optional but Recommended)

To show real-time progress in the UI, use the `progress_callback` parameter:

```python
def run_classifier(..., progress_callback=None):
    files = get_files(source_path)
    total_files = len(files)

    for idx, file in enumerate(files):
        # Report progress to UI
        if progress_callback:
            progress_callback(
                current=idx + 1,
                total=total_files,
                message=f"Processing {file.name}..."
            )

        # Your processing logic...
```

The callback receives:
- `current`: Current file number (1-based)
- `total`: Total number of files
- `message`: Status message to display

## Step-by-Step Implementation

### Step 1: Load Original File

```python
for idx, file in enumerate(files):
    # Report progress (optional)
    if progress_callback:
        progress_callback(idx + 1, len(files), f"Processing {file.name}...")

    # Load original (before any filtering)
    if file.suffix == '.csv':
        df_original = pd.read_csv(file)
    else:
        df_original = pd.read_excel(file)
```

### Step 2: Calculate Pre-Filter Stats

```python
    # Calculate BEFORE filtering
    original_total = len(df_original)
    original_sr = (df_original['sr_id'].notna() & (df_original['sr_id'] != 0)).sum()
    original_archive = original_total - original_sr
```

### Step 3: Apply Your Filters

```python
    # Apply YOUR filtering logic
    if use_filter:
        df_filtered = apply_your_filters(df_original)
        # Example:
        # df_filtered = df_original[
        #     ~df_original['sender_email'].isin(blocked_senders)
        # ].drop_duplicates(subset=['sr_id'], keep='first')
    else:
        df_filtered = df_original
```

### Step 4: Run Classifier on Filtered Data

```python
    # Run predictions on FILTERED data
    df_filtered['predicted_opening'] = your_sr_classifier(df_filtered)

    if mode in ['qf', 'both']:
        sr_mask = df_filtered['predicted_opening'] == 'SR'
        df_filtered.loc[sr_mask, 'predicted_quickfill'] = your_qf_classifier(df_filtered[sr_mask])
```

### Step 5: Save Result File

```python
    # Save with _result suffix
    output_file = out_dir / f"{file.stem}_result{file.suffix}"

    if file.suffix == '.csv':
        df_filtered.to_csv(output_file, index=False)
    else:
        df_filtered.to_excel(output_file, index=False)
```

### Step 6: Track Stats

```python
    filtered_total = len(df_filtered)

    file_stats.append({
        'source_file': file.name,                    # 'desk_A.csv'
        'original_total': int(original_total),       # 1000
        'original_sr_count': int(original_sr),       # 200
        'original_archive_count': int(original_archive), # 800
        'filtered_total': int(filtered_total),       # 400
    })

    total_original += original_total
    total_filtered += filtered_total
```

### Step 7: Return Everything

```python
return {
    'total_emails': int(total_original),      # Sum of original_total
    'processed_emails': int(total_filtered),  # Sum of filtered_total
    'sr_positive': int(total_sr),             # Optional
    'sr_negative': int(total_archive),        # Optional
    'file_stats': file_stats,                 # List of dicts
}
```

## Complete Example

```python
def run_classifier(source_path, out_path, mode='both', use_filter=True,
                   async_mode=True, max_concurrency=20):
    from pathlib import Path
    import pandas as pd

    source = Path(source_path)
    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Get files
    if source.is_file():
        files = [source]
    else:
        files = list(source.glob("*.csv")) + list(source.glob("*.xlsx"))

    file_stats = []
    total_original = 0
    total_filtered = 0
    total_sr = 0
    total_archive = 0

    for file in files:
        # 1. Load original
        df_original = pd.read_csv(file) if file.suffix == '.csv' else pd.read_excel(file)

        # 2. Pre-filter stats
        original_total = len(df_original)
        original_sr = (df_original['sr_id'].notna() & (df_original['sr_id'] != 0)).sum()
        original_archive = original_total - original_sr

        # 3. Filter
        if use_filter:
            df_filtered = your_filtering_logic(df_original)
        else:
            df_filtered = df_original

        # 4. Classify
        df_filtered['predicted_opening'] = your_sr_classifier(df_filtered, mode, async_mode, max_concurrency)

        if mode in ['qf', 'both']:
            sr_mask = df_filtered['predicted_opening'] == 'SR'
            df_filtered.loc[sr_mask, 'predicted_quickfill'] = your_qf_classifier(
                df_filtered[sr_mask], async_mode, max_concurrency
            )

        # 5. Save
        output_file = out_dir / f"{file.stem}_result{file.suffix}"
        df_filtered.to_csv(output_file, index=False) if file.suffix == '.csv' else df_filtered.to_excel(output_file, index=False)

        # 6. Track
        filtered_total = len(df_filtered)
        file_stats.append({
            'source_file': file.name,
            'original_total': int(original_total),
            'original_sr_count': int(original_sr),
            'original_archive_count': int(original_archive),
            'filtered_total': int(filtered_total),
        })

        total_original += original_total
        total_filtered += filtered_total
        total_sr += (df_filtered['predicted_opening'] == 'SR').sum()
        total_archive += (df_filtered['predicted_opening'] == 'Archive').sum()

    # 7. Return
    return {
        'total_emails': int(total_original),
        'processed_emails': int(total_filtered),
        'sr_positive': int(total_sr),
        'sr_negative': int(total_archive),
        'file_stats': file_stats,  # CRITICAL!
    }
```

## What Happens Next

1. Your function returns this dict
2. Framework extracts `file_stats`
3. Analyzer reads `*_result.csv/xlsx` files
4. Analyzer merges:
   - Original stats from `file_stats`
   - Prediction stats from result files
5. UI displays both:
   - "Original File (Before Filtering)"
   - "After Filtering" with delta showing removed count

## Example UI Display

```
📄 Original File (Before Filtering)
Total Emails: 1000
SR Creations (GT): 200
Archives (GT): 800

🔍 After Filtering
Filtered Emails: 400 (-600 removed)
GT SR Creations: 150
GT Archives: 250

✅ SR Opening Analysis
[Based on 400 filtered emails]
Predicted SR: 140
Predicted Archive: 255
Predicted Review: 5
```

## Important Notes

1. **File naming**: Result files must be `{original_name}_result.{ext}`
   - `desk_A.csv` → `desk_A_result.csv`
   - `desk_B.xlsx` → `desk_B_result.xlsx`

2. **source_file in file_stats**: Must match original filename exactly
   - Use `file.name` not `file.stem`

3. **All counts as int**: Convert pandas Series to int with `.sum()` or `int()`

4. **file_stats is a list**: One dict per file processed

5. **Order doesn't matter**: Analyzer matches by filename

## Checklist

- [ ] Calculate original_total before filtering
- [ ] Calculate original_sr_count before filtering
- [ ] Calculate original_archive_count before filtering
- [ ] Apply filters to create df_filtered
- [ ] Calculate filtered_total after filtering
- [ ] Save df_filtered as `{name}_result.{ext}`
- [ ] Include all required columns in result file
- [ ] Add each file's stats to file_stats list
- [ ] Return file_stats in the return dict
- [ ] Ensure source_file matches actual filename

## Troubleshooting

**"Original stats not showing in UI"**
- Check `file_stats` is in return dict
- Verify `source_file` matches result filename (minus `_result`)

**"Wrong email counts"**
- Ensure original stats calculated BEFORE filtering
- Ensure filtered stats calculated AFTER filtering

**"Can't match files"**
- Check result file naming: `{original}_result.{ext}`
- Verify `source_file` in file_stats matches original name
