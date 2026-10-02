# 04 — Judging Criteria Mapping

## Primary Judging Focus

### 1. Real World Relevance

| Criterion | How RiskLens Addresses It | Evidence |
|-----------|--------------------------|----------|
| Surfaces risk and fraud signals | 8 Dynamic Tables detect structuring, layering, dormant reactivation, fan-out, watchlist hits, LCR breach, credit deterioration in real-time | 129 signals detected: 35 CRITICAL, 13 HIGH, 81 MEDIUM |
| Produces audit-ready regulatory outputs | STR drafts, LCR reports, credit risk summaries with every figure linked to SQL and every statement to policy clause | Report Generator page in Streamlit |
| Combines transaction + policy text | Cortex Analyst (structured data) + Cortex Search (policy text) orchestrated by Cortex Agent | Semantic view + 20 regulatory chunks |
| Business user can ask NL questions | Chat interface with quick questions; natural language to SQL via Cortex Analyst | Investigation page in Streamlit |
| Governed, explainable answers | PII masking, role-based access, audit log, 7 guardrails, confidence flags | Governance schema + agent guardrails |
| Signal → Evidence → Finding → Report | Full flow: Dynamic Tables detect → Skills gather evidence → Case note drafted → STR generated → Human approves | End-to-end demo in Streamlit |
| Covers actual compliance workflows | STR filing (7-day deadline, MLRO review), LCR monitoring (Basel III 100% min), NPA tracking (RBI 5% threshold) | All three domains with real regulatory refs |

### 2. Technical Execution

| Criterion | How RiskLens Addresses It | Evidence |
|-----------|--------------------------|----------|
| CoCo in Planning | Architecture designed, data model framed, AGENTS.md created via CoCo | Plan card + AGENTS.md |
| CoCo in Development | All SQL, skills, agent, semantic view, search, MCP, Streamlit built through CoCo | This CoCo session (20+ turns) |
| CoCo in Execution | End-to-end flow orchestrated, MCP server deployed, Streamlit running | Live app + MCP server |
| CoCo in Testing | Validation run: FK integrity, signal counts, skill outputs, golden questions | Audit log entry: SYSTEM_VALIDATION |
| Synthetic data generation | 115K+ rows across 9 tables, referentially consistent (0 orphan keys), 5 seeded fraud patterns | FK_INTEGRITY_CHECK view |
| Data pipeline creation | 8 Dynamic Tables with 1-hour target lag, scheduled monitoring task | DT_CONSOLIDATED_ALERTS |
| Semantic model authoring | Semantic view with 6 tables, 10 VQRs, validated via Cortex Analyst | RISKLENS.CORE.RISKLENS_COMPLIANCE |
| Streamlit app generation | 4-page app: dashboard, chat, evidence panel, report generator with styled tables and charts | RISKLENS.CORE.RISKLENS_APP |
| MCP connection | MCP server exposing agent + search + 3 skills to external clients | RISKLENS.CORE.RISKLENS_MCP |
| Document processing | 20 regulatory chunks from 6 policy documents, served via Cortex Search with citations | RISKLENS.REGULATORY.POLICY_SEARCH |

### 3. Solution Completeness

| Criterion | How RiskLens Addresses It | Evidence |
|-----------|--------------------------|----------|
| End-to-end flow | Signal detection → NL question → evidence → STR → approve → audit log | All 4 Streamlit pages |
| Multiple risk domains | AML/Fraud, Liquidity (Basel III), Credit Risk | 3 skill functions + 8 Dynamic Tables |
| Audit trail | Append-only log with question, SQL, model, user, role, timestamp | COPILOT_AUDIT_LOG |
| Human-in-the-loop | Approve / Reject buttons on STR; case note creation requires human | Report Generator page |
| Governance | 3 roles (ANALYST, COMPLIANCE_OFFICER, MLRO), PII masking, object tags | GOVERNANCE schema |
| Guardrails | 7 explicit rules: no LLM math, no fabricated citations, domain boundaries, confidence flags | Agent system prompt |

---

## CoCo Usage Guidelines Mapping

| Rubric Item | Demonstrated? | How |
|-------------|--------------|-----|
| **Planning with CoCo** | Yes | Architecture blueprint, data model design, AGENTS.md |
| **Development with CoCo** | Yes | All SQL, UDTFs, agent spec, semantic view, Streamlit |
| **Execution with CoCo** | Yes | MCP deployment, Streamlit serving, scheduled task |
| **Testing with CoCo** | Yes | FK validation, skill testing, signal count verification |
| **Synthetic data generation** | Yes | 115K+ rows, 5 fraud patterns, 0 orphan keys |
| **Data pipeline creation** | Yes | 8 Dynamic Tables, 1 scheduled task |
| **Semantic model authoring** | Yes | Semantic view with 10 VQRs, tested with Cortex Analyst |
| **Streamlit app generation** | Yes | 4-page styled app with charts, tables, chat |
| **MCP connection** | Yes | MCP server with 5 tools (agent, search, 3 skills) |
| **Document processing** | Yes | 20 regulatory chunks across 6 documents |
| **Reusable skills** | Yes | 3 SKILL.md files on @SKILLS_STAGE |
| **MCP connectors** | Yes | RISKLENS_MCP exposes all capabilities |
| **Automations** | Yes | DAILY_SIGNAL_MONITOR task (8am ET daily) |
| **Custom tools / function calling** | Yes | 3 SQL UDTFs callable as agent tools |
| **Guardrails and fallback** | Yes | 7 guardrails, confidence levels, domain refusal |

---

## Scoring Prediction

| Category | Weight | Self-Assessment | Justification |
|----------|--------|----------------|---------------|
| Real World Relevance | High | **Strong** | Covers actual compliance workflows with real regulatory references |
| Technical Execution | High | **Strong** | Full Snowflake-native stack, CoCo throughout, guardrails |
| Solution Completeness | High | **Strong** | End-to-end flow, 3 domains, audit trail, governance, human-in-loop |
