# 02 — Data Model

## Schema Overview

```
RISKLENS (Database)
├── CORE (Schema)           — base tables, agent, skills, MCP server
├── SIGNALS (Schema)        — 8 Dynamic Tables for signal detection
├── REGULATORY (Schema)     — policy documents + Cortex Search service
├── AUDIT (Schema)          — audit log, FK integrity check, evaluation questions
└── GOVERNANCE (Schema)     — masking policies, tags
```

## Entity Relationship Diagram

```
  ┌──────────────┐         ┌──────────────┐
  │  CUSTOMERS   │ 1 ──► N │   ACCOUNTS   │
  │  (PK: CUST_ID)│         │  (PK: ACC_ID) │
  └──────┬───────┘         └──┬────┬──────┘
         │                    │    │
         │ 1:N                │    │ 1:N
         │                    │    │
  ┌──────▼───────────────────▼┐  ┌▼─────────────┐
  │     TRANSACTIONS          │  │    LOANS      │
  │  (PK: TXN_ID)             │  │  (PK: LOAN_ID) │
  │  FK: ACCOUNT_ID           │  │  FK: ACCOUNT_ID │
  │  FK: CUSTOMER_ID          │  │  FK: CUSTOMER_ID│
  └──────────┬────────────────┘  └───────────────┘
             │
             │ matched against
             │
  ┌──────────▼────────────┐     ┌─────────────────┐
  │     WATCHLIST          │     │    POSITIONS     │
  │  (PK: WATCHLIST_ID)    │     │  (PK: POSITION_ID)│
  │  Sanctions/PEP lists   │     │  HQLA, outflows   │
  └────────────────────────┘     └─────────────────┘

  ┌─────────────────┐     ┌────────────────┐     ┌──────────────────┐
  │   RISK_RULES    │     │  CASE_NOTES    │     │ REGULATORY_CHUNKS│
  │  Rule definitions│     │  Findings +    │     │  Policy text for │
  │  referenced by   │     │  approvals     │     │  Cortex Search   │
  │  signals         │     │                │     │                  │
  └─────────────────┘     └────────────────┘     └──────────────────┘
```

## FK Integrity

All relationships validated with zero orphan keys:

| Relationship | Orphan Count |
|-------------|-------------|
| ACCOUNTS → CUSTOMERS | 0 |
| TRANSACTIONS → ACCOUNTS | 0 |
| TRANSACTIONS → CUSTOMERS | 0 |
| LOANS → ACCOUNTS | 0 |
| LOANS → CUSTOMERS | 0 |
| ALERTS → ACCOUNTS | 0 |

Validated by: `RISKLENS.AUDIT.FK_INTEGRITY_CHECK` (persistent view)

---

## Table Definitions

### CORE.CUSTOMERS (5,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| CUSTOMER_ID | VARCHAR(20) PK | Unique ID (CUST-000001) |
| FIRST_NAME | VARCHAR(100) | First name (PII — masked for ANALYST role) |
| LAST_NAME | VARCHAR(100) | Last name (PII — masked) |
| DATE_OF_BIRTH | DATE | DOB (PII — tagged) |
| NATIONALITY | VARCHAR(50) | Country of citizenship |
| COUNTRY_OF_RESIDENCE | VARCHAR(50) | Current country |
| CUSTOMER_TYPE | VARCHAR(20) | INDIVIDUAL or CORPORATE |
| RISK_RATING | VARCHAR(10) | LOW / MEDIUM / HIGH / VERY_HIGH |
| PEP_FLAG | BOOLEAN | Politically Exposed Person |
| SANCTIONS_FLAG | BOOLEAN | On sanctions list |
| ONBOARDING_DATE | DATE | Account opening date |
| KYC_LAST_REVIEWED | DATE | Last KYC review |
| OCCUPATION | VARCHAR(100) | Job title |
| ANNUAL_INCOME | NUMBER(15,2) | Declared annual income |
| SOURCE_OF_FUNDS | VARCHAR(200) | SALARY / BUSINESS_INCOME / etc. |
| PHONE | VARCHAR(20) | Phone (PII — masked) |
| EMAIL | VARCHAR(200) | Email (PII — masked) |
| ADDRESS | VARCHAR(500) | Address (PII — tagged) |

**Distribution**: 70% LOW risk, 15% MEDIUM, 10% HIGH, 5% VERY_HIGH. 2% PEP, 0.5% sanctions flagged.

### CORE.ACCOUNTS (8,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| ACCOUNT_ID | VARCHAR(20) PK | Unique ID (ACC-00000001) |
| CUSTOMER_ID | VARCHAR(20) FK | Links to CUSTOMERS |
| ACCOUNT_TYPE | VARCHAR(30) | SAVINGS / CURRENT / LOAN / FIXED_DEPOSIT / NOSTRO |
| ACCOUNT_STATUS | VARCHAR(15) | ACTIVE / DORMANT / CLOSED / FROZEN |
| BRANCH_CODE | VARCHAR(10) | Branch identifier |
| BRANCH_NAME | VARCHAR(100) | Branch location name |
| CURRENCY | VARCHAR(3) | Account currency (default USD) |
| OPENING_DATE | DATE | When opened |
| CURRENT_BALANCE | NUMBER(18,2) | Current balance |
| AVERAGE_BALANCE_30D | NUMBER(18,2) | 30-day average |
| LAST_TRANSACTION_DATE | DATE | Last activity date |

**Distribution**: 85% ACTIVE, 8% DORMANT, 5% CLOSED, 2% FROZEN.

### CORE.TRANSACTIONS (100,110 rows)

| Column | Type | Description |
|--------|------|-------------|
| TXN_ID | VARCHAR(30) PK | Unique transaction ID |
| TXN_TIMESTAMP | TIMESTAMP_NTZ | When it occurred |
| ACCOUNT_ID | VARCHAR(20) FK | Account involved |
| CUSTOMER_ID | VARCHAR(20) FK | Customer involved |
| TXN_TYPE | VARCHAR(20) | CREDIT or DEBIT |
| TXN_CATEGORY | VARCHAR(30) | CASH_DEPOSIT / WIRE_TRANSFER / ATM / POS / INTERNAL / LOAN_REPAYMENT |
| AMOUNT | NUMBER(18,2) | Transaction amount |
| CURRENCY | VARCHAR(3) | Transaction currency |
| COUNTERPARTY_ACCOUNT | VARCHAR(30) | Other party's account |
| COUNTERPARTY_NAME | VARCHAR(200) | Other party's name |
| COUNTERPARTY_BANK | VARCHAR(100) | Other party's bank |
| COUNTERPARTY_COUNTRY | VARCHAR(50) | Country of counterparty |
| CHANNEL | VARCHAR(20) | BRANCH / ONLINE / MOBILE / ATM / SWIFT |
| IS_INTERNATIONAL | BOOLEAN | Cross-border flag |
| ORIGINATOR_COUNTRY | VARCHAR(50) | Sending country |
| BENEFICIARY_COUNTRY | VARCHAR(50) | Receiving country |

**Composition**: 100,000 normal + 110 seeded fraud pattern transactions.

### CORE.LOANS (2,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| LOAN_ID | VARCHAR(20) PK | Unique loan ID |
| ACCOUNT_ID | VARCHAR(20) FK | Linked account |
| CUSTOMER_ID | VARCHAR(20) FK | Borrower |
| LOAN_TYPE | VARCHAR(30) | TERM_LOAN / OVERDRAFT / MORTGAGE / PERSONAL / COMMERCIAL |
| SECTOR | VARCHAR(50) | RETAIL / MANUFACTURING / REAL_ESTATE / AGRICULTURE / IT_SERVICES / INFRASTRUCTURE |
| PRINCIPAL_AMOUNT | NUMBER(18,2) | Original loan amount |
| OUTSTANDING_AMOUNT | NUMBER(18,2) | Current balance |
| INTEREST_RATE | NUMBER(5,2) | Annual rate |
| DPD_BUCKET | VARCHAR(10) | CURRENT / 1-30 / 31-60 / 61-90 / 90+ |
| DAYS_PAST_DUE | INT | Exact days overdue |
| COLLATERAL_TYPE | VARCHAR(50) | PROPERTY / MACHINERY / SECURITIES / UNSECURED |
| COLLATERAL_VALUE | NUMBER(18,2) | Collateral market value |
| PROVISION_AMOUNT | NUMBER(18,2) | Loss provision booked |
| NPA_FLAG | BOOLEAN | Non-Performing Asset flag |

**Distribution**: 65% CURRENT, 15% 1-30 DPD, 10% 31-60, 6% 61-90, 4% 90+.

### CORE.POSITIONS (360 rows)

| Column | Type | Description |
|--------|------|-------------|
| POSITION_ID | VARCHAR(20) PK | Unique position ID |
| POSITION_DATE | DATE | Reporting date |
| CATEGORY | VARCHAR(30) | HQLA_L1 / HQLA_L2A / HQLA_L2B / CASH_OUTFLOW / CASH_INFLOW |
| SUB_CATEGORY | VARCHAR(50) | GOVT_BONDS / CORPORATE_BONDS / RETAIL_DEPOSITS / etc. |
| AMOUNT | NUMBER(18,2) | Position amount |
| HAIRCUT_PCT | NUMBER(5,2) | LCR haircut (0% L1, 15% L2A, 50% L2B) |
| RUNOFF_RATE_PCT | NUMBER(5,2) | Deposit runoff rate (5%-100%) |
| MATURITY_BUCKET | VARCHAR(20) | OVERNIGHT / 1W / 1M / 3M / 6M / 1Y |
| COUNTERPARTY_TYPE | VARCHAR(30) | RETAIL / SME / CORPORATE / BANK / SOVEREIGN |
| STRESS_SCENARIO | VARCHAR(20) | BASE / MODERATE / SEVERE |

### CORE.WATCHLIST (10 rows)

| Column | Type | Description |
|--------|------|-------------|
| WATCHLIST_ID | VARCHAR(20) PK | Entry ID |
| ENTITY_NAME | VARCHAR(200) | Sanctioned entity name |
| ENTITY_TYPE | VARCHAR(20) | INDIVIDUAL or ORGANIZATION |
| LIST_SOURCE | VARCHAR(50) | OFAC / UN / EU / PEP / ADVERSE_MEDIA |
| COUNTRY | VARCHAR(50) | Entity country |
| ALIASES | VARCHAR(500) | Known aliases |
| REASON | VARCHAR(500) | Why listed |

### CORE.RISK_RULES (10 rows)

| Column | Type | Description |
|--------|------|-------------|
| RULE_ID | VARCHAR(20) PK | Rule identifier (RR-001) |
| RULE_NAME | VARCHAR(200) | Human-readable name |
| DOMAIN | VARCHAR(20) | AML / FRAUD / LIQUIDITY / CREDIT |
| DESCRIPTION | VARCHAR(1000) | What the rule detects |
| SEVERITY | VARCHAR(10) | LOW / MEDIUM / HIGH / CRITICAL |
| THRESHOLD_VALUE | NUMBER(18,2) | Trigger threshold |
| LOOKBACK_HOURS | INT | Time window |
| REGULATORY_REFERENCE | VARCHAR(200) | Which regulation |

### CORE.CASE_NOTES

| Column | Type | Description |
|--------|------|-------------|
| CASE_ID | VARCHAR(36) PK | UUID |
| SIGNAL_TYPE | VARCHAR(30) | Which signal type |
| ENTITY_ID | VARCHAR(20) | Account or sector |
| FACTS | VARCHAR(5000) | Factual description |
| RULE_TRIGGERED | VARCHAR(200) | Which rule(s) |
| EVIDENCE_SUMMARY | VARCHAR(5000) | Evidence chain |
| RECOMMENDED_ACTION | VARCHAR(500) | What to do |
| STATUS | VARCHAR(20) | DRAFT / PENDING_REVIEW / APPROVED / ESCALATED / CLOSED |
| CREATED_BY | VARCHAR(100) | Who created |
| REVIEWED_BY | VARCHAR(100) | Who reviewed |

### AUDIT.COPILOT_AUDIT_LOG

| Column | Type | Description |
|--------|------|-------------|
| LOG_ID | VARCHAR(36) PK | UUID |
| SESSION_ID | VARCHAR(100) | Session identifier |
| USER_NAME | VARCHAR(100) | Who asked |
| USER_ROLE | VARCHAR(100) | With what role |
| QUESTION_TEXT | VARCHAR(5000) | The question |
| GENERATED_SQL | VARCHAR(10000) | SQL that was run |
| MODEL_USED | VARCHAR(50) | Which LLM or skill |
| RESPONSE_TEXT | VARCHAR(10000) | The answer |
| APPROVAL_STATUS | VARCHAR(20) | PENDING / APPROVED / REJECTED |

---

## Seeded Fraud Patterns

| # | Pattern | Account | Description | Expected Signal |
|---|---------|---------|-------------|----------------|
| 1 | Structuring | ACC-00000050 | 25 cash deposits $8,500-$9,900 over 72h | DT_STRUCTURING_SIGNALS |
| 2 | Layering | ACC-00000100 | 15 inflows from CH + 15 outflows to HK within hours | DT_LAYERING_SIGNALS |
| 3 | Dormant Reactivation | ACC-00000200 | 14 months inactive, sudden $1M+ inflow from UAE | DT_DORMANT_REACTIVATION |
| 4 | Fan-out | ACC-00000300 | 35 transfers to unique recipients in NG/KE/GH/PH/MM | DT_FAN_OUT_SIGNALS |
| 5 | High-risk Wires | ACC-00000400 | 8 transfers $200K-$900K to OFAC-listed entity | DT_WATCHLIST_HITS |

## Dynamic Tables (Signal Detection)

| Dynamic Table | Signal Type | Severity | Current Count |
|--------------|-------------|----------|---------------|
| DT_STRUCTURING_SIGNALS | Structuring | HIGH | 4 |
| DT_LAYERING_SIGNALS | Layering | HIGH | 1 |
| DT_DORMANT_REACTIVATION | Dormant Reactivation | MEDIUM | 51 |
| DT_FAN_OUT_SIGNALS | Fan-out | HIGH | 1 |
| DT_WATCHLIST_HITS | Watchlist Match | CRITICAL | 35 |
| DT_LCR_MONITOR | LCR Threshold | MEDIUM | 30 |
| DT_CREDIT_EARLY_WARNING | Credit Risk | HIGH | 7 |
| DT_CONSOLIDATED_ALERTS | All (union) | Mixed | 129 |

## Regulatory Documents (20 chunks)

| Document | Type | Sections | Chunks |
|----------|------|----------|--------|
| Internal AML/CFT Policy v3.2 | INTERNAL_POLICY | 7 sections (CDD, monitoring, STR, sanctions, records, risk) | 7 |
| Basel III Liquidity Framework | REGULATORY_FRAMEWORK | LCR, cash flows, NSFR, stress testing | 4 |
| Internal Liquidity Risk Policy | INTERNAL_POLICY | Risk appetite, contingency funding plan | 2 |
| Internal Credit Risk Policy v2.1 | INTERNAL_POLICY | Asset classification, concentration, early warning, provisioning | 4 |
| RBI Master Direction on KYC | REGULATORY_FRAMEWORK | Customer ID, wire transfers | 2 |
| FATF Recommendations Summary | REGULATORY_FRAMEWORK | Recommendation 20 (STR) | 1 |
