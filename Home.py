import streamlit as st
from utils.config import config

# Page config
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #64748b;
        line-height: 1.6;
    }
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
    }
    .mode-item {
        display: flex;
        margin-bottom: 0.75rem;
    }
    .mode-label {
        font-weight: 600;
        min-width: 120px;
        color: #1e293b;
    }
    .mode-desc {
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown(f'<div class="main-header">{config.APP_NAME}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Manage and analyze your email classification tests with ease</div>', unsafe_allow_html=True)

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🚀</div>
        <div class="feature-title">Launch New Test</div>
        <div class="feature-desc">
            Start a new classification test with custom parameters and source files.
            Configure mode, filters, and concurrency settings.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ Go to New Test", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📝_New_Test.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">View Test History</div>
        <div class="feature-desc">
            Browse previous tests and analyze their results. Monitor running tests
            and delete old entries.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ Go to History", use_container_width=True):
        st.switch_page("pages/2_📚_Test_History.py")

# Info box
st.markdown("""
<div class="info-box">
    <h4 style="margin-top: 0; color: #1e40af;">Classification Modes</h4>
    <div class="mode-item">
        <span class="mode-label">SR Mode:</span>
        <span class="mode-desc">Service Request classification only</span>
    </div>
    <div class="mode-item">
        <span class="mode-label">QF Mode:</span>
        <span class="mode-desc">Category/Question Form classification only</span>
    </div>
    <div class="mode-item">
        <span class="mode-label">Both Mode:</span>
        <span class="mode-desc">Complete classification with SR and category detection</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### About")
    st.info(f"""
    **Version:** {config.APP_VERSION}

    This framework allows you to test and evaluate LLM-based email classification systems.
    """)

    st.markdown("### Quick Stats")
    from utils.storage import storage
    tests = storage.get_all_tests()

    total_tests = len(tests)
    completed_tests = sum(1 for t in tests if t.status == 'completed')
    running_tests = sum(1 for t in tests if t.status == 'running')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total_tests)
    with col2:
        st.metric("Done", completed_tests)
    with col3:
        st.metric("Running", running_tests)
