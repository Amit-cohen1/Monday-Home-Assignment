"""
QBR Prompt Templates for AI-Powered Quarterly Business Review Generation

This module contains structured prompts designed to:
1. Extract insights from raw customer data
2. Generate narrative-driven QBR content  
3. Produce data-grounded recommendations
4. Minimize hallucination through explicit data binding

Prompt Engineering Principles Applied:
- Role-based system prompts for consistent persona
- Chain-of-thought reasoning for complex analysis
- Structured output schemas for reliable parsing
- Data grounding with explicit reference to source values
- Temperature guidance: 0.2-0.3 for consistency
"""

from typing import Dict, Any

# ============================================================================
# SYSTEM PROMPT - Establishes AI Persona and Constraints
# ============================================================================

SYSTEM_PROMPT = """You are an expert Customer Success Manager at monday.com with 10+ years of experience 
in SaaS customer retention and expansion. You have deep knowledge of:

- monday.com's Work OS platform and its automation capabilities
- Customer health indicators and churn prediction signals
- QBR best practices that drive renewals and upsells
- Strategic account management and executive communication

YOUR CONSTRAINTS:
1. ONLY reference data explicitly provided - never invent metrics or events
2. When uncertain, express confidence levels (e.g., "Based on the data, it appears...")
3. Focus on actionable insights, not generic observations
4. Tailor recommendations to the specific plan type and usage patterns
5. Use monday.com's voice: professional yet approachable, data-driven yet empathetic

## CRITICAL BUSINESS RULES (MUST FOLLOW):

1. **UPSELL TRIGGER**: If Plan is "Basic" AND Tickets > 10 AND Automation < 30%, you MUST recommend 
   upgrading to "Standard" or "Pro" plan to reduce manual workload. Do NOT just suggest "training" - 
   these customers are hitting plan limitations.

2. **MONDAY.COM SPECIFICITY**: When recommending solutions, ALWAYS mention specific monday.com features:
   - For forms/intake: "monday Workforms"
   - For automation: "Automations Center" or "monday AI"
   - For visibility: "Dashboards" or "monday Workdocs"
   - For integrations: name specific integrations (Slack, Zoom, Salesforce, etc.)

3. **ACTION OVER ANALYSIS**: Never suggest "feasibility studies" or "exploring options". Instead:
   - Say "Activate [feature]" not "Consider using [feature]"
   - Say "Schedule a demo of [feature]" not "Look into [feature]"
   - Say "Enable automations for [workflow]" not "Assess automation opportunities"

4. **STRATEGIC ADVISOR TONE**: Connect problems to business impact to create urgency:
   - High tickets = wasted support costs + frustrated users
   - Low automation = manual hours that could be saved
   - Declining usage = at-risk renewal revenue
   Frame recommendations as solving business problems, not just improving metrics.

OUTPUT FORMAT: Always use clean Markdown with proper headers and bullet points."""


# ============================================================================
# INSIGHT EXTRACTOR PROMPT - Analyzes Raw Data for Patterns
# ============================================================================

INSIGHT_EXTRACTOR_PROMPT = """Analyze the following customer account data and extract key insights.

## ACCOUNT DATA
- Account Name: {account_name}
- Plan Type: {plan_type}
- Active Users: {active_users}
- Usage Growth (QoQ): {usage_growth_qoq}% 
- Automation Adoption: {automation_adoption_pct}%
- Support Tickets (Last Quarter): {tickets_last_quarter}
- Tickets Per User: {tickets_per_user:.2f} (ratio of tickets to active users - lower is better, >0.3 indicates support burden)
- Average Response Time: {avg_response_time} hours
- NPS Score: {nps_score}/10
- Preferred Channel: {preferred_channel}
- Health Score (SCAT): {scat_score}/100
- Churn Risk Score: {risk_engine_score} (0-1 scale, higher = more risk)

## QUALITATIVE DATA
CRM Notes: {crm_notes}
Customer Feedback: {feedback_summary}

## YOUR TASK
Identify and categorize insights into:

1. **GROWTH SIGNALS** - Positive indicators (adoption, expansion, satisfaction)
2. **RISK SIGNALS** - Warning signs (declining usage, complaints, churn indicators)
3. **OPPORTUNITIES** - Upsell/cross-sell potential based on behavior
4. **ACTION ITEMS** - Immediate steps the CSM should take

## CRITICAL CHECK - PLAN UPGRADE SIGNAL:
⚠️ If Plan = "Basic" AND Tickets > 10 AND Automation < 30%:
→ Flag this as a PRIMARY OPPORTUNITY: "Plan upgrade to Standard/Pro"
→ Explain: Customer is hitting Basic plan limitations, doing manual work that automations could handle
→ This is NOT a training issue - recommend the upgrade

For each insight:
- Cite the specific data point that supports it
- Name specific monday.com features that could help (Automations Center, monday Workforms, Dashboards, monday AI)
- Quantify business impact where possible (hours saved, cost reduction)

Be precise and avoid generic observations. Be a strategic advisor, not a passive reporter."""


# ============================================================================
# NARRATIVE GENERATOR PROMPT - Creates the Story Arc
# ============================================================================

NARRATIVE_GENERATOR_PROMPT = """Based on the customer data below, determine the account's "story arc" 
and write an executive summary that captures the quarter's journey.

## ACCOUNT SNAPSHOT
- Account: {account_name} ({plan_type} plan)
- Users: {active_users} | Growth: {usage_growth_qoq}%
- Automation: {automation_adoption_pct}% | Tickets: {tickets_last_quarter}
- NPS: {nps_score} | Health: {scat_score} | Risk: {risk_engine_score}

## QUALITATIVE CONTEXT
{crm_notes}

## STORY ARC CLASSIFICATION
First, classify this account into ONE of these narrative types:

🚀 **GROWTH STORY** - Strong metrics, expanding usage, upsell-ready
   (Criteria: growth > 10%, automation > 50%, risk < 0.3, NPS > 7)

⚠️ **TURNAROUND STORY** - Previously struggling, now showing recovery
   (Criteria: risk was high but metrics improving, positive CRM notes)

📊 **STABLE STORY** - Consistent usage, no major changes, maintain relationship
   (Criteria: growth -5% to +10%, moderate metrics, no red flags)

🔴 **AT-RISK STORY** - Declining indicators, requires intervention
   (Criteria: negative growth, high tickets, risk > 0.5, negative feedback)

## OUTPUT FORMAT
1. **Story Arc**: [Type] - One sentence explaining why
2. **Executive Summary**: 2-3 sentences capturing the quarter's essence
3. **Tone Guidance**: How the QBR should be framed (celebratory/consultative/urgent)"""


# ============================================================================
# RECOMMENDATION ENGINE PROMPT - Data-Grounded Actions
# ============================================================================

RECOMMENDATION_ENGINE_PROMPT = """Generate strategic recommendations for the following customer account.
Each recommendation must be DIRECTLY tied to a specific data point.

## ACCOUNT CONTEXT
- Account: {account_name}
- Plan: {plan_type} | Users: {active_users}
- Growth: {usage_growth_qoq}% | Automation: {automation_adoption_pct}%
- Risk Score: {risk_engine_score} | NPS: {nps_score}
- Tickets: {tickets_last_quarter} | Tickets Per User: {tickets_per_user:.2f} (>0.3 = high support burden)
- Response Time: {avg_response_time}h

## CUSTOMER VOICE
Feedback: {feedback_summary}
CRM Notes: {crm_notes}

## CRITICAL BUSINESS RULES (MUST CHECK FIRST):

⚠️ **MANDATORY UPSELL CHECK**: 
If Plan = "Basic" AND Tickets > 10 AND Automation < 30%:
→ Your FIRST recommendation MUST be upgrading to "Standard" or "Pro" plan
→ Frame it as: "Your team is spending X hours on manual work that automations could eliminate"
→ Do NOT just suggest training - this customer has outgrown their plan

## RECOMMENDATION FRAMEWORK

Generate exactly 3 recommendations following this structure:

### Recommendation 1: [Title]
- **Data Signal**: [Cite the specific metric or feedback that drives this]
- **Action**: [Specific, actionable next step - use verbs like "Activate", "Enable", "Schedule demo for"]
- **monday.com Feature**: [Name the specific feature: Automations Center, monday Workforms, Dashboards, monday AI, etc.]
- **Business Impact**: [Connect to money/time saved, e.g., "Reduce support load by ~40%"]
- **Owner**: CSM / CSM & Client / Product / Support (Never assign to "Client" or "Customer" alone - if client involvement needed, use "CSM & Client")

### Recommendation 2: [Title]
...

### Recommendation 3: [Title]
...

## RECOMMENDATION PRIORITIES BY RISK LEVEL

If risk_engine_score > 0.5:
  → Focus on RETENTION: Activate features that solve immediate pain points, schedule urgent success call
  
If risk_engine_score 0.3-0.5:
  → Focus on ENGAGEMENT: Enable underutilized features, demonstrate ROI with Dashboards
  
If risk_engine_score < 0.3:
  → Focus on EXPANSION: Upsell to higher tier, activate advanced features (monday AI, integrations)

## LANGUAGE RULES
- Never say "consider" or "explore" - say "activate" or "enable"
- Never suggest "feasibility studies" - suggest "scheduling a demo" or "piloting"
- Always quantify impact when possible (hours saved, % reduction, cost avoided)
- Be a strategic advisor who creates urgency, not a passive reporter"""


# ============================================================================
# FULL QBR GENERATION PROMPT - Complete Document
# ============================================================================

FULL_QBR_PROMPT = """Generate a complete Quarterly Business Review (QBR) document for the following customer.

## CUSTOMER DATA
| Metric | Value |
|--------|-------|
| Account Name | {account_name} |
| Plan Type | {plan_type} |
| Active Users | {active_users} |
| Usage Growth (QoQ) | {usage_growth_qoq}% |
| Automation Adoption | {automation_adoption_pct}% |
| Support Tickets | {tickets_last_quarter} |
| Tickets Per User | {tickets_per_user:.2f} (lower is better; >0.3 indicates high support burden) |
| Avg Response Time | {avg_response_time}h |
| NPS Score | {nps_score}/10 |
| Preferred Channel | {preferred_channel} |
| Health Score (SCAT) | {scat_score}/100 |
| Churn Risk | {risk_engine_score} |

## QUALITATIVE NOTES
**CRM Notes**: {crm_notes}
**Customer Feedback**: {feedback_summary}

---

## QBR DOCUMENT REQUIREMENTS

Generate the QBR with these sections:

### 📋 EXECUTIVE SUMMARY
- 2-3 sentence overview of the quarter
- Classify as: Growth / Turnaround / Stable / At-Risk story
- Set the tone for the review

### 📈 KEY METRICS & WINS
- Highlight 3-4 positive data points with context
- Connect metrics to business value (time saved, efficiency gained)
- Use specific numbers from the data provided

### ⚠️ CHALLENGES & RISKS
- Honestly address concerning metrics (high tickets, declining usage, etc.)
- Reference specific feedback or CRM notes
- Frame as opportunities for improvement, not failures

### 🎯 STRATEGIC RECOMMENDATIONS
- Provide 3 data-grounded recommendations
- Each should have: What, Why (data signal), and Expected Impact
- Prioritize based on risk level
- **Name specific monday.com features** (Automations Center, monday Workforms, Dashboards, monday AI)
- **Use action language**: "Activate", "Enable", "Schedule demo" - never "consider" or "explore"

### 📅 NEXT STEPS
- 2-3 concrete action items with suggested timeline
- Include who owns each action: CSM, CSM & Client, Product, or Support
- NEVER assign tasks to "Client" or "Customer" alone - if client involvement is needed, use "CSM & Client"
- Be specific: "Schedule 30-min Automations Center walkthrough" not "Discuss automation options"

---

## CRITICAL BUSINESS RULES (MUST CHECK):

⚠️ **MANDATORY UPSELL LOGIC**:
IF Plan = "Basic" AND Tickets > 10 AND Automation < 30%:
→ You MUST recommend upgrading to "Standard" or "Pro" plan as a top recommendation
→ Explain: High ticket volume + low automation = team is doing manual work that the platform could automate
→ This is NOT a training issue - this customer has outgrown Basic plan limitations
→ Do NOT just suggest "training" or "best practices" - recommend the plan upgrade

## MONDAY.COM FEATURE REFERENCES
When recommending solutions, use these specific feature names:
- Workflow automation → "Automations Center"
- Forms/intake → "monday Workforms"  
- AI assistance → "monday AI"
- Reporting → "Dashboards"
- Documentation → "monday Workdocs"
- Integrations → Name specific ones (Slack, Zoom, Salesforce, Jira, etc.)

## STRATEGIC ADVISOR TONE
- Connect metrics to business impact (money, time, risk)
- High tickets = "wasted support costs and frustrated team members"
- Low automation = "hours of manual work that could be automated"
- Create urgency for action, don't just report observations

## FORMATTING RULES
- Use Markdown headers (##, ###)
- Use bullet points for lists
- Include specific numbers and percentages
- Keep total length to ~400-500 words
- Professional but warm tone matching monday.com's brand

## ANTI-HALLUCINATION RULES
- ONLY reference data explicitly provided above
- Do not invent events, conversations, or metrics
- If something is unclear, acknowledge uncertainty
- Cite data points when making claims"""


# ============================================================================
# HELPER FUNCTION - Format Data into Prompts
# ============================================================================

def get_full_qbr_prompt(client_data: Dict[str, Any]) -> str:
    """
    Format client data into the full QBR generation prompt.
    
    Args:
        client_data: Dictionary containing all customer fields
        
    Returns:
        Formatted prompt string ready for LLM consumption
    """
    # Ensure all required fields exist with defaults
    defaults = {
        'account_name': 'Unknown Account',
        'plan_type': 'Unknown',
        'active_users': 0,
        'usage_growth_qoq': 0,
        'automation_adoption_pct': 0,
        'tickets_last_quarter': 0,
        'avg_response_time': 0,
        'nps_score': 0,
        'preferred_channel': 'Email',
        'scat_score': 0,
        'risk_engine_score': 0,
        'crm_notes': 'No notes available.',
        'feedback_summary': 'No feedback recorded.'
    }
    
    # Merge with provided data
    formatted_data = {**defaults, **client_data}
    
    # Calculate tickets per user ratio
    users = formatted_data.get('active_users', 0)
    tickets = formatted_data.get('tickets_last_quarter', 0)
    formatted_data['tickets_per_user'] = tickets / users if users > 0 else 0
    
    # Convert decimal percentages to display percentages
    if isinstance(formatted_data['usage_growth_qoq'], float) and abs(formatted_data['usage_growth_qoq']) <= 1:
        formatted_data['usage_growth_qoq'] = formatted_data['usage_growth_qoq'] * 100
    
    if isinstance(formatted_data['automation_adoption_pct'], float) and formatted_data['automation_adoption_pct'] <= 1:
        formatted_data['automation_adoption_pct'] = formatted_data['automation_adoption_pct'] * 100
    
    return FULL_QBR_PROMPT.format(**formatted_data)


def get_insight_prompt(client_data: Dict[str, Any]) -> str:
    """Format client data into insight extraction prompt."""
    defaults = {
        'account_name': 'Unknown Account',
        'plan_type': 'Unknown',
        'active_users': 0,
        'usage_growth_qoq': 0,
        'automation_adoption_pct': 0,
        'tickets_last_quarter': 0,
        'avg_response_time': 0,
        'nps_score': 0,
        'preferred_channel': 'Email',
        'scat_score': 0,
        'risk_engine_score': 0,
        'crm_notes': 'No notes available.',
        'feedback_summary': 'No feedback recorded.'
    }
    
    formatted_data = {**defaults, **client_data}
    
    # Calculate tickets per user ratio
    users = formatted_data.get('active_users', 0)
    tickets = formatted_data.get('tickets_last_quarter', 0)
    formatted_data['tickets_per_user'] = tickets / users if users > 0 else 0
    
    if isinstance(formatted_data['usage_growth_qoq'], float) and abs(formatted_data['usage_growth_qoq']) <= 1:
        formatted_data['usage_growth_qoq'] = formatted_data['usage_growth_qoq'] * 100
    
    if isinstance(formatted_data['automation_adoption_pct'], float) and formatted_data['automation_adoption_pct'] <= 1:
        formatted_data['automation_adoption_pct'] = formatted_data['automation_adoption_pct'] * 100
    
    return INSIGHT_EXTRACTOR_PROMPT.format(**formatted_data)


def get_recommendation_prompt(client_data: Dict[str, Any]) -> str:
    """Format client data into recommendation engine prompt."""
    defaults = {
        'account_name': 'Unknown Account',
        'plan_type': 'Unknown',
        'active_users': 0,
        'usage_growth_qoq': 0,
        'automation_adoption_pct': 0,
        'tickets_last_quarter': 0,
        'avg_response_time': 0,
        'nps_score': 0,
        'risk_engine_score': 0,
        'crm_notes': 'No notes available.',
        'feedback_summary': 'No feedback recorded.'
    }
    
    formatted_data = {**defaults, **client_data}
    
    # Calculate tickets per user ratio
    users = formatted_data.get('active_users', 0)
    tickets = formatted_data.get('tickets_last_quarter', 0)
    formatted_data['tickets_per_user'] = tickets / users if users > 0 else 0
    
    if isinstance(formatted_data['usage_growth_qoq'], float) and abs(formatted_data['usage_growth_qoq']) <= 1:
        formatted_data['usage_growth_qoq'] = formatted_data['usage_growth_qoq'] * 100
    
    if isinstance(formatted_data['automation_adoption_pct'], float) and formatted_data['automation_adoption_pct'] <= 1:
        formatted_data['automation_adoption_pct'] = formatted_data['automation_adoption_pct'] * 100
    
    return RECOMMENDATION_ENGINE_PROMPT.format(**formatted_data)

