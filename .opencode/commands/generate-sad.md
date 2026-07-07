---
description: Generate a comprehensive System Architecture Document for a multi-agent system with Next.js frontend and selected runtime backend.
agent: system-arch
---

# AAMAD MVP System Architecture Template

## Context & Instructions
Generate a comprehensive system architecture specification for a multi-agent system using CrewAI framework with a modern Next.js frontend and assistant-ui interface.
This document serves as a detailed blueprint for AI development agents to understand the complete system structure, requirements, and implementation approach.

## Input Requirements:
**PRD Document**: {{input}}
**MVP Scope**: Focus on core value proposition with 80/20 rule - 20% effort for 80% value
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## System Architecture Specification - Generate All Sections:

### 1. MVP Architecture Philosophy & Principles
**MVP Design Principles**:
- Customer Feedback First
- Modern LLM Interface
- Automated Deployment
- Observable by Default

**Core vs. Future Features Decision Framework**:
- Phase 3 Beta (MVP): Core agent functionality, assistant-ui interface, essential integrations
- Phase 3 Full: Advanced features, enterprise security, horizontal scaling

**Technical Architecture Decisions**:
- Justify Next.js App Router
- Explain assistant-ui selection
- Define CrewAI agent communication patterns
- Specify real-time streaming requirements

### 2. Multi-Agent System Specification
**Agent Architecture Requirements**:
- Define 3-4 specialized agents maximum for MVP scope
- Specify agent roles, goals, and backstories
- Detail agent collaboration patterns
- Define memory management requirements
- Specify tool integration needs

**Task Orchestration Specification**:
- Define task dependencies and execution flow
- Specify expected outputs and data formats
- Detail context passing between agents
- Define error handling and retry mechanisms
- Specify performance requirements

**CrewAI Framework Configuration**:
- Specify crew composition and process type
- Define memory and caching requirements
- Detail verbose logging needs
- Specify integration points with Next.js API routes

### 3. Frontend Architecture (Next.js + assistant-ui)
**Technology Stack**:
- Framework: Next.js 14+ with App Router
- UI Library: assistant-ui + shadcn/ui
- Styling: Tailwind CSS
- Type Safety: TypeScript
- State Management: Zustand

**Application Structure**:
- App Router directory structure
- API route organization
- Component architecture
- Custom assistant-ui components
- Layout and navigation

**assistant-ui Integration**:
- Custom tool components
- Streaming message handling
- User interaction patterns
- Feedback collection
- Theming and customization

### 4. Backend Architecture
**API Architecture**:
- Next.js API routes for agent communication
- Streaming response handling
- Request/response data structures
- Rate limiting and security middleware
- Error handling and logging

**Database Architecture**:
- Data models for conversation history and analytics
- SQLite for MVP, PostgreSQL path
- Migration strategy
- Data retention policies

**CrewAI Integration Layer**:
- Python service layer for agent orchestration
- Agent configuration management
- Tool integration patterns
- Monitoring and logging

### 5. DevOps & Deployment
**CI/CD Pipeline**:
- GitHub Actions workflow
- Build process optimization
- Testing requirements
- Rollback procedures

**Infrastructure**:
- Compute and memory requirements
- Auto-scaling policies
- Health check endpoints
- Environment variable management

**Monitoring & Observability**:
- Application performance monitoring
- Log aggregation and analysis
- Alerting rules
- Dashboard requirements

### 6. Data Flow & Integration
**Request/Response Flow**:
- User request processing through assistant-ui
- Data transformation between frontend and CrewAI
- Streaming response handling
- Error propagation
- Caching strategies

**External Integration Requirements**:
- API integrations for agent tools
- Data source connections
- Third-party service error handling
- Webhook requirements

### 7. Performance & Scalability
**Performance Requirements**:
- Response time targets
- Concurrent user capacity
- Database query optimization
- Caching strategies

**Scalability Architecture**:
- Horizontal scaling triggers
- Load balancing strategies
- Database scaling path
- Microservice separation points

### 8. Security & Compliance
**Security Framework**:
- Authentication and authorization
- Data encryption (at rest and in transit)
- API security and input validation
- Security scanning

**Data Privacy**:
- User data handling
- GDPR compliance
- Data retention and deletion
- Audit logging

### 9. Testing & Quality Assurance
**Testing Strategy**:
- Unit testing coverage
- Integration testing
- End-to-end testing
- Performance testing
- Security testing

**Quality Gates**:
- Code quality standards
- Deployment validation
- User acceptance testing
- Performance benchmarks

### 10. MVP Launch & Feedback Strategy
**Beta Testing**:
- User selection criteria
- Feedback collection
- Feature flags
- Success metrics

**Business Metrics**:
- Key performance indicators
- Revenue tracking
- User engagement analysis

## Architecture Validation Checklist:
- [ ] All PRD requirements mapped to architectural components
- [ ] CrewAI agents properly designed
- [ ] assistant-ui integration supports required patterns
- [ ] Next.js architecture optimized for performance
- [ ] Database schema supports required queries
- [ ] API design follows RESTful principles
- [ ] Security measures appropriate for MVP
- [ ] CI/CD pipeline supports rapid iteration
- [ ] Monitoring provides actionable insights
- [ ] Architecture supports MVP to production transition
