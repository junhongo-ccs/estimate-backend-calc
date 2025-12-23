# AI Estimation System - Master Roadmap

> **Design Goal**: Azure AI Agent as the central orchestrator, using Calc API and RAG as tools to generate executive-level HTML estimates.

## 🏁 Phase 1: AI Agent Core (flow)
- [x] Azure Environment Setup (Foundry, OpenAI, Search)
- [x] RAG Knowledge Base Construction (18 docs indexed)
- [x] Local Flow Testing & Mock Integration
- [x] CI/CD Pipeline (Automated testing on push)
- [ ] **Integration: Connect Agent to Calc API Tool**
- [x] Upload & Configure Flow in Foundry (Project: `est-agent-v2`)
    - [x] Connection Configured (`jhong-mjha50n5-swedencentral`)
    - [x] Verification Passed (Compute Session)
- [/] Deployment: Azure AI Online Endpoint
    - [x] ML Workspace & Endpoint Creation
    - [!] Deployment provisioning (Ready for final deployment attempt)

## 🏗️ Phase 2: Outer Fortifications - Calculation (estimate-backend-calc)
- [ ] Implement YAML-based calculation logic (No AI)
- [ ] Create Azure Functions endpoint
- [ ] Verify standalone calculation accuracy
- [ ] Expose endpoint for Agent's Tool Call

## 💻 Phase 3: Outer Fortifications - UI (estimation-ui-app)
- [ ] Implement modern, premium single-page UI
- [ ] Connect UI to **Agent Endpoint only** (one-shot request)
- [ ] Implement HTML rendering for `doc--8px` style responses

## 🔗 Phase 4: Full System Integration & Verification
- [ ] End-to-end test: UI -> Agent -> Calc -> AI Generation -> UI
- [ ] Verify Agent-led orchestration (Agent makes the call to Calc)
- [ ] Final quality check: "Executive-ready" response verification

---
*Last updated: 2025-12-22 03:22 JST*
