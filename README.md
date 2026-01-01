<div align="center">

# 🚀 QBR Auto-Drafter

### AI-Powered Quarterly Business Reviews for Customer Success

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monday-qbr-autodrafter.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI GPT-5.2](https://img.shields.io/badge/OpenAI-GPT--5.2-00A67E.svg)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img src="assets/Monday-Com-Logo.png" alt="monday.com" width="180"/>

**Transform 5+ hours of QBR preparation into 5 minutes**

[Live Demo](https://monday-qbr-autodrafter.streamlit.app) · [Architecture](#-architecture) · [Documentation](#-documentation)

</div>

---

## 📋 Overview

QBR Auto-Drafter is an AI-powered tool that generates professional Quarterly Business Reviews from customer data. Built for Customer Success Managers at monday.com, it combines quantitative metrics with qualitative insights to produce data-grounded, actionable QBR documents.

### The Problem

CSMs spend **5+ hours per account** preparing QBRs:
- Aggregating data from CRM, support tickets, and usage metrics
- Interpreting signals across structured and unstructured data
- Crafting narratives that drive retention and expansion
- Formatting documents for executive presentation

### The Solution

QBR Auto-Drafter automates 80%+ of this workflow:

| Before | After |
|--------|-------|
| 5+ hours per QBR | < 30 minutes |
| 10-15 QBRs per quarter | 40+ QBRs per quarter |
| Inconsistent quality | Standardized, branded output |
| Delayed risk detection | Real-time signal identification |

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Generation
- **GPT-5.2** with optimized prompts
- **LLM-as-Judge validation** ensures quality
- **Zero hallucination** design with data grounding
- Automatic **churn signal detection**

</td>
<td width="50%">

### 📊 Visual Analytics
- Interactive **Plotly dashboards**
- Risk gauges and health indicators
- Portfolio overview with radar charts
- **monday.com branded** styling

</td>
</tr>
<tr>
<td>

### 📄 Export Options
- **Branded PDF** with monday.com styling
- Clean **Markdown** for docs/wikis
- Batch export for entire portfolios
- Ready for executive presentation

</td>
<td>

### ⚠️ Risk Intelligence
- Automatic **story type classification**
- Competitor mention detection
- Support ticket ratio analysis
- Preferred channel optimization

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (Streamlit)                        │
│    Password Auth → Data Upload → Account Selection → Generate QBR        │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
        ┌───────────────────┐                ┌───────────────────┐
        │  📊 Dashboard      │                │  🤖 QBR Generator  │
        │  Plotly Charts    │                │  LangChain + GPT   │
        └───────────────────┘                └─────────┬─────────┘
                                                       │
                                    ┌──────────────────┼──────────────────┐
                                    ▼                  ▼                  ▼
                            ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
                            │  Generate   │──▶│  Validate   │──▶│  Display    │
                            │  (GPT-5.2)  │   │(gpt-4o-mini)│   │  & Export   │
                            └─────────────┘   └─────────────┘   └─────────────┘
                                                    │
                                              ┌─────┴─────┐
                                              │  Retry?   │ (max 2x)
                                              └───────────┘
```

### Validation System

The system implements **LLM-as-Judge** pattern for quality assurance:

| Check | Description |
|-------|-------------|
| 🔴 Critical Signals | Competitor/churn mentions addressed prominently |
| 📝 Feedback Coverage | All CRM notes and customer feedback included |
| 📊 Data Grounding | No hallucinated metrics or invented events |
| 📋 Format Compliance | All required sections present |
| 🎯 Tone Compliance | No exposed internal formulas |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white) |
| **AI/LLM** | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white) |
| **Data** | ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white) |
| **Export** | ![PDF](https://img.shields.io/badge/fpdf2-PDF-red) ![Markdown](https://img.shields.io/badge/Markdown-000000?logo=markdown&logoColor=white) |
| **Deployment** | ![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-FF4B4B?logo=streamlit&logoColor=white) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Monday-Home-Assignment.git
cd Monday-Home-Assignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up secrets for local development
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY = "sk-your-key-here"
APP_PASSWORD = "your-password"
EOF
```

### Run Locally

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Try Sample Data

1. Enter the password when prompted
2. Click **"Try Sample Data"** to load 5 example accounts
3. Navigate to **Single Account QBR** tab
4. Select an account and click **"Generate QBR Report"**

---

## 📁 Project Structure

```
Monday-Home-Assignment/
├── 📄 app.py                       # Main Streamlit application
├── 📄 requirements.txt             # Python dependencies
├── 📊 sample_customers_q3_2025.xlsx # Sample data (5 accounts)
│
├── 🧩 components/
│   ├── __init__.py                 # Component exports
│   ├── dashboard.py                # Plotly visualizations
│   ├── qbr_generator.py            # LangChain + Pydantic generation
│   ├── validator.py                # LLM-as-Judge validation
│   └── exporters.py                # PDF/Markdown export
│
├── 💬 prompts/
│   ├── __init__.py                 # Prompt exports
│   └── qbr_prompts.py              # All prompt templates
│
├── 🎨 styles/
│   └── monday_theme.css            # monday.com branded CSS
│
├── 📚 docs/
│   ├── architecture.md             # Technical architecture
│   ├── design_brief.md             # Product design document
│   ├── deployment.md               # Deployment guide
│   ├── reflection.md               # Development learnings
│   └── architecture_diagram.xml    # draw.io diagram
│
└── 🖼️ assets/
    └── Monday-Com-Logo.png         # monday.com logo
```

---

## 📊 Data Schema

The system expects customer data with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `account_name` | string | Customer company name |
| `plan_type` | string | Basic / Standard / Pro / Enterprise |
| `active_users` | int | Number of active users |
| `usage_growth_qoq` | float | Quarter-over-quarter growth (e.g., 0.22 = 22%) |
| `automation_adoption_pct` | float | Automation feature adoption (0-1) |
| `tickets_last_quarter` | int | Support tickets opened |
| `avg_response_time` | float | Average response time in hours |
| `nps_score` | float | Net Promoter Score (0-10) |
| `preferred_channel` | string | Email / Chat / Phone / In-app |
| `scat_score` | int | Health Score (0-100) |
| `risk_engine_score` | float | Churn risk prediction (0-1) |
| `crm_notes` | string | Internal CRM notes |
| `feedback_summary` | string | Customer feedback/requests |

---

## 💰 Cost Estimation

| Component | Cost | Notes |
|-----------|------|-------|
| **GPT-5.2 Generation** | ~$0.01/QBR | Primary generation |
| **gpt-4o-mini Validation** | ~$0.0003/QBR | Quality check |
| **Streamlit Cloud** | Free | Community tier |
| **Total per QBR** | ~$0.01-0.02 | Varies by content length |

> 💡 **Comparison**: CSM hourly rate ≈ $50-75. At 5 hours per manual QBR = **$250-375 per report**. AI cost is **99.99% cheaper**.

---

## 🔒 Security

- ✅ API keys stored in Streamlit Secrets (never in code)
- ✅ Password protection for app access
- ✅ HTTPS encryption in transit
- ✅ No customer data persistence (session-only)

See [docs/deployment.md](docs/deployment.md) for secure deployment instructions.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Technical design & data flow |
| [Design Brief](docs/design_brief.md) | Product requirements & personas |
| [Deployment](docs/deployment.md) | Streamlit Cloud setup guide |
| [Reflection](docs/reflection.md) | Development learnings & next steps |

---

## 🔮 Roadmap

### Near-term
- [ ] monday.com API integration for live data
- [ ] Historical trend analysis (QoQ comparison)
- [ ] Email delivery integration

### Medium-term
- [ ] Collaborative editing in-app
- [ ] Custom QBR templates
- [ ] Multi-language support

### Long-term
- [ ] Predictive recommendations based on similar accounts
- [ ] Voice summary generation
- [ ] CRM write-back capabilities

---

## 🧪 Prompt Engineering Approach

Following [OpenAI's best practices](https://platform.openai.com/docs/guides/prompt-engineering):

1. **XML-Tagged Sections**: Clear delineation of data, rules, and examples
2. **Role Prompting**: CSM persona with strategic advisor tone
3. **Few-Shot Examples**: Good/bad examples prevent common mistakes
4. **Negative Constraints**: Explicit "never do" rules for internal formulas
5. **Low Temperature (0.3)**: Deterministic, consistent outputs

See [prompts/qbr_prompts.py](prompts/qbr_prompts.py) for full implementation.

---

## 🙏 Acknowledgments

- Built for the **monday.com Innovation Builder Assessment**
- Powered by [OpenAI](https://openai.com) GPT models
- UI framework by [Streamlit](https://streamlit.io)
- Charts by [Plotly](https://plotly.com)

---

<div align="center">

**Built with ❤️ for Customer Success teams**

[⬆ Back to top](#-qbr-auto-drafter)

</div>

