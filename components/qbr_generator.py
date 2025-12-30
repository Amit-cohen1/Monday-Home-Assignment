"""
QBR Generator Component - AI-Powered Quarterly Business Review Generation

This module handles:
1. LangChain integration with OpenAI GPT-4
2. Structured output parsing using Pydantic models
3. Multi-stage prompt execution (insights → narrative → recommendations)
4. Hallucination mitigation through data grounding
"""

import json
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.qbr_prompts import (
    SYSTEM_PROMPT,
    get_full_qbr_prompt,
    get_insight_prompt,
    get_recommendation_prompt
)


# ============================================================================
# PYDANTIC MODELS - Structured Output Schemas
# ============================================================================

class MetricHighlight(BaseModel):
    """A highlighted metric with context"""
    metric_name: str = Field(description="Name of the metric")
    value: str = Field(description="The metric value with units")
    interpretation: str = Field(description="What this metric means for the customer")
    sentiment: Literal["positive", "neutral", "negative"] = Field(description="Overall sentiment")


class RiskItem(BaseModel):
    """An identified risk or challenge"""
    risk_title: str = Field(description="Brief title of the risk")
    description: str = Field(description="Detailed description of the risk")
    severity: Literal["low", "medium", "high"] = Field(description="Risk severity level")
    data_signal: str = Field(description="The specific data point that indicates this risk")


class ActionItem(BaseModel):
    """A recommended action item"""
    action_title: str = Field(description="Brief title of the action")
    description: str = Field(description="Detailed description of what to do")
    rationale: str = Field(description="Why this action is recommended based on data")
    owner: Literal["CSM", "Customer", "Product", "Support"] = Field(description="Who owns this action")
    priority: Literal["immediate", "short-term", "long-term"] = Field(description="When to execute")


class QBROutput(BaseModel):
    """Complete structured QBR output"""
    account_name: str = Field(description="Customer account name")
    executive_summary: str = Field(description="2-3 sentence executive summary")
    story_type: Literal["growth", "turnaround", "stable", "at_risk"] = Field(
        description="The narrative arc classification"
    )
    key_metrics: List[MetricHighlight] = Field(description="3-4 highlighted metrics")
    risks: List[RiskItem] = Field(description="Identified risks and challenges")
    recommendations: List[ActionItem] = Field(description="Strategic recommendations")
    next_steps: List[str] = Field(description="Concrete next steps with timeline")
    confidence_score: float = Field(
        description="Model's confidence in the analysis (0-1)",
        ge=0,
        le=1
    )
    raw_markdown: str = Field(description="Full QBR in markdown format")


# ============================================================================
# QBR GENERATOR CLASS
# ============================================================================

class QBRGenerator:
    """
    AI-powered QBR generator using LangChain and OpenAI.
    
    Features:
    - Configurable model and temperature
    - Structured output parsing
    - Multi-stage generation pipeline
    - Error handling and fallbacks
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.3
    ):
        """
        Initialize the QBR generator.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o)
            temperature: Generation temperature (0.2-0.4 recommended for consistency)
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        self.model = model
        self.temperature = temperature
    
    def generate_qbr_markdown(self, client_data: Dict[str, Any]) -> str:
        """
        Generate a complete QBR in markdown format.
        
        Args:
            client_data: Dictionary containing all customer data fields
            
        Returns:
            Complete QBR document in markdown format
        """
        prompt = get_full_qbr_prompt(client_data)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_insights(self, client_data: Dict[str, Any]) -> str:
        """
        Generate insights analysis for a customer.
        
        Args:
            client_data: Dictionary containing all customer data fields
            
        Returns:
            Insights analysis in markdown format
        """
        prompt = get_insight_prompt(client_data)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_recommendations(self, client_data: Dict[str, Any]) -> str:
        """
        Generate strategic recommendations for a customer.
        
        Args:
            client_data: Dictionary containing all customer data fields
            
        Returns:
            Recommendations in markdown format
        """
        prompt = get_recommendation_prompt(client_data)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def classify_story_type(self, client_data: Dict[str, Any]) -> str:
        """
        Classify the account's story arc based on metrics.
        
        Uses rule-based logic for consistency (no LLM needed).
        
        Args:
            client_data: Dictionary containing customer data
            
        Returns:
            Story type: "growth", "turnaround", "stable", or "at_risk"
        """
        risk = client_data.get('risk_engine_score', 0.5)
        growth = client_data.get('usage_growth_qoq', 0)
        automation = client_data.get('automation_adoption_pct', 0)
        nps = client_data.get('nps_score', 5)
        scat = client_data.get('scat_score', 50)
        
        # Ensure growth is in decimal form
        if isinstance(growth, (int, float)) and abs(growth) > 1:
            growth = growth / 100
        
        # Ensure automation is in decimal form
        if isinstance(automation, (int, float)) and automation > 1:
            automation = automation / 100
        
        # Classification logic
        if risk >= 0.5 or growth < -0.1 or nps < 6:
            return "at_risk"
        elif risk < 0.3 and growth > 0.1 and automation > 0.5 and nps > 7:
            return "growth"
        elif scat < 60 and growth > 0:
            return "turnaround"
        else:
            return "stable"
    
    def generate_structured_qbr(self, client_data: Dict[str, Any]) -> QBROutput:
        """
        Generate a fully structured QBR with Pydantic validation.
        
        This is the main generation method that produces a complete,
        validated QBR output object.
        
        Args:
            client_data: Dictionary containing all customer data fields
            
        Returns:
            QBROutput object with all structured fields
        """
        # Generate the raw markdown QBR
        raw_markdown = self.generate_qbr_markdown(client_data)
        
        # Classify story type (rule-based for consistency)
        story_type = self.classify_story_type(client_data)
        
        # Extract key metrics from data
        key_metrics = self._extract_metrics(client_data)
        
        # Identify risks from data
        risks = self._identify_risks(client_data)
        
        # Generate recommendations
        recommendations = self._build_recommendations(client_data)
        
        # Build next steps
        next_steps = self._build_next_steps(client_data, story_type)
        
        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(client_data)
        
        # Extract executive summary from markdown (first paragraph after header)
        exec_summary = self._extract_summary(raw_markdown, client_data)
        
        return QBROutput(
            account_name=client_data.get('account_name', 'Unknown'),
            executive_summary=exec_summary,
            story_type=story_type,
            key_metrics=key_metrics,
            risks=risks,
            recommendations=recommendations,
            next_steps=next_steps,
            confidence_score=confidence,
            raw_markdown=raw_markdown
        )
    
    def _extract_metrics(self, client_data: Dict[str, Any]) -> List[MetricHighlight]:
        """Extract and interpret key metrics from client data."""
        metrics = []
        
        # Usage Growth
        growth = client_data.get('usage_growth_qoq', 0)
        if isinstance(growth, float) and abs(growth) <= 1:
            growth_pct = growth * 100
        else:
            growth_pct = growth
        
        metrics.append(MetricHighlight(
            metric_name="Usage Growth (QoQ)",
            value=f"{growth_pct:+.1f}%",
            interpretation="Strong expansion" if growth_pct > 10 else "Declining usage" if growth_pct < -5 else "Stable usage",
            sentiment="positive" if growth_pct > 5 else "negative" if growth_pct < -5 else "neutral"
        ))
        
        # Automation Adoption
        automation = client_data.get('automation_adoption_pct', 0)
        if isinstance(automation, float) and automation <= 1:
            automation_pct = automation * 100
        else:
            automation_pct = automation
        
        metrics.append(MetricHighlight(
            metric_name="Automation Adoption",
            value=f"{automation_pct:.0f}%",
            interpretation="Power user" if automation_pct > 60 else "Growth opportunity" if automation_pct < 30 else "Moderate adoption",
            sentiment="positive" if automation_pct > 50 else "negative" if automation_pct < 20 else "neutral"
        ))
        
        # NPS Score
        nps = client_data.get('nps_score', 0)
        metrics.append(MetricHighlight(
            metric_name="NPS Score",
            value=f"{nps}/10",
            interpretation="Promoter" if nps >= 8 else "Detractor" if nps < 6 else "Passive",
            sentiment="positive" if nps >= 8 else "negative" if nps < 6 else "neutral"
        ))
        
        # Active Users
        users = client_data.get('active_users', 0)
        plan = client_data.get('plan_type', 'Unknown')
        metrics.append(MetricHighlight(
            metric_name="Active Users",
            value=f"{users:,}",
            interpretation=f"{plan} tier with {'strong' if users > 100 else 'moderate' if users > 30 else 'small'} footprint",
            sentiment="positive" if users > 50 else "neutral"
        ))
        
        return metrics
    
    def _identify_risks(self, client_data: Dict[str, Any]) -> List[RiskItem]:
        """Identify risks based on data thresholds."""
        risks = []
        
        # High churn risk
        risk_score = client_data.get('risk_engine_score', 0)
        if risk_score >= 0.5:
            risks.append(RiskItem(
                risk_title="Elevated Churn Risk",
                description=f"AI risk engine predicts {risk_score*100:.0f}% churn probability",
                severity="high" if risk_score >= 0.7 else "medium",
                data_signal=f"risk_engine_score = {risk_score}"
            ))
        
        # High ticket volume
        tickets = client_data.get('tickets_last_quarter', 0)
        if tickets > 50:
            risks.append(RiskItem(
                risk_title="High Support Volume",
                description=f"{tickets} support tickets indicates friction or product issues",
                severity="high" if tickets > 80 else "medium",
                data_signal=f"tickets_last_quarter = {tickets}"
            ))
        
        # Negative growth
        growth = client_data.get('usage_growth_qoq', 0)
        if isinstance(growth, float) and abs(growth) <= 1:
            growth = growth * 100
        if growth < -5:
            risks.append(RiskItem(
                risk_title="Usage Decline",
                description=f"Quarter-over-quarter usage dropped {abs(growth):.1f}%",
                severity="high" if growth < -15 else "medium",
                data_signal=f"usage_growth_qoq = {growth}%"
            ))
        
        # Low NPS
        nps = client_data.get('nps_score', 0)
        if nps < 6:
            risks.append(RiskItem(
                risk_title="Customer Dissatisfaction",
                description=f"NPS score of {nps}/10 indicates detractor status",
                severity="high" if nps < 5 else "medium",
                data_signal=f"nps_score = {nps}"
            ))
        
        # Check feedback for negative signals
        feedback = client_data.get('feedback_summary', '').lower()
        if any(word in feedback for word in ['competitor', 'leaving', 'cancel', 'frustrated']):
            risks.append(RiskItem(
                risk_title="Competitive Threat",
                description="Customer feedback mentions competitor evaluation or frustration",
                severity="high",
                data_signal="feedback_summary contains risk keywords"
            ))
        
        return risks
    
    def _build_recommendations(self, client_data: Dict[str, Any]) -> List[ActionItem]:
        """Build data-grounded recommendations."""
        recommendations = []
        risk_score = client_data.get('risk_engine_score', 0)
        
        # High risk: focus on retention
        if risk_score >= 0.5:
            recommendations.append(ActionItem(
                action_title="Executive Escalation Call",
                description="Schedule urgent call with customer stakeholders to address concerns",
                rationale=f"Risk score of {risk_score:.0%} requires immediate intervention",
                owner="CSM",
                priority="immediate"
            ))
        
        # Low automation: training opportunity
        automation = client_data.get('automation_adoption_pct', 0)
        if isinstance(automation, float) and automation <= 1:
            automation = automation * 100
        if automation < 40:
            recommendations.append(ActionItem(
                action_title="Automation Workshop",
                description="Host hands-on session showcasing automation recipes and templates",
                rationale=f"Only {automation:.0f}% automation adoption - significant value unlock available",
                owner="CSM",
                priority="short-term"
            ))
        
        # Check feedback for feature requests
        feedback = client_data.get('feedback_summary', '')
        if 'integration' in feedback.lower() or 'connect' in feedback.lower():
            recommendations.append(ActionItem(
                action_title="Integration Deep-Dive",
                description="Review integration requirements and demonstrate available connectors",
                rationale="Customer explicitly mentioned integration needs in feedback",
                owner="CSM",
                priority="short-term"
            ))
        
        # High NPS: expansion opportunity
        nps = client_data.get('nps_score', 0)
        if nps >= 8 and risk_score < 0.3:
            recommendations.append(ActionItem(
                action_title="Expansion Discussion",
                description="Explore additional use cases and team rollout opportunities",
                rationale=f"NPS of {nps}/10 and low risk indicates upsell readiness",
                owner="CSM",
                priority="short-term"
            ))
        
        # High tickets: support review
        tickets = client_data.get('tickets_last_quarter', 0)
        if tickets > 40:
            recommendations.append(ActionItem(
                action_title="Support Ticket Review",
                description="Analyze ticket patterns and address root causes with product/support",
                rationale=f"{tickets} tickets last quarter indicates systemic issues",
                owner="Support",
                priority="immediate" if tickets > 70 else "short-term"
            ))
        
        # Ensure at least 3 recommendations
        if len(recommendations) < 3:
            recommendations.append(ActionItem(
                action_title="Quarterly Success Review",
                description="Document wins, gather feedback, and align on next quarter goals",
                rationale="Standard QBR follow-up to maintain relationship momentum",
                owner="CSM",
                priority="short-term"
            ))
        
        return recommendations[:3]  # Return top 3
    
    def _build_next_steps(self, client_data: Dict[str, Any], story_type: str) -> List[str]:
        """Build concrete next steps based on story type."""
        account = client_data.get('account_name', 'Customer')
        channel = client_data.get('preferred_channel', 'Email')
        
        if story_type == "at_risk":
            return [
                f"Schedule urgent call with {account} stakeholders within 48 hours",
                f"Prepare risk mitigation plan addressing top concerns",
                f"Loop in account executive and support lead for escalation"
            ]
        elif story_type == "growth":
            return [
                f"Send executive summary via {channel} highlighting wins",
                f"Schedule expansion discussion for next 2 weeks",
                f"Identify case study opportunity with marketing team"
            ]
        elif story_type == "turnaround":
            return [
                f"Document recovery progress and share with stakeholders",
                f"Schedule check-in call to reinforce positive momentum",
                f"Identify additional success metrics to track"
            ]
        else:  # stable
            return [
                f"Send QBR summary via {channel}",
                f"Schedule routine check-in for next month",
                f"Explore one new feature or use case to drive engagement"
            ]
    
    def _calculate_confidence(self, client_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness."""
        required_fields = [
            'account_name', 'plan_type', 'active_users', 'usage_growth_qoq',
            'automation_adoption_pct', 'tickets_last_quarter', 'nps_score',
            'risk_engine_score', 'crm_notes', 'feedback_summary'
        ]
        
        present = sum(1 for f in required_fields if client_data.get(f) is not None)
        completeness = present / len(required_fields)
        
        # Adjust for quality of qualitative data
        crm_notes = client_data.get('crm_notes', '')
        feedback = client_data.get('feedback_summary', '')
        
        quality_bonus = 0
        if len(crm_notes) > 50:
            quality_bonus += 0.05
        if len(feedback) > 30:
            quality_bonus += 0.05
        
        return min(1.0, completeness * 0.9 + quality_bonus)
    
    def _extract_summary(self, markdown: str, client_data: Dict[str, Any]) -> str:
        """Extract or generate executive summary."""
        # Try to find summary in markdown
        lines = markdown.split('\n')
        in_summary = False
        summary_lines = []
        
        for line in lines:
            if 'executive summary' in line.lower() or 'summary' in line.lower():
                in_summary = True
                continue
            if in_summary:
                if line.startswith('#') or line.startswith('##'):
                    break
                if line.strip():
                    summary_lines.append(line.strip())
                if len(summary_lines) >= 2:
                    break
        
        if summary_lines:
            return ' '.join(summary_lines)
        
        # Fallback: generate from data
        account = client_data.get('account_name', 'This account')
        story = self.classify_story_type(client_data)
        growth = client_data.get('usage_growth_qoq', 0)
        if isinstance(growth, float) and abs(growth) <= 1:
            growth = growth * 100
        
        story_descriptions = {
            'growth': f'{account} had an excellent quarter with {growth:+.0f}% usage growth and strong platform adoption.',
            'turnaround': f'{account} shows signs of recovery after previous challenges, with improving engagement metrics.',
            'stable': f'{account} maintained consistent usage this quarter with opportunities for deeper engagement.',
            'at_risk': f'{account} requires immediate attention due to declining metrics and elevated churn signals.'
        }
        
        return story_descriptions.get(story, f'{account} completed Q3 with mixed results requiring strategic focus.')

