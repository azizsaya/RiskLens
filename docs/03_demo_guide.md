# 03 — Demo Guide

## Pre-Demo Setup
- Open Streamlit app: `RISKLENS.CORE.RISKLENS_APP`
- Use ACCOUNTADMIN role (for full demo including unmasked PII)
- Have a second browser tab open to Snowsight for showing CoCo session history

---

## Demo Flow (3 Minutes)

### Act 1: The Dashboard (30 seconds)

**Click: Dashboard**

> "This is the compliance officer's command center. Everything updates in real-time via Dynamic Tables."

- Point at the **8 KPI metrics** across the top:
  - **129 total alerts** — 35 Critical, 13 High, 81 Medium
  - **LCR at ~101%** — barely above Basel III minimum, status AMBER
  - **NPA at 9.95%** — double the 5% threshold, status RED
  - **Provision coverage at 10.65%** — far below 70% target, RED
- Show the **signal distribution chart** — watchlist matches dominate
- Scroll to the **Sector Concentration table** — NPA column is color-coded red for breaches
- Show the **Alert Queue** — filter by CRITICAL to see watchlist matches

**Talking point:** *"Three risk domains, all computed in SQL via Dynamic Tables. The LCR is 101% — we're one bad day from breaching Basel III."*

---

### Act 2: Evidence & Skills (45 seconds)

**Click: Evidence & Skills**

> "Now let's investigate. These are discrete SQL skills — the LLM never does math."

- Enter `ACC-00000050` and click **Run Fraud Detection**
  - Show: Risk Score **80/100**, level **VERY_HIGH**, 4 structuring signals
  - Point out the **Recommendation**: "URGENT: File STR within 7 days"
  - Show the **signal details table**

- Click **Run AML Pattern Match**
  - Show: **STRUCTURING** pattern detected
  - **24 matched transactions** totaling **$220K**
  - Point out the **Policy Citation box**: "Internal AML/CFT Policy v3.2, Section 3(a)"
  - Highlight: *"The policy clause comes from Cortex Search, not the LLM"*

- Click **Run Basel Metrics**
  - Show: LCR 101% (AMBER), NPA 9.95% (RED), Provision Coverage 10.65% (RED)
  - Expand a **Components** view to show the HQLA breakdown

**Talking point:** *"Three skills, all pure SQL. Numbers never touch the LLM. Every result is auditable and reproducible."*

---

### Act 3: Investigation Chat (30 seconds)

**Click: Investigation**

> "A compliance officer can also just ask questions in natural language."

- Select quick question: **"Why was account ACC-00000050 flagged?"**
- Show the response: it cites the structuring pattern, references the AML policy
- Point out the **audit log counter** incrementing in the sidebar

**Talking point:** *"The Cortex Agent routes to Analyst for data and Search for policy. If it can't find evidence, it says so — never guesses."*

---

### Act 4: Report Generator (45 seconds)

**Click: Report Generator**

> "Now let's turn this evidence into a filing."

- Select **Suspicious Transaction Report (STR)**
- Enter `ACC-00000050`, click **Generate STR**
- Walk through the report:
  1. **Subject Information** — customer details (note PII masking if using ANALYST role)
  2. **Suspicious Activity** — each pattern with policy citation in blue box
  3. **Supporting Transactions** — data table with totals
  4. **Recommendation** — from the fraud detection skill
  5. **Filing Requirements** — 7 business days, MLRO review, no tipping off

- Click **Approve & File**
- Show: "STR APPROVED. Case note created. Audit log updated."

**Talking point:** *"Signal to evidence to documented finding to audit-ready report — one flow, fully governed, with human approval required."*

---

### Act 5: Close (30 seconds)

> "To summarize what we built:"

- **8 Dynamic Tables** detecting fraud signals in real-time
- **3 SQL skills** where the LLM never does arithmetic
- **Cortex Agent** with 7 guardrails — refuses when evidence is insufficient
- **3 reusable SKILL.md files** on a stage, attached to the agent
- **MCP server** exposing everything to external clients
- **Masking policies** — analyst sees `J***`, MLRO sees `James`
- **Scheduled monitoring task** runs daily at 8am
- **Complete audit trail** of every interaction
- *"And the entire thing was built through CoCo CLI in this session."*

---

## Backup Questions for Q&A

| Question | What It Shows |
|----------|--------------|
| "What if deposits drop 10%?" | Stress scenario via Basel Metrics skill |
| "Show watchlist matches" | Alert queue filter on CRITICAL |
| "What does the AML policy say about structuring?" | Cortex Search citation |
| "Which sectors have NPA above 5%?" | Dashboard table with red NPA values |
| "How is the LCR computed?" | Basel Metrics skill with component breakdown |
| "What's the provision coverage?" | Basel Metrics: 10.65% RED vs 70% target |

## Edge Cases to Demonstrate

| Scenario | Expected Behavior |
|----------|------------------|
| Ask about weather | "This question is outside my compliance domain." |
| Ask to close a case without evidence | Agent refuses: "Cannot advise without evidence" |
| Query non-existent account | Fraud skill returns 0 signals, "NO_ACTION" |
| Ask agent to compute a number | Agent uses SQL tool, shows query |
