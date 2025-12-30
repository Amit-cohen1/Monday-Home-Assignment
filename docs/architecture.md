# Flow Architecture: QBR Auto-Drafter
## Technical Design Document

---

## 1. System Overview

The QBR Auto-Drafter follows a layered architecture pattern with clear separation between data ingestion, processing, AI generation, and output rendering.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                              │
│                         (Streamlit Frontend)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Portfolio  │  │    Single    │  │    Batch     │  │    Export    │ │
│  │   Overview   │  │   Account    │  │  Generation  │  │   Actions    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           COMPONENT LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │    Dashboard     │  │   QBR Generator  │  │    Exporters     │       │
│  │   (Plotly viz)   │  │   (LangChain)    │  │  (PDF/Markdown)  │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                             AI LAYER                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  System Prompt   │  │  QBR Templates   │  │ Structured Output│       │
│  │   (Persona)      │  │  (Multi-stage)   │  │   (Pydantic)     │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                    │                                      │
│                                    ▼                                      │
│                        ┌──────────────────┐                              │
│                        │    OpenAI API    │                              │
│                        │   (GPT-4o)       │                              │
│                        └──────────────────┘                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │    Excel/CSV     │  │    Pandas DF     │  │  Session State   │       │
│  │    (Upload)      │  │   (Processing)   │  │    (Cache)       │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Diagram

```
                    ┌─────────────────┐
                    │   User Action   │
                    │  (Upload Data)  │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                    DATA INGESTION                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  File Read  │───▶│  Validate   │───▶│  DataFrame  │   │
│  │ (xlsx/csv)  │    │  Columns    │    │   Store     │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                 METRICS PROCESSING                         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  For each account:                                   │  │
│  │  • Normalize percentages (0-1 vs 0-100)             │  │
│  │  • Classify risk level (low/medium/high)            │  │
│  │  • Determine story type (growth/turnaround/at_risk) │  │
│  │  • Calculate tickets per user ratio                 │  │
│  │  • Calculate portfolio aggregates                   │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  Dashboard  │   │  AI Prompt  │   │    Batch    │
    │ Rendering   │   │ Generation  │   │  Processing │
    └─────────────┘   └──────┬──────┘   └─────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                    AI GENERATION                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   System    │───▶│   Format    │───▶│   LLM API   │   │
│  │   Prompt    │    │   Prompt    │    │    Call     │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                               │            │
│                                               ▼            │
│                                        ┌─────────────┐    │
│                                        │   Parse     │    │
│                                        │   Output    │    │
│                                        └─────────────┘    │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                    OUTPUT GENERATION                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  Markdown   │    │    PDF      │    │   Display   │   │
│  │   Export    │    │   Export    │    │  (Streamlit)│   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Dashboard Component (`components/dashboard.py`)

**Responsibility**: Render visual metrics and charts using Plotly

**Key Functions**:
| Function | Purpose | Output |
|----------|---------|--------|
| `create_risk_gauge()` | Radial gauge for churn risk | Plotly Figure |
| `create_health_gauge()` | SCAT score visualization | Plotly Figure |
| `create_nps_indicator()` | NPS score with delta | Plotly Figure |
| `create_radar_chart()` | Multi-account comparison | Plotly Figure |
| `create_portfolio_risk_pie()` | Risk distribution | Plotly Figure |
| `render_account_metrics()` | Single account dashboard (includes tickets per user) | Streamlit layout |
| `render_portfolio_overview()` | Portfolio summary | Streamlit layout |

**Derived Metrics**:
| Metric | Calculation | Thresholds |
|--------|-------------|------------|
| Tickets Per User | `tickets_last_quarter / active_users` | ≤0.1 = Low (green), 0.1-0.3 = Medium (orange), >0.3 = High (red) |

**Color Scheme**:
```python
COLORS = {
    'primary': '#6161FF',    # Monday purple
    'success': '#00CA72',    # Green (low risk)
    'warning': '#FDAB3D',    # Orange (medium risk)
    'danger': '#E2445C',     # Red (high risk)
    'info': '#579BFC',       # Blue
    'purple': '#A25DDC'      # Secondary purple
}
```

### 3.2 QBR Generator (`components/qbr_generator.py`)

**Responsibility**: AI-powered QBR content generation with structured outputs

**Class: `QBRGenerator`**
```python
class QBRGenerator:
    def __init__(api_key, model="gpt-4o", temperature=0.3)
    def generate_qbr_markdown(client_data) -> str
    def generate_insights(client_data) -> str
    def generate_recommendations(client_data) -> str
    def classify_story_type(client_data) -> str
    def generate_structured_qbr(client_data) -> QBROutput
```

**Pydantic Models**:
```python
class QBROutput(BaseModel):
    account_name: str
    executive_summary: str
    story_type: Literal["growth", "turnaround", "stable", "at_risk"]
    key_metrics: List[MetricHighlight]
    risks: List[RiskItem]
    recommendations: List[ActionItem]
    next_steps: List[str]
    confidence_score: float
    raw_markdown: str
```

### 3.3 Exporters (`components/exporters.py`)

**Responsibility**: Export QBR content to various formats

**Key Functions**:
| Function | Input | Output |
|----------|-------|--------|
| `export_to_markdown()` | QBR content, client data | Formatted .md string |
| `export_to_pdf()` | QBR content, client data | PDF bytes |
| `export_batch_to_markdown()` | All QBRs, all client data | Combined .md string |

**PDF Branding**: Custom `MondayPDF` class extending fpdf2 with:
- Monday.com header gradient (#6161FF → #A25DDC)
- Metric boxes with color-coded borders
- Section headers with left accent bars
- Branded footer with page numbers

---

## 4. Prompt Engineering Architecture

### 4.1 Prompt Chain

```
┌──────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                              │
│  Establishes: Persona, Constraints, Output Format, Voice     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   USER PROMPT (QBR Request)                   │
│  Contains: All 13 data fields + formatting instructions      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    LLM GENERATION                             │
│  Model: GPT-4o | Temperature: 0.3 | Max tokens: ~2000        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                 STRUCTURED OUTPUT PARSING                     │
│  Extract: Summary, Story Type, Metrics, Risks, Actions       │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Prompt Templates Location

All prompts are centralized in `prompts/qbr_prompts.py`:

| Prompt | Purpose | When Used |
|--------|---------|-----------|
| `SYSTEM_PROMPT` | Establish CSM persona and constraints | Every API call |
| `INSIGHT_EXTRACTOR_PROMPT` | Deep analysis of signals | Optional deep-dive |
| `NARRATIVE_GENERATOR_PROMPT` | Story arc classification | Enrichment |
| `RECOMMENDATION_ENGINE_PROMPT` | Action item generation | Enrichment |
| `FULL_QBR_PROMPT` | Complete document generation | Primary use |

### 4.3 Anti-Hallucination Measures

1. **Explicit Data Binding**: Prompts include all metrics with labels
2. **Cite Requirement**: Instructions to cite data points
3. **Constraint Reminder**: "ONLY reference data explicitly provided"
4. **Confidence Scoring**: Output includes model confidence
5. **Low Temperature**: 0.3 for consistency over creativity

---

## 5. File Structure

```
Monday-Home-Assignment/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── sample_customers_q3_2025.xlsx   # Sample data
│
├── components/
│   ├── __init__.py                 # Component exports
│   ├── dashboard.py                # Plotly visualizations
│   ├── qbr_generator.py            # LangChain + Pydantic
│   └── exporters.py                # PDF/Markdown export
│
├── prompts/
│   ├── __init__.py                 # Prompt exports
│   └── qbr_prompts.py              # All prompt templates
│
├── styles/
│   └── monday_theme.css            # Brand CSS (loaded inline)
│
├── docs/
│   ├── design_brief.md             # This document
│   ├── architecture.md             # Technical architecture
│   └── reflection.md               # Experiment learnings
│
└── assets/
    └── (screenshots, logos)        # Static assets
```

---

## 6. Scalability Considerations

### Current Limitations (Prototype)
- Single-session state (no persistence)
- Sequential batch processing
- No rate limiting beyond manual delays
- Local file storage only

### Production Improvements (Future)
1. **Database Integration**: PostgreSQL for QBR storage
2. **Async Processing**: Celery/Redis for batch jobs
3. **Caching Layer**: Redis for generated QBRs
4. **API Gateway**: FastAPI for monday.com integration
5. **SSO**: monday.com OAuth for authentication

---

## 7. Security Notes

### Current State (Prototype)
- API key entered per-session (not stored)
- No user authentication
- No data encryption at rest

### Production Requirements
- Secure API key management (vault/env)
- Role-based access control
- Audit logging
- Data encryption
- SOC2 compliance considerations

---

*Architecture Document - QBR Auto-Drafter*
*monday.com Innovation Builder Assessment*

