# RiskLens Demo Script (3 Minutes)

## Setup
- Open Streamlit app: RISKLENS.CORE.RISKLENS_APP
- Ensure ACCOUNTADMIN role for full demo (masking demo needs role switch)

---

## 1. Alert Dashboard (30s)
- Show KPI row: **129 total alerts** — 35 Critical, 13 High, 81 Medium
- Point out Basel metrics: **LCR, NPA ratio, Provision Coverage** — all computed in SQL
- Show signal type chart — watchlist matches dominate
- Scroll to alert queue — filter by CRITICAL

**Key message:** "Real-time signals across AML, credit, and liquidity — all from Dynamic Tables."

## 2. Evidence & Skills (45s)
- Navigate to Evidence & Skills tab
- Enter `ACC-00000050` and click **Run Fraud Detection**
- Show: Risk Score 80/100, VERY_HIGH, 4 structuring signals, recommendation
- Click **Run AML Pattern Match**
- Show: STRUCTURING pattern, 24 matched transactions, $220K total
- Point out the **Policy Citation** box — exact clause from AML Policy Section 3(a)

**Key message:** "Three discrete SQL skills — fraud detection, AML matching, Basel metrics. Numbers come from SQL, never the LLM."

## 3. Investigation Chat (30s)
- Navigate to Investigation
- Select: "Why was account ACC-00000050 flagged?"
- Show the LLM response citing regulatory references
- Point out audit log counter incrementing in sidebar

**Key message:** "Natural language → cited, evidence-backed answer. Every interaction logged."

## 4. Report Generator (45s)
- Navigate to Report Generator
- Select STR, enter `ACC-00000050`, click **Generate STR**
- Walk through the report sections:
  - Subject info (note PII masking if analyst role)
  - Suspicious activity with policy citations
  - Supporting transactions
  - Recommendation
- Click **Approve & File**
- Show success message — case note created, audit log updated

**Key message:** "Signal → evidence → finding → audit-ready report. One-click filing with human-in-the-loop approval."

## 5. Closing (30s)
- Show sidebar: audit log count increased
- Mention governance: 3 roles, PII masking, object tags
- Mention MCP server exposing the agent + skills to external clients
- "Entire solution built through CoCo CLI — Cortex Analyst, Search, Agents, Dynamic Tables, Streamlit"

---

## Backup Questions for Q&A
- "What is the current LCR?" → Run Basel Metrics skill
- "Show watchlist matches" → Alert queue filter CRITICAL
- "What does the AML policy say about structuring?" → Investigation chat
- "Which sectors have NPA above 5%?" → Dashboard sector table
