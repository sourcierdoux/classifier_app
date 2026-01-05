import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils.storage import storage

st.set_page_config(page_title="Test Results", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .status-completed { background-color: #d1fae5; color: #065f46; }
    .status-running { background-color: #dbeafe; color: #1e40af; }
    .status-failed { background-color: #fee2e2; color: #991b1b; }
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .file-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #3b82f6;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Get test ID from session state
test_id = st.session_state.get('selected_test_id')

if not test_id:
    st.warning("⚠️ No test selected. Please select a test from the history page.")
    if st.button("📚 Go to Test History"):
        st.switch_page("pages/2_📚_Test_History.py")
    st.stop()

# Load test
test = storage.get_test(test_id)

if not test:
    st.error("❌ Test not found")
    st.stop()

# Header
st.title("📊 Test Results")

status_class = f"status-{test.status}"
st.markdown(f'<span class="status-badge {status_class}">{test.status.upper()}</span>', unsafe_allow_html=True)

# Running indicator
if test.status in ['pending', 'running']:
    st.info("🔄 Test is still running. Results will appear here when complete.")
    if st.button("🔄 Refresh"):
        st.rerun()

# Test Information
st.markdown('<div class="section-header">ℹ️ Test Information</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Test ID", test.test_id[:8] + "...")
    st.caption(f"Mode: **{test.mode.upper()}**")

with col2:
    created = datetime.fromisoformat(test.created_at)
    st.metric("Created", created.strftime('%Y-%m-%d'))
    st.caption(created.strftime('%H:%M:%S'))

with col3:
    if test.started_at and test.completed_at:
        start = datetime.fromisoformat(test.started_at)
        end = datetime.fromisoformat(test.completed_at)
        duration = (end - start).total_seconds()
        st.metric("Duration", f"{duration:.1f}s")
    else:
        st.metric("Duration", "N/A")

with col4:
    st.metric("Total Emails", test.total_emails or 0)

# Paths
with st.expander("📁 File Paths"):
    st.text(f"Source: {test.source_path}")
    st.text(f"Output: {test.out_path}")

# Configuration
st.markdown('<div class="section-header">⚙️ Configuration</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Use Filter", "✓ Enabled" if test.use_filter else "✗ Disabled")
with col2:
    st.metric("Async Mode", "✓ Enabled" if test.async_mode else "✗ Disabled")
with col3:
    st.metric("Max Concurrency", test.max_concurrency)

# Per-File Detailed Analysis
if test.status == 'completed' and test.file_analyses:
    st.markdown('<div class="section-header">📈 Detailed Analysis (Per File)</div>', unsafe_allow_html=True)

    # Summary stats across all files
    total_files = len(test.file_analyses)
    successful_analyses = sum(1 for f in test.file_analyses if f.get('status') == 'success')

    st.info(f"📁 **{successful_analyses}/{total_files}** files analyzed successfully")

    # Tabs for each file
    if successful_analyses > 0:
        file_tabs = st.tabs([f"📄 {analysis['file_name']}" for analysis in test.file_analyses if analysis.get('status') == 'success'])

        for idx, analysis in enumerate([a for a in test.file_analyses if a.get('status') == 'success']):
            with file_tabs[idx]:
                display_file_analysis(analysis, test.mode)

    # Show failed analyses
    failed_analyses = [f for f in test.file_analyses if f.get('status') == 'failed']
    if failed_analyses:
        with st.expander("⚠️ Failed Analyses", expanded=False):
            for failed in failed_analyses:
                st.error(f"**{failed['file_name']}**: {failed.get('error', 'Unknown error')}")

# Error message
if test.status == 'failed' and test.error_message:
    st.markdown('<div class="section-header">❌ Error Details</div>', unsafe_allow_html=True)
    st.error(test.error_message)

# Actions
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔙 Back to History", use_container_width=True):
        st.switch_page("pages/2_📚_Test_History.py")

with col2:
    if st.button("🆕 New Test", use_container_width=True):
        st.switch_page("pages/1_📝_New_Test.py")

with col3:
    if st.button("🗑️ Delete Test", use_container_width=True, type="secondary"):
        storage.delete_test(test_id)
        st.success("Test deleted!")
        st.session_state.pop('selected_test_id', None)
        st.switch_page("pages/2_📚_Test_History.py")


def display_file_analysis(analysis: dict, mode: str):
    """Display detailed analysis for a single file"""

    basic_stats = analysis.get('basic_stats', {})
    sr_analysis = analysis.get('sr_analysis', {})
    qf_analysis = analysis.get('quickfill_analysis', {})

    # Basic Statistics
    st.markdown("#### 📊 Basic Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Emails", basic_stats.get('total_emails', 0))
    with col2:
        st.metric("GT SR Creations", basic_stats.get('gt_sr_creation_count', 0))
    with col3:
        st.metric("GT Archives", basic_stats.get('gt_sr_archive_count', 0))

    # SR Opening Analysis
    if mode in ['sr', 'both']:
        st.markdown("#### ✅ SR Opening Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Predicted SR",
                sr_analysis.get('predicted_sr_count', 0),
                help="Number of emails predicted as SR Creation"
            )
        with col2:
            st.metric(
                "Predicted Archive",
                sr_analysis.get('predicted_archive_count', 0),
                help="Number of emails predicted as Archive"
            )
        with col3:
            st.metric(
                "Predicted Review",
                sr_analysis.get('predicted_review_count', 0),
                help="Number of emails predicted as Review (unsure)"
            )

        # Precision Metrics
        st.markdown("##### 🎯 Precision Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            sr_prec = sr_analysis.get('sr_creation_precision')
            if sr_prec is not None:
                st.metric(
                    "SR Creation Precision",
                    f"{sr_prec:.2%}",
                    help="Of all predicted SR, how many are actually SR?"
                )
            else:
                st.metric("SR Creation Precision", "N/A")

        with col2:
            arch_prec = sr_analysis.get('archive_precision')
            if arch_prec is not None:
                st.metric(
                    "Archive Precision",
                    f"{arch_prec:.2%}",
                    help="Of all predicted Archive, how many are actually Archive?"
                )
            else:
                st.metric("Archive Precision", "N/A")

        with col3:
            accuracy = sr_analysis.get('overall_accuracy')
            if accuracy is not None:
                st.metric(
                    "Overall Accuracy",
                    f"{accuracy:.2%}",
                    help="Accuracy excluding Review predictions"
                )
            else:
                st.metric("Overall Accuracy", "N/A")

        # SR Distribution Pie Chart
        pred_sr = sr_analysis.get('predicted_sr_count', 0)
        pred_arch = sr_analysis.get('predicted_archive_count', 0)
        pred_rev = sr_analysis.get('predicted_review_count', 0)

        if pred_sr + pred_arch + pred_rev > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['SR Creation', 'Archive', 'Review'],
                values=[pred_sr, pred_arch, pred_rev],
                marker=dict(colors=['#10b981', '#ef4444', '#f59e0b']),
                hole=0.4
            )])
            fig.update_layout(
                title="SR Prediction Distribution",
                height=350,
                margin=dict(t=50, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    # Quickfill Analysis
    if mode in ['qf', 'both']:
        st.markdown("#### 🏷️ Quickfill Analysis")

        total_qf = qf_analysis.get('total_quickfills_predicted', 0)
        qf_accuracy = qf_analysis.get('accuracy')

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Quickfills Predicted", total_qf)
        with col2:
            if qf_accuracy is not None:
                st.metric("Quickfill Accuracy", f"{qf_accuracy:.2%}")
            else:
                st.metric("Quickfill Accuracy", "N/A")

        # Special Quickfills
        special_counts = qf_analysis.get('special_quickfill_counts', {})
        if special_counts:
            st.markdown("##### ⭐ Special Quickfills")
            cols = st.columns(len(special_counts))
            for idx, (qf_name, count) in enumerate(special_counts.items()):
                with cols[idx]:
                    st.metric(qf_name, count)

        # Quickfill Distribution
        distribution = qf_analysis.get('distribution', {})
        if distribution:
            st.markdown("##### 📊 Quickfill Distribution")

            # Bar chart
            sorted_dist = dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

            fig = go.Figure(data=[
                go.Bar(
                    x=list(sorted_dist.keys()),
                    y=list(sorted_dist.values()),
                    marker_color='#3b82f6',
                    text=list(sorted_dist.values()),
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title="Predicted Quickfill Counts",
                xaxis_title="Quickfill Category",
                yaxis_title="Count",
                height=400,
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)

        # Confusion Matrix
        confusion_matrix = qf_analysis.get('confusion_matrix')
        if confusion_matrix:
            st.markdown("##### 🔀 Confusion Matrix (Ground Truth vs Predicted)")

            labels = confusion_matrix.get('labels', [])
            matrix_data = confusion_matrix.get('matrix', {})

            # Create matrix for heatmap
            matrix_values = []
            for true_label in labels:
                row = []
                for pred_label in labels:
                    row.append(matrix_data.get(true_label, {}).get(pred_label, 0))
                matrix_values.append(row)

            # Heatmap
            fig = go.Figure(data=go.Heatmap(
                z=matrix_values,
                x=[f"Pred: {l}" for l in labels],
                y=[f"True: {l}" for l in labels],
                colorscale='Blues',
                text=matrix_values,
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Count")
            ))
            fig.update_layout(
                title="Confusion Matrix",
                xaxis_title="Predicted Quickfill",
                yaxis_title="Ground Truth Quickfill",
                height=max(400, len(labels) * 40),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show matrix as table
            with st.expander("📋 View as Table"):
                df_matrix = pd.DataFrame(matrix_values, index=labels, columns=labels)
                st.dataframe(df_matrix, use_container_width=True)


# Sidebar
with st.sidebar:
    st.markdown("### 📋 Test Summary")

    st.markdown(f"""
    **Test ID:** `{test.test_id[:12]}...`

    **Status:** {test.status.upper()}

    **Mode:** {test.mode.upper()}

    **Created:** {datetime.fromisoformat(test.created_at).strftime('%Y-%m-%d %H:%M')}
    """)

    if test.status == 'completed':
        st.success("✅ Test completed successfully")

        if test.file_analyses:
            st.markdown("### 📊 Files Analyzed")
            st.metric("Total Files", len(test.file_analyses))

            successful = sum(1 for f in test.file_analyses if f.get('status') == 'success')
            st.metric("Successful", successful)

    elif test.status == 'running':
        st.info("⏳ Processing...")

    elif test.status == 'failed':
        st.error("❌ Test failed")
