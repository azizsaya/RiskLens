# 01 — Project Overview

## The Problem

Banking and NBFC compliance teams manage real-time fraud detection, liquidity risk, credit risk, and regulatory reporting (AML, Basel III, local regulations) using largely manual processes. Analysts spend hours gathering evidence across disparate systems, cross-referencing policy documents, and assembling audit-ready reports. This manual workflow is slow, error-prone, and doesn't scale.

## What RiskLens Does

RiskLens is a compliance copilot that:

1. **Detects risk and fraud signals** automatically from transaction, loan, and position data using Dynamic Tables
2. **Answers natural language questions** from compliance officers with governed, explainable, evidence-backed responses
3. **Produces audit-ready regulatory outputs** — STR filings, LCR reports, credit risk summaries — with every figure linked to its source query and every statement linked to its policy clause
4. **Maintains a complete audit trail** of every question, SQL query, model used, and approval decision

## The Spine: Signal → Evidence → Finding → Report

```
Signal Detection          Evidence Gathering       Finding              Report
(Dynamic Tables)          (Agent + Skills)         (Case Note)          (STR / LCR / Credit)
                                                                        
Structuring ──┐           ┌── Cortex Analyst ──┐   ┌── Facts         ┌── Subject Info
Layering ─────┤           │   (SQL data)       │   │── Rule Triggered│── Suspicious Activity
Dormant ──────┤  ──►      │                    ├──►│── Evidence       ├──►  with Citations
Fan-out ──────┤  Alert    ├── Cortex Search ───┤   │── Recommendation│── Transactions
Watchlist ────┤  Queue    │   (Policy clauses) │   └── Status        │── Recommendation
LCR Breach ───┤           │                    │                     │── Filing Requirements
Credit Risk ──┘           └── SQL Skills ──────┘                     └── Approve / Reject
                              (No LLM math)                               (Human-in-loop)
```

## Core Design Principles

### 1. SQL Computes Numbers, LLM Writes Narrative
All metrics (LCR, NPA ratio, provision coverage, risk scores) are computed by SQL table functions. The LLM is never allowed to perform arithmetic. This ensures reproducibility and auditability.

### 2. Every Answer is Evidence-Backed
- **Structured data questions**: Cortex Analyst generates SQL from the semantic view; the SQL and results are shown
- **Policy questions**: Cortex Search retrieves the exact clause with document name and section
- **Combined questions**: Both tools are used; facts and citations are clearly separated

### 3. Governed by Default
- PII (name, email, phone) is masked for the ANALYST role; only the MLRO sees full data
- Object tags classify every table by sensitivity level and data domain
- Role hierarchy enforces least-privilege access

### 4. Audit Trail is Mandatory
Every copilot interaction writes to `COPILOT_AUDIT_LOG` with: question, generated SQL, model used, user, role, timestamp, and approval status.

### 5. Guardrails Prevent Hallucination
The agent has 7 explicit guardrails:
1. Never compute numbers — all from SQL
2. Never fabricate policy clauses — only cite what Cortex Search returns
3. Separate facts (SQL) from analysis (LLM)
4. Refuse out-of-domain questions
5. Flag low confidence when evidence is insufficient
6. Never advise closing a case without evidence
7. Always show source SQL

## What's Covered

| Domain | Signals | Metrics | Reports |
|--------|---------|---------|---------|
| **AML/Fraud** | Structuring, layering, dormant reactivation, fan-out, watchlist hits | Risk score (0-100), reason codes | Suspicious Transaction Report (STR) |
| **Liquidity** | LCR threshold breach | LCR (HQLA / net outflows) | LCR / Liquidity Summary |
| **Credit Risk** | NPA breach, concentration risk, DPD migration | NPA ratio, provision coverage | Credit Risk Portfolio Summary |

## Technology Stack

- **Snowflake Cortex**: Analyst, Search, Agents, COMPLETE (llama3.1-70b)
- **Dynamic Tables**: 8 tables for real-time signal detection
- **MCP Server**: Exposes agent + skills to external MCP clients
- **Streamlit in Snowflake**: 4-page compliance dashboard
- **CoCo CLI**: Entire project planned, built, tested, and deployed through Cortex Code
