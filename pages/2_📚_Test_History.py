import streamlit as st
import pandas as pd
from datetime import datetime
from utils.storage import storage

st.set_page_config(page_title="Test History", page_icon="📚", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-running {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-completed {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-failed {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Test History")
st.markdown("Browse and manage your classification test history")

# Refresh button
col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Load tests
tests = storage.get_all_tests()

if not tests:
    st.info("📭 No tests found. Create your first test to get started!")
    if st.button("➡️ Create New Test", type="primary"):
        st.switch_page("pages/1_📝_New_Test.py")
else:
    # Filter options
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "Status",
            options=['pending', 'running', 'completed', 'failed'],
            default=['pending', 'running', 'completed', 'failed']
        )

    with col2:
        mode_filter = st.multiselect(
            "Mode",
            options=['sr', 'qf', 'both'],
            default=['sr', 'qf', 'both']
        )

    # Filter tests
    filtered_tests = [
        t for t in tests
        if t.status in status_filter and t.mode in mode_filter
    ]

    st.markdown(f"### 📊 Tests ({len(filtered_tests)} / {len(tests)})")

    # Display tests as cards
    for test in filtered_tests:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"**{test.source_path}**")
                created = datetime.fromisoformat(test.created_at)
                st.caption(f"Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")

            with col2:
                status_class = f"status-{test.status}"
                st.markdown(f'<span class="{status_class}">{test.status.upper()}</span>', unsafe_allow_html=True)
                st.caption(f"Mode: {test.mode.upper()}")

            with col3:
                if test.total_emails is not None:
                    st.metric("Emails", test.total_emails)
                else:
                    st.caption("Emails: -")

            with col4:
                if st.button("👁️ View", key=f"view_{test.test_id}", use_container_width=True):
                    st.session_state['selected_test_id'] = test.test_id
                    st.switch_page("pages/3_📊_Test_Results.py")

                if st.button("🗑️ Delete", key=f"delete_{test.test_id}", use_container_width=True):
                    storage.delete_test(test.test_id)
                    st.rerun()

            st.divider()

    # Statistics
    st.markdown("### 📈 Statistics")
    col1, col2, col3, col4 = st.columns(4)

    total = len(tests)
    completed = sum(1 for t in tests if t.status == 'completed')
    running = sum(1 for t in tests if t.status == 'running')
    failed = sum(1 for t in tests if t.status == 'failed')

    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("Running", running)
    with col4:
        st.metric("Failed", failed)

    # Show detailed table
    if st.checkbox("Show detailed table"):
        df_data = []
        for test in filtered_tests:
            df_data.append({
                'Test ID': test.test_id[:8],
                'Created': datetime.fromisoformat(test.created_at).strftime('%Y-%m-%d %H:%M'),
                'Source': test.source_path.split('/')[-1],
                'Mode': test.mode.upper(),
                'Status': test.status,
                'Emails': test.total_emails if test.total_emails else '-',
                'Filters': '✓' if test.use_filter else '✗',
                'Async': '✓' if test.async_mode else '✗',
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ About Test History")
    st.info("""
    **Features:**
    - View all past tests
    - Filter by status and mode
    - Delete old tests
    - Quick access to results

    **Status Meanings:**
    - 🟡 **Pending**: Waiting to start
    - 🔵 **Running**: Currently processing
    - 🟢 **Completed**: Finished successfully
    - 🔴 **Failed**: Encountered an error
    """)

    if tests:
        st.markdown("### 🕐 Recent Activity")
        recent_tests = tests[:3]
        for test in recent_tests:
            created = datetime.fromisoformat(test.created_at)
            st.caption(f"**{test.status}** - {created.strftime('%H:%M:%S')}")
