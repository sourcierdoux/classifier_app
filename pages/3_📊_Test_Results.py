import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
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
    .status-completed {
        background-color: #d1fae5;
        color: #065f46;
    }
    .status-running {
        background-color: #dbeafe;
        color: #1e40af;
    }
    .status-failed {
        background-color: #fee2e2;
        color: #991b1b;
    }
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Get test ID from session state or query params
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
    st.metric("Async Mode", "✓" if test.async_mode else "✗")
    st.caption(f"Concurrency: {test.max_concurrency}")

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

# Results (only if completed)
if test.status == 'completed':
    st.markdown('<div class="section-header">📈 Results</div>', unsafe_allow_html=True)

    # Overview metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Emails",
            test.total_emails or 0,
            help="Total number of emails in the dataset"
        )

    with col2:
        st.metric(
            "Processed Emails",
            test.processed_emails or 0,
            help="Number of emails successfully processed"
        )

    # SR Results
    if test.mode in ['sr', 'both'] and test.sr_positive is not None:
        st.markdown("### Service Request Classification")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "SR Positive",
                test.sr_positive,
                delta=f"{(test.sr_positive / test.total_emails * 100):.1f}%" if test.total_emails else None,
                delta_color="off"
            )

        with col2:
            st.metric(
                "SR Negative",
                test.sr_negative,
                delta=f"{(test.sr_negative / test.total_emails * 100):.1f}%" if test.total_emails else None,
                delta_color="off"
            )

        with col3:
            # SR Pie Chart
            if test.total_emails and test.total_emails > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['SR Positive', 'SR Negative'],
                    values=[test.sr_positive, test.sr_negative],
                    marker=dict(colors=['#10b981', '#ef4444']),
                    hole=0.4
                )])
                fig.update_layout(
                    title="SR Distribution",
                    height=300,
                    margin=dict(t=50, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)

    # Category Results
    if test.mode in ['qf', 'both'] and test.category_breakdown:
        st.markdown("### Category Breakdown")

        # Category bar chart
        categories = list(test.category_breakdown.keys())
        counts = list(test.category_breakdown.values())

        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=counts,
                marker_color='#3b82f6',
                text=counts,
                textposition='auto',
            )
        ])
        fig.update_layout(
            title="Category Distribution",
            xaxis_title="Category",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Category table
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### Detailed Breakdown")
            for category, count in test.category_breakdown.items():
                percentage = (count / test.total_emails * 100) if test.total_emails else 0
                st.progress(percentage / 100, text=f"{category}: {count} ({percentage:.1f}%)")

        with col2:
            st.markdown("#### Top Categories")
            sorted_categories = sorted(
                test.category_breakdown.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for i, (category, count) in enumerate(sorted_categories[:5], 1):
                st.metric(f"#{i} {category}", count)

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

        st.markdown("### 📊 Quick Stats")
        st.metric("Emails", test.total_emails or 0)

        if test.sr_positive is not None:
            success_rate = (test.sr_positive / test.total_emails * 100) if test.total_emails else 0
            st.metric("SR Success Rate", f"{success_rate:.1f}%")

    elif test.status == 'running':
        st.info("⏳ Processing...")

    elif test.status == 'failed':
        st.error("❌ Test failed")
