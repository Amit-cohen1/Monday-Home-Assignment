"""
monday.com QBR Auto-Drafter
AI-Powered Quarterly Business Review Generator

Innovation Builder Assessment Prototype
Generates data-driven QBR summaries for Customer Success Managers

Author: Candidate for AI Innovation Builder Role
Date: December 2024
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import time

# Import custom components
from components.dashboard import (
    render_dashboard,
    render_account_metrics,
    render_portfolio_overview,
    COLORS
)
from components.qbr_generator import QBRGenerator
from components.exporters import (
    get_markdown_download_data,
    get_pdf_download_data,
    export_batch_to_markdown
)
from typing import Tuple, List

# ============================================================================
# DATA VALIDATION
# ============================================================================

# Required columns for QBR generation
REQUIRED_COLUMNS = [
    'account_name',
    'plan_type', 
    'active_users',
    'usage_growth_qoq',
    'automation_adoption_pct',
    'tickets_last_quarter',
    'avg_response_time',
    'nps_score',
    'preferred_channel',
    'scat_score',
    'risk_engine_score',
    'crm_notes',
    'feedback_summary'
]

def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that the uploaded DataFrame has the required structure.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Check if DataFrame is empty
    if df is None or df.empty:
        errors.append("The uploaded file is empty or could not be parsed.")
        return False, errors
    
    # Check for required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # If we have the required columns, validate data types and values
    if not missing_columns:
        # Check account_name is not empty
        if df['account_name'].isna().any() or (df['account_name'] == '').any():
            errors.append("'account_name' column contains empty values.")
        
        # Check numeric columns
        numeric_columns = [
            ('active_users', 0, None),
            ('usage_growth_qoq', -1, 1),
            ('automation_adoption_pct', 0, 1),
            ('tickets_last_quarter', 0, None),
            ('avg_response_time', 0, None),
            ('nps_score', 0, 10),
            ('scat_score', 0, 100),
            ('risk_engine_score', 0, 1)
        ]
        
        for col, min_val, max_val in numeric_columns:
            if col in df.columns:
                # Check if column can be converted to numeric
                try:
                    numeric_vals = pd.to_numeric(df[col], errors='coerce')
                    if numeric_vals.isna().all():
                        errors.append(f"'{col}' must contain numeric values.")
                    elif min_val is not None and (numeric_vals < min_val).any():
                        errors.append(f"'{col}' contains values below minimum ({min_val}).")
                    elif max_val is not None and (numeric_vals > max_val).any():
                        errors.append(f"'{col}' contains values above maximum ({max_val}).")
                except Exception:
                    errors.append(f"'{col}' must contain numeric values.")
    
    return len(errors) == 0, errors

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="monday.com QBR Auto-Drafter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION & API KEY HANDLING
# ============================================================================

def check_password():
    """Returns True if the user entered the correct password."""
    # Check if password protection is configured
    if "APP_PASSWORD" not in st.secrets:
        # No password configured, allow access
        return True
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    # Show password prompt
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
        <div style="text-align: center; max-width: 400px; padding: 2rem;">
            <img src="https://dapulse-res.cloudinary.com/image/upload/f_auto,q_auto/remote_mondaycom_static/img/monday-logo-x2.png" 
                 width="180" alt="monday.com" style="margin-bottom: 1.5rem;">
            <h2 style="margin-bottom: 0.5rem;">QBR Auto-Drafter</h2>
            <p style="color: #676879; margin-bottom: 1.5rem;">Enter password to access the application</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Password", type="password", placeholder="Enter password...")
        if st.button("Access App", use_container_width=True, type="primary"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            elif password:
                st.error("Incorrect password. Please try again.")
    
    return False


def get_openai_api_key():
    """Get OpenAI API key from secrets."""
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return None


# Check authentication before proceeding
if not check_password():
    st.stop()

# Get API key from secrets
openai_api_key = get_openai_api_key()

# ============================================================================
# CUSTOM CSS - Monday.com Branding
# ============================================================================

def load_custom_css():
    """Load Monday.com branded CSS with dark mode support."""
    css_file = Path(__file__).parent / "styles" / "monday_theme.css"
    
    # Load external CSS file
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Inline critical CSS with CSS variables for dark mode support
    st.markdown("""
    <style>
    /* Import Figtree font (Monday.com's font) */
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap');
    
    /* CSS Variables for theming */
    :root {
        --app-primary: #6161FF;
        --app-primary-dark: #4B4BCC;
        --app-purple: #A25DDC;
        --app-success: #00CA72;
        --app-warning: #FDAB3D;
        --app-danger: #E2445C;
        --app-bg-primary: #F6F7FB;
        --app-bg-card: #FFFFFF;
        --app-text-primary: #323338;
        --app-text-secondary: #676879;
        --app-border: #E6E9EF;
        --app-shadow: rgba(0, 0, 0, 0.08);
        --app-shadow-hover: rgba(0, 0, 0, 0.12);
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --app-primary: #7B7BFF;
            --app-primary-dark: #6161FF;
            --app-purple: #B87DE8;
            --app-success: #00E085;
            --app-warning: #FFB84D;
            --app-danger: #FF6B7A;
            --app-bg-primary: #1A1A2E;
            --app-bg-card: #1F2937;
            --app-text-primary: #E8E8E8;
            --app-text-secondary: #A0A0A8;
            --app-border: #374151;
            --app-shadow: rgba(0, 0, 0, 0.3);
            --app-shadow-hover: rgba(0, 0, 0, 0.4);
        }
    }
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Figtree', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header gradient - stays consistent in both modes */
    .main-header {
        background: linear-gradient(135deg, var(--app-primary) 0%, var(--app-purple) 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(97, 97, 255, 0.3);
    }
    
    .main-header h1 {
        font-weight: 700;
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
        color: white;
    }
    
    .main-header p {
        opacity: 0.9;
        margin-top: 0.5rem;
        font-size: 1.05rem;
        color: white;
    }
    
    /* Card styling */
    .metric-card {
        background: var(--app-bg-card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px var(--app-shadow);
        border-left: 4px solid var(--app-primary);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--app-shadow-hover);
    }
    
    /* Risk badges */
    .risk-high {
        background: linear-gradient(135deg, var(--app-danger) 0%, #FF6B6B 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, var(--app-warning) 0%, #FFD93D 100%);
        color: #1a1a1a;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }
    
    .risk-low {
        background: linear-gradient(135deg, var(--app-success) 0%, #00E676 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1F1F3D 0%, #2D2D5A 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: rgba(255,255,255,0.9);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--app-primary) 0%, var(--app-primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(97, 97, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(97, 97, 255, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--app-bg-primary);
        padding: 4px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        color: var(--app-text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--app-primary) !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--app-bg-primary);
        border-radius: 8px;
        font-weight: 600;
        color: var(--app-text-primary);
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 202, 114, 0.1) 0%, rgba(0, 202, 114, 0.05) 100%);
        border-left: 4px solid var(--app-success);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(253, 171, 61, 0.1) 0%, rgba(253, 171, 61, 0.05) 100%);
        border-left: 4px solid var(--app-warning);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(226, 68, 92, 0.1) 0%, rgba(226, 68, 92, 0.05) 100%);
        border-left: 4px solid var(--app-danger);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Account selector card */
    .account-selector {
        background: var(--app-bg-card);
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid var(--app-border);
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .account-selector:hover {
        border-color: var(--app-primary);
        box-shadow: 0 4px 12px rgba(97, 97, 255, 0.15);
    }
    
    .account-selector.selected {
        border-color: var(--app-primary);
        background: linear-gradient(135deg, rgba(97, 97, 255, 0.05) 0%, rgba(162, 93, 220, 0.05) 100%);
    }
    
    /* Dark mode specific inline element styles */
    @media (prefers-color-scheme: dark) {
        /* Empty state box */
        .empty-state-box {
            background: var(--app-bg-card) !important;
            border-color: var(--app-border) !important;
        }
        
        .empty-state-box h2, .empty-state-box p {
            color: var(--app-text-primary) !important;
        }
        
        /* Feature cards */
        .feature-card {
            background: var(--app-bg-card) !important;
            border-color: var(--app-border) !important;
        }
        
        .feature-card div {
            color: var(--app-text-primary) !important;
        }
        
        /* Batch generation cards */
        .batch-info-box {
            background: var(--app-bg-card) !important;
            border-color: var(--app-border) !important;
        }
        
        .batch-info-box h3, .batch-info-box p, .batch-info-box div {
            color: var(--app-text-primary) !important;
        }
        
        /* Result cards */
        .result-card {
            background: var(--app-bg-card) !important;
            border-color: var(--app-border) !important;
        }
        
        .result-card div {
            color: var(--app-text-primary) !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'generated_qbrs' not in st.session_state:
    st.session_state.generated_qbrs = {}

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'portfolio'

if 'df' not in st.session_state:
    st.session_state.df = None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <img src="https://dapulse-res.cloudinary.com/image/upload/f_auto,q_auto/remote_mondaycom_static/img/monday-logo-x2.png" 
             width="140" alt="monday.com">
    </div>
    """, unsafe_allow_html=True)
    
    # API Status indicator
    if openai_api_key:
        st.markdown("""
        <div style="background: rgba(0, 202, 114, 0.15); border-radius: 8px; padding: 0.5rem 0.75rem; 
                    display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="color: #00CA72;">✓</span>
            <span style="font-size: 0.85rem; color: #00CA72;">AI Ready</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(226, 68, 92, 0.15); border-radius: 8px; padding: 0.5rem 0.75rem; 
                    margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #E2445C;">⚠</span>
                <span style="font-size: 0.85rem; color: #E2445C;">API key not configured</span>
            </div>
            <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-top: 0.25rem;">
                Contact administrator
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Model settings - collapsed by default for simplicity
    with st.expander("🤖 Advanced Settings", expanded=False):
        model_option = st.selectbox(
            "AI Model",
            [
                "gpt-5.2",          # Latest - Dec 2025, instant/thinking modes
                "gpt-5.1",          # Nov 2025, multimodal + personalities
                "gpt-4.5",          # Feb 2025, "Orion" - largest GPT-4
                "gpt-4o",           # GPT-4 Omni - fast and capable
                "gpt-4o-mini",      # Faster, cheaper GPT-4
                "o1",               # Advanced reasoning model
                "o1-mini",          # Faster reasoning model
            ],
            help="gpt-5.2 is the latest (Dec 2025). gpt-4o recommended for best speed/cost balance."
        )
        
        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Lower = more factual, Higher = more creative"
        )
        
        st.caption("💡 Default settings work great for most cases")
    
    st.divider()
    
    # Quick help section
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    <div style="font-size: 0.8rem; opacity: 0.85; line-height: 1.5;">
        <div style="margin-bottom: 0.75rem;">
            <strong>1.</strong> Upload or try sample data
        </div>
        <div style="margin-bottom: 0.75rem;">
            <strong>2.</strong> Go to "Single Account" tab
        </div>
        <div style="margin-bottom: 0.75rem;">
            <strong>3.</strong> Click "Generate QBR"
        </div>
        <div>
            <strong>4.</strong> Export as PDF or Markdown
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 QBR Auto-Drafter</h1>
    <p>AI-powered Quarterly Business Review generator for Customer Success teams</p>
</div>
""", unsafe_allow_html=True)

# Determine current step for visual indicator
current_step = 1
if st.session_state.df is not None:
    current_step = 2
    if st.session_state.generated_qbrs:
        current_step = 3

# Step indicator - simple version
step1_style = "background: var(--app-success); border-color: var(--app-success); color: white;" if current_step > 1 else ("background: var(--app-primary); border-color: var(--app-primary); color: white;" if current_step == 1 else "background: transparent; opacity: 0.5;")
step2_style = "background: var(--app-success); border-color: var(--app-success); color: white;" if current_step > 2 else ("background: var(--app-primary); border-color: var(--app-primary); color: white;" if current_step == 2 else "background: transparent; opacity: 0.5;")
step3_style = "background: var(--app-primary); border-color: var(--app-primary); color: white;" if current_step == 3 else "background: transparent; opacity: 0.5;"

step1_icon = "✓" if current_step > 1 else "1"
step2_icon = "✓" if current_step > 2 else "2"
step3_icon = "3"

st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
    <div style="display: flex; align-items: center; gap: 0.5rem;">
        <div style="width: 28px; height: 28px; border-radius: 50%; {step1_style} border: 2px solid; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">{step1_icon}</div>
        <span style="font-size: 0.85rem; color: var(--app-text-primary); font-weight: 500;">Upload Data</span>
    </div>
    <div style="width: 30px; height: 2px; background: var(--app-border);"></div>
    <div style="display: flex; align-items: center; gap: 0.5rem;">
        <div style="width: 28px; height: 28px; border-radius: 50%; {step2_style} border: 2px solid; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">{step2_icon}</div>
        <span style="font-size: 0.85rem; color: var(--app-text-primary); font-weight: 500;">Select Account</span>
    </div>
    <div style="width: 30px; height: 2px; background: var(--app-border);"></div>
    <div style="display: flex; align-items: center; gap: 0.5rem;">
        <div style="width: 28px; height: 28px; border-radius: 50%; {step3_style} border: 2px solid; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">{step3_icon}</div>
        <span style="font-size: 0.85rem; color: var(--app-text-primary); font-weight: 500;">Generate QBR</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Data Upload Section with clearer guidance
st.markdown("""
<div style="background: var(--app-bg-card); border-radius: 12px; padding: 1.25rem; 
            border: 1px solid var(--app-border); margin-bottom: 1rem;">
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <span style="background: var(--app-primary); color: white; width: 28px; height: 28px; 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                    font-weight: 600; font-size: 0.85rem;">1</span>
        <span style="font-weight: 600; color: var(--app-text-primary); font-size: 1.1rem;">Start by loading your customer data</span>
    </div>
    <p style="color: var(--app-text-secondary); font-size: 0.9rem; margin: 0 0 0 2.5rem;">
        Upload an Excel or CSV file with your customer metrics, or try our sample data to explore the tool.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📁 Upload Customer Data",
        type=["csv", "xlsx"],
        help="Upload your customer dataset (Excel or CSV)",
        label_visibility="collapsed"
    )

with col2:
    use_sample = st.button("🚀 Try Sample Data", use_container_width=True, type="primary")
    
    # Always show download template button
    sample_path = Path(__file__).parent / "sample_customers_q3_2025.xlsx"
    if sample_path.exists():
        with open(sample_path, "rb") as f:
            st.download_button(
                label="📥 Download Template",
                data=f.read(),
                file_name="qbr_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download sample data file to see the expected format",
                use_container_width=True
            )

# Load data
df = None

if use_sample:
    sample_path = Path(__file__).parent / "sample_customers_q3_2025.xlsx"
    if sample_path.exists():
        try:
            temp_df = pd.read_excel(sample_path)
            is_valid, validation_errors = validate_dataframe(temp_df)
            if is_valid:
                df = temp_df
                st.session_state.df = df
                st.success(f"Loaded sample data: {len(df)} accounts")
            else:
                st.error("⚠️ Sample data validation failed:")
                for error in validation_errors:
                    st.error(f"  • {error}")
        except Exception as e:
            st.error(f"Error loading sample file: {e}")
    else:
        st.error("Sample data file not found")

elif uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            temp_df = pd.read_csv(uploaded_file)
        else:
            temp_df = pd.read_excel(uploaded_file)
        
        # Validate the uploaded data
        is_valid, validation_errors = validate_dataframe(temp_df)
        
        if is_valid:
            df = temp_df
            st.session_state.df = df
            st.success(f"✅ Loaded {len(df)} accounts from {uploaded_file.name}")
        else:
            st.error("⚠️ **Data Validation Failed**")
            st.warning("The uploaded file does not have the required structure. Please ensure your file contains the following columns:")
            
            # Show required columns in an expander
            with st.expander("📋 View Required Columns", expanded=True):
                col1, col2 = st.columns(2)
                half = len(REQUIRED_COLUMNS) // 2
                with col1:
                    for col in REQUIRED_COLUMNS[:half + 1]:
                        st.markdown(f"• `{col}`")
                with col2:
                    for col in REQUIRED_COLUMNS[half + 1:]:
                        st.markdown(f"• `{col}`")
            
            # Show specific validation errors
            with st.expander("🔍 View Validation Errors", expanded=True):
                for error in validation_errors:
                    st.error(f"• {error}")
            
            # Provide download button for sample data
            sample_path = Path(__file__).parent / "sample_customers_q3_2025.xlsx"
            if sample_path.exists():
                with open(sample_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Sample Data Template",
                        data=f.read(),
                        file_name="sample_customers_template.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download this file to see the expected data format"
                    )
            
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.info("Please ensure the file is a valid CSV or Excel file.")

elif st.session_state.df is not None:
    df = st.session_state.df

# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================

if df is not None and openai_api_key:
    
    # Success message with next step guidance
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 202, 114, 0.1) 0%, rgba(0, 202, 114, 0.05) 100%);
                border-left: 4px solid var(--app-success); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.25rem;">✅</span>
            <div>
                <div style="font-weight: 600; color: var(--app-text-primary);">Data loaded successfully!</div>
                <div style="font-size: 0.85rem; color: var(--app-text-secondary);">
                    Now explore your portfolio below, or go to <strong>Single Account</strong> tab to generate a QBR.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    view_tabs = st.tabs(["🏢 Portfolio Overview", "👤 Single Account QBR", "📦 Batch Generate"])
    
    # -------------------------------------------------------------------------
    # TAB 1: PORTFOLIO OVERVIEW
    # -------------------------------------------------------------------------
    with view_tabs[0]:
        render_portfolio_overview(df)
        
        # Raw data expander
        with st.expander("📊 View Raw Data"):
            # Format the dataframe for display
            display_df = df.copy()
            display_df['usage_growth_qoq'] = display_df['usage_growth_qoq'].apply(lambda x: f"{x:.1%}")
            display_df['automation_adoption_pct'] = display_df['automation_adoption_pct'].apply(lambda x: f"{x:.0%}")
            display_df['risk_engine_score'] = display_df['risk_engine_score'].apply(lambda x: f"{x:.0%}")
            st.dataframe(display_df, use_container_width=True)
    
    # -------------------------------------------------------------------------
    # TAB 2: SINGLE ACCOUNT QBR
    # -------------------------------------------------------------------------
    with view_tabs[1]:
        
        # Guidance header
        st.markdown("""
        <div style="background: var(--app-bg-card); border-radius: 12px; padding: 1rem 1.25rem; 
                    border: 1px solid var(--app-border); margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">👤</span>
                <div>
                    <div style="font-weight: 600; color: var(--app-text-primary);">Generate a Single Account QBR</div>
                    <div style="font-size: 0.85rem; color: var(--app-text-secondary);">
                        Select an account below, review their metrics, then click Generate to create an AI-powered QBR.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Account selector with label
        col_select, col_info = st.columns([3, 1])
        with col_select:
            selected_account = st.selectbox(
                "🔍 Select an Account",
                options=df['account_name'].tolist(),
                help="Choose an account to generate QBR"
            )
        with col_info:
            if selected_account:
                client_data_preview = df[df['account_name'] == selected_account].iloc[0]
                risk = client_data_preview['risk_engine_score']
                if risk >= 0.6:
                    risk_badge = ("🔴", "High Risk", "var(--app-danger)")
                elif risk >= 0.3:
                    risk_badge = ("🟡", "Medium", "var(--app-warning)")
                else:
                    risk_badge = ("🟢", "Healthy", "var(--app-success)")
                st.markdown(f"""
                <div style="background: var(--app-bg-card); border-radius: 8px; padding: 0.75rem; 
                            text-align: center; border: 1px solid var(--app-border); margin-top: 1.5rem;">
                    <div style="font-size: 1.25rem;">{risk_badge[0]}</div>
                    <div style="font-size: 0.8rem; color: {risk_badge[2]}; font-weight: 600;">{risk_badge[1]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if selected_account:
            client_data = df[df['account_name'] == selected_account].iloc[0].to_dict()
            
            # Render metrics dashboard
            render_account_metrics(client_data)
            
            # Generation section with prominent CTA
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(97, 97, 255, 0.1) 0%, rgba(162, 93, 220, 0.1) 100%);
                        border-radius: 12px; padding: 1.25rem; margin: 1rem 0; border: 1px solid var(--app-border);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.25rem;">🤖</span>
                    <div>
                        <div style="font-weight: 600; color: var(--app-text-primary);">Ready to generate?</div>
                        <div style="font-size: 0.85rem; color: var(--app-text-secondary);">
                            Click the button below to create an AI-powered Quarterly Business Review for this account.
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                generate_btn = st.button(
                    "🚀 Generate QBR Report",
                    use_container_width=True,
                    type="primary"
                )
            
            # Check if QBR already generated
            cached_qbr = st.session_state.generated_qbrs.get(selected_account)
            
            if generate_btn or cached_qbr:
                if generate_btn:
                    # Generate new QBR
                    with st.spinner(f"Analyzing {selected_account} and generating insights..."):
                        try:
                            generator = QBRGenerator(
                                api_key=openai_api_key,
                                model=model_option,
                                temperature=temperature
                            )
                            
                            qbr_output = generator.generate_structured_qbr(client_data)
                            
                            # Cache the result
                            st.session_state.generated_qbrs[selected_account] = qbr_output
                            
                        except Exception as e:
                            st.error(f"Error generating QBR: {e}")
                            st.stop()
                else:
                    qbr_output = cached_qbr
                
                # Display results
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # Story type badge
                story_colors = {
                    'growth': ('🚀', '#00CA72', 'Growth Story'),
                    'turnaround': ('🔄', '#579BFC', 'Turnaround Story'),
                    'stable': ('📊', '#FDAB3D', 'Stable Account'),
                    'at_risk': ('⚠️', '#E2445C', 'At-Risk Account')
                }
                
                emoji, color, label = story_colors.get(qbr_output.story_type, ('📋', '#6161FF', 'QBR'))
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                    <span style="background: {color}; color: white; padding: 0.5rem 1.25rem; 
                                border-radius: 20px; font-weight: 600; font-size: 0.9rem;">
                        {emoji} {label}
                    </span>
                    <span style="color: var(--app-text-secondary); font-size: 0.9rem;">
                        Confidence: {qbr_output.confidence_score:.0%}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # QBR Content
                col_qbr, col_actions = st.columns([3, 1])
                
                with col_qbr:
                    # Display QBR content with styling applied via CSS
                    st.markdown(qbr_output.raw_markdown)
                
                with col_actions:
                    st.markdown("### ⚡ Actions")
                    
                    # Risk-based action
                    if client_data['risk_engine_score'] >= 0.5:
                        st.markdown("""
                        <div class="risk-high">⚠️ High Risk Detected</div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    elif client_data['risk_engine_score'] >= 0.3:
                        st.markdown("""
                        <div class="risk-medium">⚡ Medium Risk</div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="risk-low">✅ Healthy Account</div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    # Export buttons
                    st.markdown("### 📤 Export")
                    
                    # Markdown download
                    md_content, md_filename = get_markdown_download_data(
                        qbr_output.raw_markdown,
                        selected_account,
                        client_data
                    )
                    
                    st.download_button(
                        label="📄 Download Markdown",
                        data=md_content,
                        file_name=md_filename,
                        mime="text/plain",
                        key=f"md_download_{selected_account}",
                        use_container_width=True
                    )
                    
                    # PDF download
                    try:
                        pdf_content, pdf_filename = get_pdf_download_data(
                            qbr_output.raw_markdown,
                            selected_account,
                            client_data
                        )
                        
                        st.download_button(
                            label="📑 Download PDF",
                            data=pdf_content,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key=f"pdf_download_{selected_account}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"PDF export unavailable: {e}")
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    # Recommendations summary
                    st.markdown("### 🎯 Top Actions")
                    for rec in qbr_output.recommendations[:3]:
                        priority_colors = {
                            'immediate': 'var(--app-danger)',
                            'short-term': 'var(--app-warning)',
                            'long-term': '#579BFC'
                        }
                        color = priority_colors.get(rec.priority, 'var(--app-primary)')
                        st.markdown(f"""
                        <div style="background: var(--app-bg-primary); border-radius: 8px; padding: 0.75rem; 
                                    margin-bottom: 0.5rem; border-left: 3px solid {color};">
                            <div style="font-weight: 600; font-size: 0.85rem; color: var(--app-text-primary);">
                                {rec.action_title}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--app-text-secondary); margin-top: 0.25rem;">
                                {rec.owner} • {rec.priority}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # TAB 3: BATCH GENERATION
    # -------------------------------------------------------------------------
    with view_tabs[2]:
        # Guidance header
        st.markdown("""
        <div style="background: var(--app-bg-card); border-radius: 12px; padding: 1rem 1.25rem; 
                    border: 1px solid var(--app-border); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">📦</span>
                <div>
                    <div style="font-weight: 600; color: var(--app-text-primary);">Batch QBR Generation</div>
                    <div style="font-size: 0.85rem; color: var(--app-text-secondary);">
                        Generate QBRs for multiple accounts at once. Perfect for quarterly review preparation.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step 1: Account selection
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
            <span style="background: var(--app-primary); color: white; width: 24px; height: 24px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: 600; font-size: 0.8rem;">1</span>
            <span style="font-weight: 600; color: var(--app-text-primary);">Select accounts to include</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_accounts = st.multiselect(
                "Choose accounts to include",
                options=df['account_name'].tolist(),
                default=df['account_name'].tolist(),
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown(f"""
            <div style="background: var(--app-bg-card); border-radius: 8px; padding: 1rem; text-align: center;
                        border: 1px solid var(--app-border);">
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--app-primary);">
                    {len(selected_accounts)}
                </div>
                <div style="font-size: 0.75rem; color: var(--app-text-secondary);">accounts selected</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Step 2: Generate
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 1.5rem 0 0.75rem 0;">
            <span style="background: var(--app-primary); color: white; width: 24px; height: 24px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: 600; font-size: 0.8rem;">2</span>
            <span style="font-weight: 600; color: var(--app-text-primary);">Generate all reports</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Estimate time
        estimated_time = len(selected_accounts) * 8  # ~8 seconds per account
        st.caption(f"⏱️ Estimated time: ~{estimated_time} seconds for {len(selected_accounts)} accounts")
        
        # Generate button
        if st.button("🚀 Generate All QBRs", use_container_width=True, type="primary"):
            
            if not selected_accounts:
                st.warning("Please select at least one account")
            else:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                batch_results = {}
                all_client_data = {}
                
                generator = QBRGenerator(
                    api_key=openai_api_key,
                    model=model_option,
                    temperature=temperature
                )
                
                for idx, account in enumerate(selected_accounts):
                    status_text.markdown(f"**Generating QBR for {account}...** ({idx + 1}/{len(selected_accounts)})")
                    
                    try:
                        client_data = df[df['account_name'] == account].iloc[0].to_dict()
                        all_client_data[account] = client_data
                        
                        qbr_output = generator.generate_structured_qbr(client_data)
                        batch_results[account] = qbr_output.raw_markdown
                        
                        # Cache individual results
                        st.session_state.generated_qbrs[account] = qbr_output
                        
                    except Exception as e:
                        batch_results[account] = f"Error generating QBR: {e}"
                    
                    progress_bar.progress((idx + 1) / len(selected_accounts))
                    time.sleep(0.5)  # Rate limiting
                
                status_text.markdown("**✅ All QBRs generated successfully!**")
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # Results summary
                st.markdown("#### 📊 Generation Results")
                
                result_cols = st.columns(len(selected_accounts))
                
                for idx, account in enumerate(selected_accounts):
                    with result_cols[idx]:
                        client_data = all_client_data[account]
                        risk = client_data['risk_engine_score']
                        
                        if risk >= 0.6:
                            badge = "🔴"
                            color = "#E2445C"
                        elif risk >= 0.3:
                            badge = "🟡"
                            color = "#FDAB3D"
                        else:
                            badge = "🟢"
                            color = "#00CA72"
                        
                        st.markdown(f"""
                        <div class="result-card" style="background: var(--app-bg-card); border-radius: 12px; padding: 1rem;
                                    border: 1px solid var(--app-border); text-align: center;">
                            <div style="font-size: 1.5rem;">{badge}</div>
                            <div style="font-weight: 600; font-size: 0.85rem; color: var(--app-text-primary); 
                                        margin-top: 0.5rem; overflow: hidden; text-overflow: ellipsis;">
                                {account}
                            </div>
                            <div style="font-size: 0.75rem; color: {color}; margin-top: 0.25rem;">
                                Risk: {risk:.0%}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                
                # Batch export
                st.markdown("#### 📤 Export All")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Combined markdown
                    combined_md = export_batch_to_markdown(batch_results, all_client_data)
                    
                    st.download_button(
                        label="📄 Download All (Markdown)",
                        data=combined_md.encode('utf-8'),
                        file_name="QBR_Portfolio_Q3_2025.md",
                        mime="text/plain",
                        key="batch_md_download",
                        use_container_width=True
                    )
                
                with col2:
                    st.info("💡 Individual PDFs available in Single Account view")
                
                # Individual QBR expanders
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                st.markdown("#### 📋 Individual QBRs")
                
                for account, qbr_content in batch_results.items():
                    with st.expander(f"📊 {account}"):
                        st.markdown(qbr_content)

elif df is not None and not openai_api_key:
    st.error("⚠️ OpenAI API key is not configured. Please contact the administrator to enable QBR generation.")
    
    # Still show data preview
    st.markdown("### 📊 Data Preview")
    render_portfolio_overview(df)

else:
    # Empty state with clear guidance
    empty_state_html = """<div class="empty-state-box" style="text-align: center; padding: 3rem 2rem; background: var(--app-bg-card); border-radius: 16px; border: 1px solid var(--app-border); box-shadow: 0 4px 24px var(--app-shadow);">
<div style="font-size: 4rem; margin-bottom: 1rem;">👋</div>
<h2 style="color: var(--app-text-primary); margin-bottom: 0.5rem;">Welcome to QBR Auto-Drafter</h2>
<p style="color: var(--app-text-secondary); max-width: 550px; margin: 0 auto 1.5rem auto; line-height: 1.6;">Generate professional Quarterly Business Reviews in seconds using AI. Just upload your customer data and let us handle the rest.</p>
<div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;">
<div style="display: flex; align-items: center; gap: 0.5rem; color: var(--app-text-secondary); font-size: 0.9rem;"><span style="color: var(--app-success);">✓</span> No complex setup</div>
<div style="display: flex; align-items: center; gap: 0.5rem; color: var(--app-text-secondary); font-size: 0.9rem;"><span style="color: var(--app-success);">✓</span> Export to PDF</div>
<div style="display: flex; align-items: center; gap: 0.5rem; color: var(--app-text-secondary); font-size: 0.9rem;"><span style="color: var(--app-success);">✓</span> Risk detection built-in</div>
</div>
<div style="background: linear-gradient(135deg, rgba(97, 97, 255, 0.1) 0%, rgba(162, 93, 220, 0.1) 100%); border-radius: 12px; padding: 1.5rem; max-width: 400px; margin: 0 auto;">
<div style="font-weight: 600; color: var(--app-text-primary); margin-bottom: 0.5rem;">👆 Get started above</div>
<div style="font-size: 0.9rem; color: var(--app-text-secondary);">Upload a CSV/Excel file with customer data, or click <strong>Try Sample Data</strong> to explore with demo data.</div>
</div>
</div>"""
    st.markdown(empty_state_html, unsafe_allow_html=True)
    
    # How it works section
    how_it_works_html = """<div style="margin-top: 2rem;">
<h3 style="text-align: center; color: var(--app-text-primary); margin-bottom: 1.5rem;">How it works</h3>
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
<div style="background: var(--app-bg-card); border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid var(--app-border); position: relative;">
<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--app-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">1</div>
<div style="font-size: 2rem; margin: 0.5rem 0;">📁</div>
<div style="font-weight: 600; color: var(--app-text-primary);">Upload Data</div>
<div style="font-size: 0.85rem; color: var(--app-text-secondary); margin-top: 0.25rem;">Import your customer metrics from Excel or CSV</div>
</div>
<div style="background: var(--app-bg-card); border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid var(--app-border); position: relative;">
<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--app-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">2</div>
<div style="font-size: 2rem; margin: 0.5rem 0;">🤖</div>
<div style="font-weight: 600; color: var(--app-text-primary);">AI Analysis</div>
<div style="font-size: 0.85rem; color: var(--app-text-secondary); margin-top: 0.25rem;">GPT-4 analyzes metrics and generates insights</div>
</div>
<div style="background: var(--app-bg-card); border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid var(--app-border); position: relative;">
<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--app-primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem;">3</div>
<div style="font-size: 2rem; margin: 0.5rem 0;">📄</div>
<div style="font-weight: 600; color: var(--app-text-primary);">Export & Share</div>
<div style="font-size: 0.85rem; color: var(--app-text-secondary); margin-top: 0.25rem;">Download as PDF or Markdown to share with clients</div>
</div>
</div>
</div>"""
    st.markdown(how_it_works_html, unsafe_allow_html=True)
