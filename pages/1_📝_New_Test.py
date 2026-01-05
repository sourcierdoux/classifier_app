import streamlit as st
import uuid
from datetime import datetime
from utils.config import config
from utils.storage import storage
from utils.models import TestResult
from utils.classifier import run_classifier
from utils.analysis import analyzer

st.set_page_config(page_title="New Test", page_icon="📝", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .help-text {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📝 Launch New Test")
st.markdown("Configure and start a new email classification test")

# Check if we have a running test in session state
if 'running_test_id' in st.session_state:
    st.info("A test is currently running. Check the results in Test History.")
    if st.button("View Test Results"):
        st.session_state['selected_test_id'] = st.session_state['running_test_id']
        st.switch_page("pages/3_📊_Test_Results.py")
    st.divider()

# Form
with st.form("new_test_form"):
    st.markdown('<div class="section-header">📁 Data Configuration</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        source_path = st.text_input(
            "Source Path *",
            placeholder="/path/to/emails.csv or /path/to/folder",
            help="Path to source file (.csv, .xlsx) or folder containing dataframes"
        )

    with col2:
        out_path = st.text_input(
            "Output Path *",
            value=config.OUTPUT_DIRECTORY,
            help="Path where results will be saved"
        )

    st.markdown('<div class="section-header">⚙️ Classification Settings</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Classification Mode",
        options=['both', 'sr', 'qf'],
        index=0 if config.DEFAULT_MODE == 'both' else (1 if config.DEFAULT_MODE == 'sr' else 2),
        horizontal=True,
        help="Choose which classification to run"
    )

    mode_descriptions = {
        'both': '🔄 **Both** - SR + Category classification (recommended)',
        'sr': '✅ **SR Only** - Service Request classification',
        'qf': '🏷️ **QF Only** - Category classification'
    }
    st.markdown(f"<div class='help-text'>{mode_descriptions[mode]}</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">🔧 Advanced Options</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        use_filter = st.checkbox(
            "Use Aggressive Filters",
            value=config.DEFAULT_USE_FILTER,
            help="Apply data filtering before classification"
        )

        async_mode = st.checkbox(
            "Async Mode",
            value=config.DEFAULT_ASYNC_MODE,
            help="Run predictions in parallel for faster processing"
        )

    with col2:
        max_concurrency = st.slider(
            "Max Concurrency",
            min_value=1,
            max_value=config.MAX_CONCURRENCY_LIMIT,
            value=config.DEFAULT_MAX_CONCURRENCY,
            disabled=not async_mode,
            help="Number of parallel predictions (only applies if async mode is enabled)"
        )

    st.divider()

    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        submit_button = st.form_submit_button(
            "🚀 Start Test",
            use_container_width=True,
            type="primary"
        )

    with col3:
        cancel_button = st.form_submit_button(
            "Cancel",
            use_container_width=True
        )

# Handle form submission
if submit_button:
    if not source_path or not out_path:
        st.error("❌ Please fill in both Source Path and Output Path")
    else:
        # Create test record
        test_id = str(uuid.uuid4())
        test = TestResult(
            test_id=test_id,
            status='pending',
            source_path=source_path,
            out_path=out_path,
            mode=mode,
            use_filter=use_filter,
            async_mode=async_mode,
            max_concurrency=max_concurrency,
            created_at=datetime.now().isoformat()
        )

        storage.save_test(test)

        # Show progress
        with st.spinner("🔄 Running classifier..."):
            try:
                # Update status to running
                test.status = 'running'
                test.started_at = datetime.now().isoformat()
                storage.save_test(test)

                # Run classifier
                results = run_classifier(
                    source_path=source_path,
                    out_path=out_path,
                    mode=mode,
                    use_filter=use_filter,
                    async_mode=async_mode,
                    max_concurrency=max_concurrency
                )

                # Update test with basic results
                test.total_emails = results.get('total_emails', 0)
                test.processed_emails = results.get('processed_emails', 0)
                test.sr_positive = results.get('sr_positive')
                test.sr_negative = results.get('sr_negative')
                test.category_breakdown = results.get('category_breakdown')

                # Run detailed analysis on output files
                st.info("📊 Running detailed analysis on prediction results...")
                try:
                    file_analyses = analyzer.analyze_test_results(out_path)
                    test.file_analyses = file_analyses
                    st.success(f"✅ Analyzed {len(file_analyses)} file(s)")
                except Exception as analysis_error:
                    st.warning(f"⚠️ Analysis completed with warnings: {str(analysis_error)}")
                    test.file_analyses = None

                # Mark as completed
                test.status = 'completed'
                test.completed_at = datetime.now().isoformat()
                storage.save_test(test)

                st.success("✅ Test completed successfully!")
                st.balloons()

                # Redirect to results
                if st.button("📊 View Results"):
                    st.session_state['selected_test_id'] = test_id
                    st.switch_page("pages/3_📊_Test_Results.py")

            except Exception as e:
                # Update status to failed
                test.status = 'failed'
                test.completed_at = datetime.now().isoformat()
                test.error_message = str(e)
                storage.save_test(test)

                st.error(f"❌ Test failed: {str(e)}")

if cancel_button:
    st.switch_page("Home.py")

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ Configuration Tips")
    st.info("""
    **Source Path Examples:**
    - `/data/emails.csv`
    - `/data/email_batch.xlsx`
    - `/data/email_folder/`

    **Mode Selection:**
    - Use **Both** for complete analysis
    - Use **SR Only** for quick SR detection
    - Use **QF Only** for category classification

    **Performance:**
    - Enable Async Mode for faster processing
    - Increase concurrency for more parallelism
    - Use filters to reduce data size
    """)

    with st.expander("🎯 Current Defaults"):
        st.write(f"**Mode:** {config.DEFAULT_MODE}")
        st.write(f"**Filters:** {'Enabled' if config.DEFAULT_USE_FILTER else 'Disabled'}")
        st.write(f"**Async:** {'Enabled' if config.DEFAULT_ASYNC_MODE else 'Disabled'}")
        st.write(f"**Concurrency:** {config.DEFAULT_MAX_CONCURRENCY}")
