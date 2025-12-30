# Experiment & Reflection
## QBR Auto-Drafter Development Learnings

---

## 1. What Worked Well

### Structured Output Parsing
The combination of **Pydantic models** with LangChain provided reliable, typed outputs. Rather than parsing free-form markdown, the system generates structured objects (`QBROutput`) that can be:
- Displayed in UI components
- Exported in multiple formats
- Validated automatically

**Key Insight**: Structured outputs reduce downstream errors and enable modular rendering.

### Risk-Based Narrative Adaptation
The **story type classification** (growth/turnaround/stable/at_risk) proved highly effective at adapting tone. The same QBR generator produces:
- Celebratory language for growth accounts
- Urgent, solution-focused language for at-risk accounts
- Strategic expansion suggestions for healthy accounts

This matches how experienced CSMs naturally adjust their communication.

### Visual Dashboard First
Starting with the **visual dashboard** before AI generation was the right order. It:
- Provided immediate value without API costs
- Helped identify which metrics matter most
- Created natural context for AI-generated narratives

### Multi-Stage Prompts (Available but Not Default)
Having separate prompts for insights, recommendations, and full QBR offers flexibility. For complex accounts, CSMs could run a deeper analysis. For routine reviews, the single combined prompt suffices.

---

## 2. What Didn't Work / Challenges

### Initial Prompt Complexity
Early prompts tried to do too much in a single pass:
- Extract insights
- Classify story type
- Generate recommendations
- Format as markdown

**Solution**: Simplified the main prompt, moved complex logic to code (rule-based story classification), and let the LLM focus on narrative generation.

### Percentage Format Inconsistency
The sample data had inconsistent formats:
- `usage_growth_qoq`: decimal (0.16 = 16%)
- Some fields appeared as integers

**Solution**: Added normalization logic in the generator to detect and convert formats.

### PDF Generation Complexity
The fpdf2 library has limitations:
- No native markdown parsing
- Limited font support
- Complex positioning

**Solution**: Created a custom `MondayPDF` class with helper methods for consistent styling. Future: Consider using WeasyPrint or ReportLab for richer PDFs.

### Emoji Handling in PDFs
Markdown output includes emojis (📊, 🚀) that don't render in basic PDF fonts.

**Solution**: Strip emojis during PDF export with regex. Acceptable tradeoff for prototype.

---

## 3. Measuring Success

### Proposed Evaluation Metrics

| Metric | How to Measure | Target |
|--------|----------------|--------|
| **Factual Accuracy** | Manual audit: Do all cited metrics match source data? | 100% |
| **Insight Relevance** | CSM rating: "Was this insight actionable?" (1-5) | ≥4.0 |
| **Time Savings** | Compare prep time with/without tool | 80% reduction |
| **Coverage Quality** | Are all key metrics addressed? (checklist) | All fields |
| **Recommendation Specificity** | Are actions concrete, not generic? (human eval) | ≥3 specific actions |

### A/B Test Design (Future)
1. Select 10 accounts randomly
2. Generate AI QBRs for 5, manual QBRs for 5
3. Blind evaluation by CS leadership
4. Score on: completeness, insight quality, actionability
5. Track 90-day customer outcomes (optional)

### Automated Quality Checks
- **Hallucination Detection**: Cross-reference generated numbers against source data
- **Completeness Score**: Verify all required sections present
- **Sentiment Alignment**: Check narrative tone matches risk level

---

## 4. Next Steps / Future Improvements

### High Priority

#### 1. monday.com Integration
Connect directly to monday.com's API to pull:
- Board data as structured metrics
- Automation recipes as adoption signals
- Activity logs as engagement indicators

```python
# Conceptual integration
from monday import MondayClient

client = MondayClient(api_key)
account_data = client.get_account_metrics(account_id)
qbr = generator.generate_structured_qbr(account_data)
```

#### 2. Historical Trend Analysis
Add quarter-over-quarter comparison:
- "NPS improved from 6.2 to 7.8 this quarter"
- "Risk score trending downward over 3 quarters"
- Visualize trajectory, not just snapshots

#### 3. Collaborative Editing
After AI generates draft:
- CSM can edit in-app
- Changes tracked and versioned
- Final version saved to monday Docs

### Medium Priority

#### 4. Multi-Language Support
Internationalize QBR generation:
- Prompt templates in multiple languages
- PDF generation with proper fonts
- Date/number formatting localization

#### 5. Custom Template Builder
Let CS teams define their own QBR structure:
- Drag-and-drop section ordering
- Custom prompt snippets
- Brand-specific language

#### 6. Email Integration
Auto-generate follow-up emails:
- Risk mitigation outreach
- Upsell opportunity emails
- Scheduled delivery via Outreach/Salesloft

### Exploratory

#### 7. Voice Summary
Generate audio version of QBR summary:
- CSM can listen during commute
- Embedded in mobile app
- Quick refresh before customer call

#### 8. Predictive Recommendations
Use ML to recommend actions based on similar accounts:
- "Accounts like this responded well to automation training"
- "Consider executive business review based on growth pattern"

---

## 5. Technical Debt & Refactoring

### Current Technical Debt
1. **Inline CSS**: Move all CSS to external file with Streamlit's new theme system
2. **Session State**: Implement proper state management pattern
3. **Error Handling**: Add comprehensive try/except with user-friendly messages
4. **Type Hints**: Complete type annotations throughout codebase
5. **Testing**: Add unit tests for data transformation and prompt formatting

### Refactoring Priorities
1. Extract color/theme constants to single config file
2. Create abstract base class for exporters
3. Implement caching layer for repeated QBR requests
4. Add logging for debugging and monitoring

---

## 6. Key Learnings

### On AI/LLM Development
1. **Grounding is everything**: The difference between useful AI and "AI slop" is data grounding
2. **Temperature matters**: 0.3 produces consistent business writing; 0.7+ gets creative but unpredictable
3. **Structured outputs scale**: Pydantic models pay dividends in maintainability
4. **Prompts are code**: Treat them with the same rigor (version control, testing, review)

### On Product Development
1. **Start with the dashboard**: Visualizations provide immediate value and inform AI design
2. **Export is not optional**: Real users need to take outputs elsewhere (email, slides, docs)
3. **Risk-based UX**: UI should adapt to data signals (red badges, urgent language)
4. **Sample data is gold**: Well-designed test data reveals edge cases early

### On monday.com Context
1. **CSMs need speed, not polish**: A good-enough draft in 5 minutes beats a perfect one in 5 hours
2. **Risk detection is the killer feature**: Early warning beats better reporting
3. **Integration is the endgame**: Standalone tools die; platform-connected tools thrive

---

## 7. Conclusion

The QBR Auto-Drafter prototype successfully demonstrates:

✅ **AI-powered narrative generation** that respects data boundaries  
✅ **Visual dashboards** with monday.com branding  
✅ **Risk-aware adaptation** of tone and recommendations  
✅ **Working exports** to PDF and Markdown  
✅ **Batch processing** for portfolio-wide generation  

The path forward involves deeper monday.com integration, historical analysis, and collaborative workflows. But the core value proposition—**transforming hours of prep into minutes of review**—is validated.

---

*Reflection Document - QBR Auto-Drafter*
*monday.com Innovation Builder Assessment*
*December 2024*

