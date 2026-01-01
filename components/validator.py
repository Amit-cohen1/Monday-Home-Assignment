"""
QBR Validator Component

Implements LLM-as-Judge pattern to validate generated QBR quality.
Uses a lightweight model (gpt-4o-mini) to check:
- Data grounding (no hallucinations)
- Feedback coverage (all customer points addressed)
- Critical signal detection (competitor/churn mentions)
- Format compliance (all sections present)
- Tone compliance (no internal formulas exposed)
"""

import json
import re
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


# ============================================================================
# VALIDATION PROMPT
# ============================================================================

VALIDATOR_SYSTEM_PROMPT = """You are a QA validator for Customer Success QBR documents.
Your job is to verify that AI-generated QBRs are accurate, complete, and professional.

You will receive:
1. The original customer data (metrics + qualitative notes)
2. The generated QBR document

You must check for issues and return a structured JSON response."""


VALIDATOR_PROMPT = """Validate the following QBR document against the original customer data.

## ORIGINAL CUSTOMER DATA

<metrics>
- Account Name: {account_name}
- Plan Type: {plan_type}
- Active Users: {active_users}
- Usage Growth (QoQ): {usage_growth_qoq}%
- Automation Adoption: {automation_adoption_pct}%
- Support Tickets: {tickets_last_quarter}
- Avg Response Time: {avg_response_time}h
- NPS Score: {nps_score}/10
- Preferred Channel: {preferred_channel}
- Health Score (SCAT): {scat_score}/100
- Churn Risk: {risk_engine_score}
</metrics>

<qualitative_notes>
CRM Notes: {crm_notes}
Customer Feedback: {feedback_summary}
</qualitative_notes>

## GENERATED QBR

<qbr_document>
{qbr_content}
</qbr_document>

---

## VALIDATION CHECKLIST

Evaluate each category and identify specific issues:

### 1. CRITICAL SIGNAL DETECTION
- Does CRM Notes or Feedback contain: "competitor", "trial", "alternative", "switching", "cancel", "unhappy", "frustrated", "escalation"?
- If YES, is this addressed PROMINENTLY (in first paragraph or first recommendation)?

### 2. FEEDBACK COVERAGE
- List ALL distinct points from CRM Notes
- List ALL distinct points from Customer Feedback
- Is EACH point addressed somewhere in the QBR?

### 3. DATA GROUNDING
- Are all metrics cited in the QBR actually from the provided data?
- Did the QBR invent any events, meetings, conversations, or metrics?

### 4. FORMAT COMPLIANCE
- Does the QBR have: Executive Summary, Key Metrics/Wins, Challenges/Risks, Recommendations, Next Steps?
- Do recommendations have: What, Why, Owner, Timeline?

### 5. TONE COMPLIANCE
- Are there any exposed internal formulas like "Plan = Basic + Tickets > 10"?
- Are comparison operators (>, <, =) used inappropriately?

---

## RESPONSE FORMAT

Return ONLY valid JSON (no markdown, no explanations):

{{
  "validation_passed": true/false,
  "overall_score": 0-100,
  "critical_issues": ["list of blocking issues that require regeneration"],
  "warnings": ["list of non-blocking issues to flag to CSM"],
  "checks": {{
    "critical_signals": {{
      "signals_in_data": ["list of detected signals"],
      "properly_addressed": true/false,
      "issue": "description if not addressed"
    }},
    "feedback_coverage": {{
      "crm_points": ["list of points from CRM Notes"],
      "feedback_points": ["list of points from Feedback"],
      "missed_points": ["list of points not addressed in QBR"],
      "coverage_pct": 0-100
    }},
    "data_grounding": {{
      "hallucinations_detected": ["list of invented facts"],
      "is_grounded": true/false
    }},
    "format_compliance": {{
      "missing_sections": ["list of missing required sections"],
      "is_compliant": true/false
    }},
    "tone_compliance": {{
      "exposed_formulas": ["list of exposed internal logic"],
      "is_compliant": true/false
    }}
  }},
  "improvement_hints": ["specific suggestions for regeneration if needed"]
}}
"""


# ============================================================================
# VALIDATION RESULT DATACLASS
# ============================================================================

@dataclass
class ValidationResult:
    """Structured validation result."""
    passed: bool
    overall_score: int
    critical_issues: List[str]
    warnings: List[str]
    checks: Dict[str, Any]
    improvement_hints: List[str]
    raw_response: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def has_critical_issues(self) -> bool:
        return len(self.critical_issues) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def get_status_emoji(self) -> str:
        if self.passed and not self.has_warnings:
            return "✅"
        elif self.passed and self.has_warnings:
            return "⚠️"
        else:
            return "❌"
    
    def get_status_message(self) -> str:
        if self.passed and not self.has_warnings:
            return "Quality verified"
        elif self.passed and self.has_warnings:
            return f"Passed with {len(self.warnings)} warning(s)"
        else:
            return f"Validation failed: {len(self.critical_issues)} issue(s)"


# ============================================================================
# VALIDATOR CLASS
# ============================================================================

class QBRValidator:
    """
    Validates QBR documents using LLM-as-Judge pattern.
    
    Uses gpt-4o-mini for cost efficiency (~$0.0003 per validation).
    Implements circuit breaker pattern for repeated failures.
    """
    
    MAX_RETRIES = 2  # Maximum regeneration attempts before showing with warnings
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the validator.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for validation (default: gpt-4o-mini for cost efficiency)
        """
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0,  # Deterministic for consistent validation
            max_tokens=2000
        )
    
    def validate(
        self,
        qbr_content: str,
        client_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a generated QBR against the original client data.
        
        Args:
            qbr_content: The generated QBR markdown content
            client_data: Original client data dictionary
            
        Returns:
            ValidationResult with pass/fail status and details
        """
        try:
            # Prepare the validation prompt
            prompt = self._format_validation_prompt(qbr_content, client_data)
            
            # Call the validator LLM
            messages = [
                SystemMessage(content=VALIDATOR_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse the JSON response
            result = self._parse_validation_response(response_text)
            return result
            
        except Exception as e:
            # Return a failed validation with error details
            return ValidationResult(
                passed=False,
                overall_score=0,
                critical_issues=[f"Validation error: {str(e)}"],
                warnings=[],
                checks={},
                improvement_hints=[],
                error=str(e)
            )
    
    def _format_validation_prompt(
        self,
        qbr_content: str,
        client_data: Dict[str, Any]
    ) -> str:
        """Format the validation prompt with data."""
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
        
        formatted_data = {**defaults, **client_data}
        formatted_data['qbr_content'] = qbr_content
        
        # Convert decimal percentages
        if isinstance(formatted_data['usage_growth_qoq'], float) and abs(formatted_data['usage_growth_qoq']) <= 1:
            formatted_data['usage_growth_qoq'] = formatted_data['usage_growth_qoq'] * 100
        
        if isinstance(formatted_data['automation_adoption_pct'], float) and formatted_data['automation_adoption_pct'] <= 1:
            formatted_data['automation_adoption_pct'] = formatted_data['automation_adoption_pct'] * 100
        
        return VALIDATOR_PROMPT.format(**formatted_data)
    
    def _parse_validation_response(self, response_text: str) -> ValidationResult:
        """Parse the LLM's JSON response into a ValidationResult."""
        try:
            # Try to extract JSON from the response
            # Sometimes the LLM wraps it in markdown code blocks
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            return ValidationResult(
                passed=data.get('validation_passed', False),
                overall_score=data.get('overall_score', 0),
                critical_issues=data.get('critical_issues', []),
                warnings=data.get('warnings', []),
                checks=data.get('checks', {}),
                improvement_hints=data.get('improvement_hints', []),
                raw_response=response_text
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                passed=False,
                overall_score=0,
                critical_issues=[f"Failed to parse validation response: {str(e)}"],
                warnings=[],
                checks={},
                improvement_hints=[],
                raw_response=response_text,
                error=str(e)
            )
    
    def get_regeneration_hints(self, validation_result: ValidationResult) -> str:
        """
        Generate hints for the main LLM to improve the QBR on regeneration.
        
        Args:
            validation_result: The failed validation result
            
        Returns:
            String of hints to append to the regeneration prompt
        """
        hints = []
        
        # Add critical issues as priorities
        if validation_result.critical_issues:
            hints.append("CRITICAL - You MUST fix these issues:")
            for issue in validation_result.critical_issues:
                hints.append(f"  - {issue}")
        
        # Add improvement hints from validator
        if validation_result.improvement_hints:
            hints.append("\nImprovement suggestions:")
            for hint in validation_result.improvement_hints:
                hints.append(f"  - {hint}")
        
        # Add specific check failures
        checks = validation_result.checks
        
        if checks.get('critical_signals', {}).get('properly_addressed') == False:
            signals = checks['critical_signals'].get('signals_in_data', [])
            hints.append(f"\n⚠️ CRITICAL: Address these signals PROMINENTLY: {', '.join(signals)}")
        
        if checks.get('feedback_coverage', {}).get('missed_points'):
            missed = checks['feedback_coverage']['missed_points']
            hints.append(f"\n⚠️ MISSED FEEDBACK: Address these points: {', '.join(missed)}")
        
        if checks.get('data_grounding', {}).get('hallucinations_detected'):
            hallucinations = checks['data_grounding']['hallucinations_detected']
            hints.append(f"\n⚠️ REMOVE HALLUCINATIONS: {', '.join(hallucinations)}")
        
        if checks.get('tone_compliance', {}).get('exposed_formulas'):
            formulas = checks['tone_compliance']['exposed_formulas']
            hints.append(f"\n⚠️ REMOVE EXPOSED FORMULAS: {', '.join(formulas)}")
        
        return "\n".join(hints) if hints else ""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_validation_status_html(result: ValidationResult) -> str:
    """
    Format validation result as HTML for Streamlit display.
    
    Args:
        result: ValidationResult object
        
    Returns:
        HTML string for display
    """
    emoji = result.get_status_emoji()
    message = result.get_status_message()
    score = result.overall_score
    
    # Determine color based on status
    if result.passed and not result.has_warnings:
        color = "#00CA72"  # Monday green
        bg_color = "rgba(0, 202, 114, 0.1)"
    elif result.passed:
        color = "#FDAB3D"  # Monday warning
        bg_color = "rgba(253, 171, 61, 0.1)"
    else:
        color = "#E2445C"  # Monday danger
        bg_color = "rgba(226, 68, 92, 0.1)"
    
    html = f"""
    <div style="
        background: {bg_color};
        border: 1px solid {color};
        border-radius: 8px;
        padding: 12px 16px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 1.5rem;">{emoji}</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: {color};">{message}</div>
            <div style="font-size: 0.85rem; color: var(--app-text-secondary);">
                Quality Score: {score}/100
            </div>
        </div>
    </div>
    """
    
    # Add warnings if present
    if result.warnings:
        html += """
        <div style="
            background: rgba(253, 171, 61, 0.05);
            border-left: 3px solid #FDAB3D;
            padding: 10px 15px;
            margin: 5px 0;
            font-size: 0.9rem;
        ">
            <strong>⚠️ Review Recommended:</strong>
            <ul style="margin: 5px 0 0 0; padding-left: 20px;">
        """
        for warning in result.warnings:
            html += f"<li>{warning}</li>"
        html += "</ul></div>"
    
    # Add critical issues if present
    if result.critical_issues:
        html += """
        <div style="
            background: rgba(226, 68, 92, 0.05);
            border-left: 3px solid #E2445C;
            padding: 10px 15px;
            margin: 5px 0;
            font-size: 0.9rem;
        ">
            <strong>❌ Issues Found:</strong>
            <ul style="margin: 5px 0 0 0; padding-left: 20px;">
        """
        for issue in result.critical_issues:
            html += f"<li>{issue}</li>"
        html += "</ul></div>"
    
    return html

