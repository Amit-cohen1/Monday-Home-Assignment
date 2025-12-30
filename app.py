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
# CUSTOM CSS - Monday.com Branding
# ============================================================================

def load_custom_css():
    """Load Monday.com branded CSS."""
    css_file = Path(__file__).parent / "styles" / "monday_theme.css"
    
    # Inline critical CSS
    st.markdown("""
    <style>
    /* Import Figtree font (Monday.com's font) */
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap');
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Figtree', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #6161FF 0%, #A25DDC 100%);
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
    }
    
    .main-header p {
        opacity: 0.9;
        margin-top: 0.5rem;
        font-size: 1.05rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #6161FF;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    /* Risk badges */
    .risk-high {
        background: linear-gradient(135deg, #E2445C 0%, #FF6B6B 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #FDAB3D 0%, #FFD93D 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #00CA72 0%, #00E676 100%);
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
        background: linear-gradient(135deg, #6161FF 0%, #4B4BCC 100%);
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
        background: #F6F7FB;
        padding: 4px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #6161FF !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F6F7FB;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 202, 114, 0.1) 0%, rgba(0, 202, 114, 0.05) 100%);
        border-left: 4px solid #00CA72;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(253, 171, 61, 0.1) 0%, rgba(253, 171, 61, 0.05) 100%);
        border-left: 4px solid #FDAB3D;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(226, 68, 92, 0.1) 0%, rgba(226, 68, 92, 0.05) 100%);
        border-left: 4px solid #E2445C;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Account selector card */
    .account-selector {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid #E6E9EF;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .account-selector:hover {
        border-color: #6161FF;
        box-shadow: 0 4px 12px rgba(97, 97, 255, 0.15);
    }
    
    .account-selector.selected {
        border-color: #6161FF;
        background: linear-gradient(135deg, rgba(97, 97, 255, 0.05) 0%, rgba(162, 93, 220, 0.05) 100%);
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
    
    st.markdown("### ⚙️ Configuration")
    
    # API Key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to enable AI features",
        placeholder="sk-..."
    )
    
    if openai_api_key:
        st.success("API Key configured")
    else:
        st.warning("Enter API key to proceed")
    
    st.divider()
    
    # Model settings
    st.markdown("### 🤖 Model Settings")
    
    model_option = st.selectbox(
        "AI Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        help="Select the AI model for QBR generation"
    )
    
    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower = more consistent, Higher = more creative"
    )
    
    st.divider()
    
    # About section
    st.markdown("### 📖 About")
    st.markdown("""
    <div style="font-size: 0.85rem; opacity: 0.8;">
    This prototype demonstrates AI-powered QBR generation for Customer Success teams.
    <br><br>
    <b>Built for:</b> monday.com Innovation Builder Assessment
    <br><br>
    <b>Features:</b>
    <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
        <li>Visual dashboards</li>
        <li>AI-generated insights</li>
        <li>Risk classification</li>
        <li>PDF/Markdown export</li>
    </ul>
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

# Data Upload Section
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📁 Upload Customer Data",
        type=["csv", "xlsx"],
        help="Upload your customer dataset (Excel or CSV)"
    )

with col2:
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    use_sample = st.button("📋 Use Sample Data", use_container_width=True)
    
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
    
    # View Toggle
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    view_tabs = st.tabs(["🏢 Portfolio Overview", "👤 Single Account", "📦 Batch Generate"])
    
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
        
        # Account selector
        selected_account = st.selectbox(
            "Select Account",
            options=df['account_name'].tolist(),
            help="Choose an account to generate QBR"
        )
        
        if selected_account:
            client_data = df[df['account_name'] == selected_account].iloc[0].to_dict()
            
            # Render metrics dashboard
            render_account_metrics(client_data)
            
            st.divider()
            
            # Generation section
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                generate_btn = st.button(
                    "🚀 Generate QBR",
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
                    <span style="color: #676879; font-size: 0.9rem;">
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
                            'immediate': '#E2445C',
                            'short-term': '#FDAB3D',
                            'long-term': '#579BFC'
                        }
                        color = priority_colors.get(rec.priority, '#6161FF')
                        st.markdown(f"""
                        <div style="background: #F6F7FB; border-radius: 8px; padding: 0.75rem; 
                                    margin-bottom: 0.5rem; border-left: 3px solid {color};">
                            <div style="font-weight: 600; font-size: 0.85rem; color: #323338;">
                                {rec.action_title}
                            </div>
                            <div style="font-size: 0.75rem; color: #676879; margin-top: 0.25rem;">
                                {rec.owner} • {rec.priority}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # TAB 3: BATCH GENERATION
    # -------------------------------------------------------------------------
    with view_tabs[2]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(97, 97, 255, 0.1) 0%, rgba(162, 93, 220, 0.1) 100%);
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #E6E9EF;">
            <h3 style="margin: 0 0 0.5rem 0; color: #323338;">📦 Batch QBR Generation</h3>
            <p style="margin: 0; color: #676879;">
                Generate QBRs for all accounts in your dataset with one click. 
                Perfect for preparing quarterly reviews across your entire portfolio.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Account selection
        st.markdown("#### Select Accounts")
        
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
            <div style="background: white; border-radius: 8px; padding: 1rem; text-align: center;
                        border: 1px solid #E6E9EF; height: 100%;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #6161FF;">
                    {len(selected_accounts)}
                </div>
                <div style="font-size: 0.75rem; color: #676879;">accounts selected</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
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
                        <div style="background: white; border-radius: 12px; padding: 1rem;
                                    border: 1px solid #E6E9EF; text-align: center;">
                            <div style="font-size: 1.5rem;">{badge}</div>
                            <div style="font-weight: 600; font-size: 0.85rem; color: #323338; 
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
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to enable QBR generation.")
    
    # Still show data preview
    st.markdown("### 📊 Data Preview")
    render_portfolio_overview(df)

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: #F6F7FB; 
                border-radius: 16px; border: 2px dashed #E6E9EF;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
        <h2 style="color: #323338; margin-bottom: 0.5rem;">Welcome to QBR Auto-Drafter</h2>
        <p style="color: #676879; max-width: 500px; margin: 0 auto;">
            Upload your customer data or use the sample dataset to get started. 
            Our AI will generate comprehensive Quarterly Business Reviews in seconds.
        </p>
        <div style="margin-top: 2rem;">
            <span style="background: #6161FF; color: white; padding: 0.5rem 1rem; 
                        border-radius: 8px; font-weight: 500;">
                ⬆️ Upload data above to begin
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("📈", "Visual Dashboards", "Interactive charts and metrics"),
        ("🤖", "AI Insights", "GPT-4 powered analysis"),
        ("⚠️", "Risk Detection", "Automatic churn signals"),
        ("📄", "Export Ready", "PDF & Markdown output")
    ]
    
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; 
                        text-align: center; border: 1px solid #E6E9EF;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-weight: 600; color: #323338;">{title}</div>
                <div style="font-size: 0.85rem; color: #676879; margin-top: 0.25rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
