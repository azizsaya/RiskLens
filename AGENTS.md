# RiskLens Compliance Copilot — Project Instructions

## Overview
RiskLens is a Snowflake-native compliance copilot for banking/NBFC risk management.
It covers AML/Fraud, Liquidity (Basel III), and Credit Risk — from signal detection
through evidence gathering to audit-ready regulatory output.

## Architecture
```
RISKLENS database
├── CORE schema          — base tables + agent + semantic view + skills + MCP server
├── SIGNALS schema       — 8 Dynamic Tables (fraud/risk signal detection)
├── REGULATORY schema    — policy chunks + Cortex Search service + live lookup
├── AUDIT schema         — copilot audit log + FK integrity check + evaluation questions
└── GOVERNANCE schema    — masking policies, tags, roles
```

## Critical Constraints
1. **SQL computes numbers, LLM writes narrative.** Never let the LLM do arithmetic.
   All metrics (LCR, NPA ratio, provision coverage) come from SQL functions.
2. **Every answer must be evidence-backed.** Show the SQL query used and cite the
   specific policy section. If data is insufficient, say so explicitly.
3. **Audit trail is mandatory.** Every copilot interaction logs to
   RISKLENS.AUDIT.COPILOT_AUDIT_LOG with question, SQL, model, user, timestamp.
4. **PII is governed.** FIRST_NAME, LAST_NAME, EMAIL, PHONE are masked for
   RISKLENS_ANALYST role. Only RISKLENS_MLRO and ACCOUNTADMIN see full PII.

## Data Model (FK Relationships)
```
CUSTOMERS (PK: CUSTOMER_ID)
  └─> ACCOUNTS (PK: ACCOUNT_ID, FK: CUSTOMER_ID)
       ├─> TRANSACTIONS (FK: ACCOUNT_ID, CUSTOMER_ID)
       └─> LOANS (FK: ACCOUNT_ID, CUSTOMER_ID)
WATCHLIST (PK: WATCHLIST_ID) — matched against TRANSACTIONS.COUNTERPARTY_NAME
POSITIONS (PK: POSITION_ID) — liquidity positions for LCR computation
RISK_RULES (PK: RULE_ID) — rule definitions referenced by signals
```
All FK relationships validated: zero orphan keys (see RISKLENS.AUDIT.FK_INTEGRITY_CHECK).

## Seeded Fraud Patterns
- **Structuring**: ACC-00000050 — 25 cash deposits between $8.5K-$9.9K
- **Layering**: ACC-00000100 — rapid in-out wires via Offshore Holdings Ltd (Switzerland→Hong Kong)
- **Dormant reactivation**: ACC-00000200 — 14 months dormant, sudden $1M+ inflow from UAE
- **Fan-out**: ACC-00000300 — 35 transfers to unique recipients in NG, KE, GH, PH, MM
- **High-risk wires**: ACC-00000400 — $200K-$900K to Global Commodities FZE (OFAC listed)

## Skills (SQL Table Functions)
| Skill | Function | I/O |
|-------|----------|-----|
| Fraud Detection | `SKILL_FRAUD_DETECTION(account_id)` | Risk score 0-100, signals, reason codes, recommendation |
| AML Pattern Match | `SKILL_AML_PATTERN_MATCH(account_id)` | Pattern type, matched txns, amount, rule, policy clause citation |
| Basel Metrics | `SKILL_BASEL_METRICS(date, scenario)` | LCR, NPA ratio, provision coverage with status and regulatory ref |

## Key Objects
- **Semantic View**: RISKLENS.CORE.RISKLENS_COMPLIANCE (6 tables, 10 VQRs)
- **Cortex Search**: RISKLENS.REGULATORY.POLICY_SEARCH (20 policy chunks, 5 documents)
- **Cortex Agent**: RISKLENS.CORE.COMPLIANCE_COPILOT (Analyst + Search tools)
- **MCP Server**: RISKLENS.CORE.RISKLENS_MCP (agent + search + 3 skills exposed)
- **Streamlit**: RISKLENS.CORE.RISKLENS_APP (dashboard + chat + evidence + reports)

## Roles
| Role | Access | PII |
|------|--------|-----|
| RISKLENS_ANALYST | Read all, no case note writes | Masked |
| RISKLENS_COMPLIANCE_OFFICER | Read all + case notes | Masked |
| RISKLENS_MLRO | Full access + approvals + audit | Unmasked |

## Demo Flow (3 minutes)
1. Alert Dashboard → show 129 alerts (35 CRITICAL, 13 HIGH, 81 MEDIUM)
2. Evidence & Skills → run SKILL_FRAUD_DETECTION('ACC-00000050') → risk score 80
3. Investigation Chat → ask "Why was account ACC-00000050 flagged?"
4. Evidence & Skills → run SKILL_AML_PATTERN_MATCH('ACC-00000050') → structuring detected
5. Report Generator → generate STR for ACC-00000050 with full evidence chain
6. Click "Approve & File" → case note created, audit log updated
7. Show audit log in sidebar counter incrementing

## Evaluation Questions (RISKLENS.AUDIT.EVALUATION_QUESTIONS)
10 golden questions across AML, Credit, and Liquidity domains with expected answers.

## Model
Using `llama3.1-70b` for CORTEX.COMPLETE in chat. All structured queries go through
Cortex Analyst (semantic view) or direct SQL skills — never through the LLM.
