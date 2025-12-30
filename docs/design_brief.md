# Design Brief: QBR Auto-Drafter
## monday.com Innovation Builder Assessment

---

## 1. Problem Framing

### The Challenge
Customer Success Managers (CSMs) at monday.com currently spend **5+ hours per account** preparing Quarterly Business Reviews. This manual process involves:
- Aggregating data from multiple sources (CRM, support tickets, usage metrics)
- Interpreting quantitative metrics alongside qualitative feedback
- Crafting a coherent narrative that drives retention and expansion
- Formatting documents for executive presentation

### Pain Points Identified
1. **Time-intensive**: 5+ hours per QBR means limited coverage of accounts
2. **Inconsistent quality**: Different CSMs produce varying report styles
3. **Missed insights**: Manual analysis may overlook cross-metric patterns
4. **Delayed action**: Lengthy preparation delays intervention for at-risk accounts

---

## 2. User Personas

### Primary User: Customer Success Manager (CSM)
**Profile:**
- Manages 20-50 accounts across different plan tiers
- Prepares 10-20 QBRs per quarter
- Needs data-driven talking points for executive conversations
- Values efficiency without sacrificing quality

**Goals:**
- Reduce QBR preparation time by 80%
- Deliver consistent, professional reports
- Identify risk signals before they escalate
- Find upsell opportunities backed by data

### Secondary User: CS Team Lead
**Profile:**
- Oversees portfolio of 100+ accounts
- Needs visibility into team-wide account health
- Reviews QBRs for quality and accuracy

**Goals:**
- Monitor portfolio risk distribution
- Ensure consistent QBR standards
- Scale team capacity without adding headcount

---

## 3. Success Metrics

### Efficiency Metrics
| Metric | Current State | Target | Measurement |
|--------|---------------|--------|-------------|
| QBR Prep Time | 5+ hours | <30 minutes | Time tracking |
| Accounts Covered | Limited | All accounts | Coverage % |
| CSM Capacity | 10-15 QBRs/quarter | 40+ QBRs/quarter | Volume count |

### Quality Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Data Accuracy | 100% grounded in source data | Audit sampling |
| Insight Relevance | 4.5/5 CSM rating | User feedback |
| Action Clarity | 3+ specific next steps | Content analysis |

### Business Impact Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| At-Risk Detection | 48hr faster identification | Time to intervention |
| Retention Rate | +5% improvement | Renewal tracking |
| Upsell Conversion | +10% from QBR leads | Pipeline attribution |

---

## 4. Design Principles

### 1. Data-First, Not AI-First
The system must **ground all outputs in provided data**. No hallucinated metrics, invented events, or fabricated conversations. If the data doesn't support a claim, the AI shouldn't make it.

### 2. Interpretive, Not Descriptive
Users don't need the AI to list metrics—they can read dashboards. The value is in **interpretation**: "Usage dropped 12% AND tickets spiked AND NPS declined = likely churn risk requiring immediate intervention."

### 3. Action-Oriented
Every QBR must end with **specific, data-grounded recommendations**. Not "improve engagement" but "Schedule automation workshop to address 25% adoption rate—similar accounts saw 40% lift after training."

### 4. Human-in-the-Loop
AI generates drafts; humans refine and deliver. The system supports CSMs, doesn't replace them. Export and editing capabilities are essential.

---

## 5. Key Assumptions

1. **Data Quality**: Source data is accurate and complete. The system trusts CRM notes, usage metrics, and feedback summaries as ground truth.

2. **Model Capabilities**: GPT-4 class models can reliably synthesize structured + unstructured data into coherent business narratives.

3. **User Adoption**: CSMs will adopt AI-generated drafts if they save significant time and maintain quality.

4. **Risk Scoring Validity**: The existing `risk_engine_score` and `scat_score` are validated predictive signals.

---

## 6. Limitations & Scope

### In Scope (This Prototype)
- Single-account QBR generation
- Batch generation for portfolio
- Visual metrics dashboard
- PDF and Markdown export
- Risk-based narrative adaptation

### Out of Scope (Future Iterations)
- Real-time monday.com integration
- Automated email delivery
- Historical trend analysis
- Multi-quarter comparison
- Collaborative editing features
- CRM write-back capabilities

---

## 7. Validation Approach

### Phase 1: Prototype Testing (Current)
- Generate QBRs for 5 sample accounts
- Verify all metrics are correctly referenced
- Confirm recommendations align with risk levels

### Phase 2: User Feedback (Recommended)
- Share with 3-5 CSMs for qualitative feedback
- Measure time savings vs. manual preparation
- Identify missing information or format issues

### Phase 3: A/B Comparison (Future)
- Compare AI-generated vs. manually-written QBRs
- Blind evaluation by CS leadership
- Measure customer response to each type

---

## 8. Technical Approach Summary

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Input    │───▶│   AI Processing  │───▶│     Output      │
│                 │    │                  │    │                 │
│ • Excel/CSV     │    │ • Data Validation│    │ • Visual Charts │
│ • 13 fields     │    │ • Risk Classify  │    │ • QBR Markdown  │
│ • Structured +  │    │ • GPT-4 Analysis │    │ • PDF Export    │
│   Unstructured  │    │ • Structured Out │    │ • Batch Reports │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Technical Decisions
1. **Streamlit**: Rapid prototyping, easy deployment, good for demos
2. **LangChain + OpenAI**: Flexible prompt engineering, structured outputs
3. **Plotly**: Interactive charts matching monday.com's visual standards
4. **Pydantic**: Validated structured outputs to prevent malformed data
5. **fpdf2**: PDF generation with custom branding

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Hallucination** | Structured prompts with explicit data binding; confidence scores |
| **Inconsistent Tone** | System prompt establishing monday.com voice; temperature = 0.3 |
| **Missing Context** | CRM notes and feedback as mandatory input fields |
| **Export Failures** | Fallback to markdown if PDF generation fails |
| **API Costs** | Model selection option (gpt-4o-mini for cost-sensitive users) |

---

## 10. Conclusion

The QBR Auto-Drafter addresses a real pain point for Customer Success teams: the labor-intensive process of preparing quarterly reviews. By combining structured metrics with AI-powered narrative generation, CSMs can:

1. **Save 80%+ of preparation time** while maintaining quality
2. **Ensure consistent, data-grounded reports** across the team
3. **Identify risks faster** through automated signal detection
4. **Scale QBR coverage** to all accounts, not just top-tier

This prototype demonstrates the core value proposition. Next steps would include integration with live monday.com data, collaborative features, and enterprise-grade deployment.

---

*Document prepared for monday.com Innovation Builder Assessment*
*December 2024*

