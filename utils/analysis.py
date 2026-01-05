"""
Analysis module for calculating KPIs from prediction results
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .config import config


class ResultsAnalyzer:
    """Analyzes prediction results file by file"""

    def __init__(self):
        self.sr_id_col = config.analysis["sr_id_column"]
        self.gt_qf_col = config.analysis["ground_truth_quickfill_column"]
        self.pred_opening_col = config.analysis["predicted_opening_column"]
        self.pred_qf_col = config.analysis["predicted_quickfill_column"]
        self.sr_creation_label = config.analysis["sr_labels"]["creation"]
        self.archive_label = config.analysis["sr_labels"]["archive"]
        self.review_label = config.analysis["sr_labels"]["review"]
        self.special_qfs = config.analysis["special_quickfills"]

    def analyze_test_results(self, out_path: str, file_stats: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Analyze all result files in the output path.
        Merges with pre-filter stats if provided.

        Args:
            out_path: Path to result files
            file_stats: Optional list of pre-filter stats from run_classifier
                Each dict should have: {
                    'source_file': 'filename.csv',
                    'original_total': 1000,
                    'original_sr_count': 200,
                    'original_archive_count': 800,
                    'filtered_total': 400
                }

        Returns:
            List of per-file analyses with both original and filtered stats
        """
        out_dir = Path(out_path)

        if not out_dir.exists():
            raise ValueError(f"Output path does not exist: {out_path}")

        # Find all result files (files with _result in name)
        result_files = []
        if out_dir.is_file():
            result_files = [out_dir]
        else:
            result_files = list(out_dir.glob("*_result.csv")) + list(out_dir.glob("*_result.xlsx"))

        if not result_files:
            raise ValueError(f"No result files found in {out_path}")

        # Create lookup for pre-filter stats by source filename
        prefilter_lookup = {}
        if file_stats:
            for stat in file_stats:
                source_name = stat.get('source_file', '')
                # Map source file to result file (e.g., desk_A.csv -> desk_A_result.csv)
                prefilter_lookup[source_name] = stat

        # Analyze each file
        analyses = []
        for file_path in result_files:
            try:
                analysis = self.analyze_single_file(file_path)

                # Try to match with pre-filter stats
                # Result file: desk_A_result.csv -> source: desk_A.csv
                result_name = file_path.name
                source_name = result_name.replace('_result', '')

                if source_name in prefilter_lookup:
                    # Merge pre-filter stats
                    prefilter = prefilter_lookup[source_name]
                    analysis['original_stats'] = {
                        'total_emails': prefilter.get('original_total'),
                        'sr_count': prefilter.get('original_sr_count'),
                        'archive_count': prefilter.get('original_archive_count'),
                    }
                    analysis['filtered_total'] = prefilter.get('filtered_total')

                analyses.append(analysis)
            except Exception as e:
                # Include failed analysis with error message
                analyses.append({
                    'file_name': file_path.name,
                    'error': str(e),
                    'status': 'failed'
                })

        return analyses

    def analyze_single_file(self, file_path: Path) -> Dict:
        """Analyze a single result file (after filtering)"""
        # Load data
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        # Basic file stats (AFTER FILTERING)
        total_emails = len(df)

        # Determine ground truth SR creation/archive (from filtered data)
        gt_sr_creation = df[self.sr_id_col].notna() & (df[self.sr_id_col] != 0)
        gt_sr_archive = ~gt_sr_creation

        # Count ground truth (in filtered data)
        gt_sr_creation_count = gt_sr_creation.sum()
        gt_sr_archive_count = gt_sr_archive.sum()

        # SR Analysis
        sr_analysis = self._analyze_sr_predictions(df, gt_sr_creation, gt_sr_archive)

        # Quickfill Analysis
        qf_analysis = self._analyze_quickfill_predictions(df, gt_sr_creation)

        return {
            'file_name': file_path.name,
            'status': 'success',
            'basic_stats': {
                'total_emails': int(total_emails),
                'gt_sr_creation_count': int(gt_sr_creation_count),
                'gt_sr_archive_count': int(gt_sr_archive_count),
            },
            'sr_analysis': sr_analysis,
            'quickfill_analysis': qf_analysis,
        }

    def _analyze_sr_predictions(self, df: pd.DataFrame, gt_sr_creation: pd.Series, gt_sr_archive: pd.Series) -> Dict:
        """Analyze SR opening predictions"""
        pred_opening = df[self.pred_opening_col]

        # Count predictions
        pred_sr_count = (pred_opening == self.sr_creation_label).sum()
        pred_archive_count = (pred_opening == self.archive_label).sum()
        pred_review_count = (pred_opening == self.review_label).sum()

        # Calculate precision for SR Creation and Archive
        # SR Creation Precision: Of all predicted as SR, how many are actually SR?
        sr_precision = None
        if pred_sr_count > 0:
            predicted_as_sr = pred_opening == self.sr_creation_label
            correct_sr = (predicted_as_sr & gt_sr_creation).sum()
            sr_precision = float(correct_sr / pred_sr_count)

        # Archive Precision: Of all predicted as Archive, how many are actually Archive?
        archive_precision = None
        if pred_archive_count > 0:
            predicted_as_archive = pred_opening == self.archive_label
            correct_archive = (predicted_as_archive & gt_sr_archive).sum()
            archive_precision = float(correct_archive / pred_archive_count)

        # Overall accuracy (excluding Review since no ground truth for it)
        non_review_mask = pred_opening != self.review_label
        if non_review_mask.sum() > 0:
            # Create ground truth labels
            gt_labels = np.where(gt_sr_creation, self.sr_creation_label, self.archive_label)
            pred_labels = pred_opening[non_review_mask]
            gt_labels_filtered = gt_labels[non_review_mask]
            accuracy = float((pred_labels == gt_labels_filtered).sum() / len(pred_labels))
        else:
            accuracy = None

        return {
            'predicted_sr_count': int(pred_sr_count),
            'predicted_archive_count': int(pred_archive_count),
            'predicted_review_count': int(pred_review_count),
            'sr_creation_precision': round(sr_precision, 4) if sr_precision is not None else None,
            'archive_precision': round(archive_precision, 4) if archive_precision is not None else None,
            'overall_accuracy': round(accuracy, 4) if accuracy is not None else None,
        }

    def _analyze_quickfill_predictions(self, df: pd.DataFrame, gt_sr_creation: pd.Series) -> Dict:
        """Analyze quickfill predictions"""
        # Only analyze rows where SR creation is predicted
        pred_opening = df[self.pred_opening_col]
        sr_predicted_mask = pred_opening == self.sr_creation_label

        if sr_predicted_mask.sum() == 0:
            return {
                'total_quickfills_predicted': 0,
                'distribution': {},
                'special_quickfill_counts': {},
                'confusion_matrix': None,
                'accuracy': None,
            }

        # Get predicted quickfills (only for SR predictions)
        pred_qf = df.loc[sr_predicted_mask, self.pred_qf_col]

        # Distribution of predicted quickfills
        distribution = pred_qf.value_counts().to_dict()

        # Special quickfill counts
        special_qf_counts = {}
        for qf in self.special_qfs:
            special_qf_counts[qf] = int((pred_qf == qf).sum())

        # Confusion matrix and accuracy (only for ground truth SR creation cases)
        confusion_matrix = None
        accuracy = None

        # Filter to only ground truth SR creation cases (where we have ground truth quickfills)
        gt_sr_mask = gt_sr_creation & sr_predicted_mask

        if gt_sr_mask.sum() > 0:
            gt_qf = df.loc[gt_sr_mask, self.gt_qf_col]
            pred_qf_filtered = df.loc[gt_sr_mask, self.pred_qf_col]

            # Remove NaN values
            valid_mask = gt_qf.notna() & pred_qf_filtered.notna()
            if valid_mask.sum() > 0:
                gt_qf_clean = gt_qf[valid_mask]
                pred_qf_clean = pred_qf_filtered[valid_mask]

                # Create confusion matrix
                confusion_matrix = self._create_confusion_matrix(gt_qf_clean, pred_qf_clean)

                # Calculate accuracy
                accuracy = float((gt_qf_clean == pred_qf_clean).sum() / len(gt_qf_clean))

        return {
            'total_quickfills_predicted': int(pred_qf.notna().sum()),
            'distribution': {str(k): int(v) for k, v in distribution.items()},
            'special_quickfill_counts': special_qf_counts,
            'confusion_matrix': confusion_matrix,
            'accuracy': round(accuracy, 4) if accuracy is not None else None,
        }

    def _create_confusion_matrix(self, y_true: pd.Series, y_pred: pd.Series) -> Dict:
        """Create a confusion matrix as a dictionary"""
        # Get all unique labels
        all_labels = sorted(set(y_true.unique()) | set(y_pred.unique()))

        # Create confusion matrix
        matrix = {}
        for true_label in all_labels:
            matrix[str(true_label)] = {}
            for pred_label in all_labels:
                count = ((y_true == true_label) & (y_pred == pred_label)).sum()
                matrix[str(true_label)][str(pred_label)] = int(count)

        return {
            'labels': [str(l) for l in all_labels],
            'matrix': matrix
        }


# Global analyzer instance
analyzer = ResultsAnalyzer()
