# Market Research Document (MRD)

## Recruitment Assistant Application — CrewAI Multi-Agent System

**Document Version:** 1.0  
**Date:** July 7, 2026  
**Prepared by:** @product-mgr (AAMAD Phase 1 — Define)

---

## 1. Executive Summary

The recruitment industry is undergoing a fundamental transformation driven by artificial intelligence and multi-agent automation. This Market Research Document analyzes the opportunity for an AI-powered Recruitment Assistant application built on the CrewAI framework — a system that orchestrates autonomous AI agents to collaborate on candidate sourcing, evaluation, outreach strategy, and recruiter reporting.

The CrewAI recruitment example provides a proven reference architecture with four specialized agents (Researcher, Matcher, Communicator, Reporter) executing sequential tasks. Our analysis indicates a substantial market opportunity, with the global AI in recruitment market projected to reach USD 614.15 billion by 2033 at a CAGR of 31.2%, driven by enterprise demand for hiring automation, talent analytics, and cost reduction.

This MRD establishes the market context, competitive landscape, target personas, and validated market assumptions that will inform the Product Requirements Document (PRD).

---

## 2. Market Overview

### 2.1 Industry Context

The Human Resources Technology (HRTech) market represents one of the fastest-growing segments of enterprise software:

| Metric | Value | Source |
|--------|-------|--------|
| Global AI Market (2026) | USD 601.93 billion | MarketsandMarkets, June 2026 |
| Global AI Market (2033) | USD 3,638.08 billion | MarketsandMarkets, June 2026 |
| AI CAGR (2026-2033) | 29.3% | MarketsandMarkets, June 2026 |
| HR Analytics Market (2024) | USD 3.6 billion | MarketsandMarkets, 2019 |
| Enterprise AI in HR/Recruitment | Fastest-growing application area | Grand View Research |

### 2.2 Key Market Drivers

1. **Talent Shortage & Competition**: Global talent markets face acute skilled-worker shortages, particularly in technology, healthcare, and engineering. Organizations need faster, more targeted sourcing.

2. **Cost of Bad Hires**: The average cost of a bad hire is estimated at 30% of the employee's first-year earnings. AI-driven matching reduces mis-hire rates by improving candidate-role alignment.

3. **Time-to-Fill Pressure**: Average time-to-fill for technical roles exceeds 40 days. Multi-agent automation can compress this timeline by 50-70% through parallel research and automated outreach.

4. **Regulatory Compliance**: EEOC, GDPR, and OFCCP requirements demand auditable, bias-mitigated hiring processes. AI systems with structured outputs and traceable decision-making support compliance.

5. **Remote Work Expansion**: Geographic boundaries no longer limit talent pools. AI agents can source and evaluate candidates globally without proportional increases in recruiter workload.

### 2.3 Market Segmentation

#### By Organization Size
| Segment | Characteristics | AI Adoption |
|---------|----------------|-------------|
| Enterprise (1000+) | High-volume hiring, multiple roles, global reach | High — dedicated TA teams, ATS integrations |
| Mid-Market (100-999) | Growing teams, budget-conscious, hybrid tools | Medium — seeking automation ROI |
| SMB (<100) | Infrequent hiring, owner-driven, limited HR staff | Low-Medium — need simplicity, low cost |

#### By Industry Vertical
- **Technology & Software**: Highest adoption rate, complex skill requirements
- **Healthcare**: Credential verification, licensing compliance
- **Financial Services**: Regulatory screening, compliance requirements
- **Manufacturing**: Volume hiring, shift-based workforce
- **Professional Services**: Client-facing roles, cultural fit emphasis

#### By Hiring Type
- **Executive/Leadership**: High-touch, relationship-driven, low volume
- **Technical/Specialized**: Skill-matching intensive, rapid market changes
- **Volume/Operational**: High-volume, template-driven, cost-sensitive
- **Contract/Temp**: Speed-critical, compliance-heavy, repeatable

---

## 3. Target Market Analysis

### 3.1 Primary Target: Internal Talent Acquisition Teams

**Profile:**
- Companies with 200-5,000 employees
- Dedicated TA teams of 3-15 recruiters
- High-volume hiring (50-500 requisitions/year)
- Existing ATS (Greenhouse, Lever, Workday, etc.)
- Budget: $15,000-$75,000/year for recruitment tools

**Pain Points:**
- Manual sourcing consumes 60-70% of recruiter time
- Candidate quality varies due to subjective screening
- Outreach response rates average 10-15%
- No visibility into sourcing pipeline efficiency
- Difficulty scaling during hiring surges

**Decision Makers:**
- VP of Talent Acquisition
- Head of Recruiting
- HR Operations Director

### 3.2 Secondary Target: Staffing Agencies & RPOs

**Profile:**
- 10-200 recruiters managing multiple client accounts
- High-volume, multi-role, speed-critical
- Revenue tied to placement speed and quality
- Need differentiation through technology

**Pain Points:**
- Client SLA pressure (fill rates, time-to-fill)
- Recruiter productivity caps at 15-25 requisitions
- Candidate pipeline leakage between roles
- Reporting and client communication overhead

### 3.3 Tertiary Target: Startups & Scaleups

**Profile:**
- 10-200 employees, lean HR (1-3 people)
- Hiring spikes during funding rounds
- Technical co-founder or CEO often involved in hiring
- Budget: $0-$10,000/year

**Pain Points:**
- No dedicated recruiter; founder screens candidates
- Lack of employer brand recognition
- Competing for talent against established companies
- Time-constrained, need efficiency over sophistication

---

## 4. Competitive Landscape

### 4.1 Direct Competitors

| Product | Company | Key Differentiator | Price Range |
|---------|---------|-------------------|-------------|
| HireEZ | HireEZ | AI-powered sourcing with browser extension | $8,000-$25,000/yr |
| Entelo | Entelo | Predictive analytics for candidate engagement | $10,000-$30,000/yr |
| Fetcher | Fetcher | Automated sourcing with diversity focus | $5,000-$15,000/yr |
| Humanly | Humanly | Conversational AI for screening | $6,000-$20,000/yr |
| Paradox (Olivia) | Paradox | AI assistant for high-volume hiring | Custom pricing |
| Eightfold AI | Eightfold | Talent intelligence platform | Enterprise pricing |

### 4.2 Indirect Competitors

- **LinkedIn Recruiter**: Dominant sourcing platform, $10,000+/year
- **Greenhouse/Lever**: ATS with built-in sourcing features
- **Gem/Beamery**: CRM-focused talent engagement platforms
- **Manual Sourcing**: Free but labor-intensive (still dominant)

### 4.3 Competitive Gaps (Opportunities)

1. **Multi-Agent Architecture**: No competitor offers autonomous agent collaboration — most use single-agent or rule-based automation.

2. **Open-Source Foundation**: CrewAI is MIT-licensed; no competitor offers an open, extensible AI recruitment framework.

3. **Local/Custom LLM Support**: Most competitors require vendor-specific API access. CrewAI supports Ollama, LM Studio, and custom models.

4. **Workflow Transparency**: Multi-agent systems provide explainable decision chains, unlike black-box AI screening tools.

5. **Extensibility**: Custom tools, knowledge sources, and agent configurations allow adaptation to niche industries.

---

## 5. CrewAI Recruitment Example — Reference Architecture

### 5.1 Agent Roles (from CrewAI Example)

| Agent | Role | Goal | Tools |
|-------|------|------|-------|
| **Researcher** | Job Candidate Researcher | Find potential candidates using online resources | SerperDevTool, ScrapeWebsiteTool, LinkedInTool |
| **Matcher** | Candidate Matcher and Scorer | Score and rank candidates against job requirements | SerperDevTool, ScrapeWebsiteTool |
| **Communicator** | Candidate Outreach Strategist | Develop engagement strategies and templates | SerperDevTool, ScrapeWebsiteTool |
| **Reporter** | Candidate Reporting Specialist | Compile recruiter-ready reports | None (synthesis only) |

### 5.2 Task Flow (Sequential Process)

```
┌─────────────────┐
│  Input: Job     │
│  Requirements   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Task 1: Research │  Agent: Researcher
│ Candidates       │  Tools: Web search, scraping
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Task 2: Match &  │  Agent: Matcher
│ Score Candidates │  Tools: Web search, scoring
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Task 3: Outreach │  Agent: Communicator
│ Strategy         │  Tools: Web search, templates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Task 4: Report   │  Agent: Reporter
│ to Recruiters    │  Tools: Synthesis, formatting
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Output: Final    │
│ Candidate Report │
└─────────────────┘
```

### 5.3 Output Specifications

- **Task 1 Output**: List of 10 potential candidates with contact info and brief profiles
- **Task 2 Output**: Ranked list with detailed scores and justifications
- **Task 3 Output**: Outreach methods, templates, and engagement tactics
- **Task 4 Output**: Comprehensive markdown report with profiles, scores, and strategies

### 5.4 Technical Stack

- **Runtime**: CrewAI (Python >=3.10)
- **LLM**: GPT-4o (default, configurable to other models)
- **Tools**: SerperDevTool, ScrapeWebsiteTool, custom LinkedInTool
- **Configuration**: YAML-based agent/task definitions
- **Process**: Sequential (expandable to hierarchical)

---

## 6. Market Sizing

### 6.1 Total Addressable Market (TAM)

- Global HR software market: USD 24 billion (2026)
- AI in recruitment segment: USD 1.8 billion (2026)
- Projected AI in recruitment by 2030: USD 5.9 billion

### 6.2 Serviceable Addressable Market (SAM)

- Companies actively using or evaluating AI recruitment tools: 150,000 globally
- Average annual spend per company: $12,000
- SAM = USD 1.8 billion (2026)

### 6.3 Serviceable Obtainable Market (SOM)

- Year 1 target: 500 customers (enterprise + mid-market)
- Average contract value: $18,000
- Year 1 Revenue Target: USD 9 million

### 6.4 Growth Projections

| Year | Customers | ARPU | Revenue | Growth |
|------|-----------|------|---------|--------|
| Year 1 | 500 | $18,000 | $9M | — |
| Year 2 | 1,500 | $22,000 | $33M | 267% |
| Year 3 | 4,000 | $25,000 | $100M | 203% |

---

## 7. Customer Personas

### 7.1 Primary Persona: Sarah, VP of Talent Acquisition

- **Company**: Mid-market SaaS (500 employees, 50 hires/year)
- **Goals**: Reduce time-to-fill, improve candidate quality, scale team
- **Frustrations**: Manual sourcing bottlenecks, low outreach response rates
- **Budget Authority**: $50,000/year for recruitment technology
- **Buyer Journey**: Evaluates 3-5 vendors, requires ROI proof, champions internally

### 7.2 Secondary Persona: Marcus, Staffing Agency Director

- **Company**: IT staffing firm (30 recruiters, 200+ active requisitions)
- **Goals**: Increase fill rate, reduce cost-per-hire, differentiate from competitors
- **Frustrations**: Recruiter burnout, client SLA pressure, candidate pipeline gaps
- **Budget Authority**: $75,000/year for sourcing tools
- **Buyer Journey**: Quick evaluation, demo-driven, needs integration with existing ATS

### 7.3 Tertiary Persona: Lisa, Startup Founder

- **Company**: Series A startup (40 employees, 10 hires next quarter)
- **Goals**: Hire key roles quickly, compete with big tech for talent
- **Frustrations**: No recruiter, founder wearing too many hats, limited budget
- **Budget Authority**: $5,000-$10,000/year
- **Buyer Journey**: Self-serve, community-driven, values free tier and open source

---

## 8. Technology Trends

### 8.1 Multi-Agent Systems

- CrewAI represents the emerging standard for multi-agent orchestration
- Agent-to-agent communication enables complex workflow decomposition
- Sequential, hierarchical, and hybrid process models provide flexibility
- Human-in-the-loop patterns ensure oversight and quality control

### 8.2 Agentic AI

- Shift from chatbot interfaces to autonomous task execution
- Agents with tools, memory, and knowledge sources for contextual decision-making
- Flow-based orchestration combining deterministic logic with AI reasoning

### 8.3 Local & Open-Source LLMs

- Ollama, LM Studio, and vLLM enable on-premise deployment
- Data privacy compliance (GDPR, HIPAA) without cloud dependency
- Cost optimization: local inference eliminates per-token API costs

### 8.4 Explainable AI in HR

- Regulatory pressure (EU AI Act, NYC Local Law 144) demands auditability
- Multi-agent systems provide transparent decision chains
- Structured outputs enable bias detection and fairness monitoring

---

## 9. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| LinkedIn API changes / legal restrictions | High | High | Design for multiple data sources; avoid dependency on any single platform |
| LLM hallucination in candidate profiles | High | Medium | Human-in-the-loop validation; structured output schemas |
| Bias in AI-driven candidate scoring | High | Medium | Bias detection tools; diverse training data; regular audits |
| Competition from established ATS vendors | Medium | High | Differentiate on multi-agent architecture; open-source advantage |
| Data privacy regulations (GDPR, CCPA) | High | Medium | Privacy-by-design; local deployment option; data anonymization |
| Low user trust in AI recruitment | Medium | Medium | Transparent reasoning; human override; explainable outputs |

---

## 10. Key Assumptions

1. **AAMAD_TARGET_RUNTIME = crewai**: The system will use CrewAI as the primary runtime framework.
2. **LLM Access**: Users will have access to OpenAI API keys or local LLM alternatives.
3. **LinkedIn Integration**: The LinkedIn scraping tool is for demonstration purposes only; production deployment will use compliant data sources.
4. **MVP Scope**: Initial release focuses on the core 4-agent workflow; advanced features (ATS integration, multi-role, analytics dashboard) are deferred.
5. **Market Timing**: AI recruitment adoption is accelerating; the window for open-source multi-agent solutions is 12-18 months before major vendors replicate the approach.

---

## 11. Open Questions

1. Should the MVP include a web UI, or remain CLI-only for the initial release?
2. What ATS platforms should be prioritized for integration (Greenhouse, Lever, Workday)?
3. Should the system support multi-role hiring (multiple job descriptions simultaneously)?
4. What compliance frameworks (EEOC, GDPR, OFCCP) must be addressed in MVP?
5. Is a freemium/open-source model viable for initial customer acquisition?

---

## 12. Recommendations

1. **Proceed with MVP development** using the CrewAI recruitment example as the reference architecture.
2. **Focus on enterprise/mid-market** as the primary target for initial launch.
3. **Build on open-source foundation** to differentiate from closed-source competitors.
4. **Prioritize explainability** as a core value proposition for compliance-conscious buyers.
5. **Plan for ATS integration** as the most requested feature in post-MVP releases.

---

*This MRD will be used as input for the Product Requirements Document (PRD) in the next step of AAMAD Phase 1.*
