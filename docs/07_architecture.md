# 07 — Architecture

## 1. System Architecture (High-Level)

```mermaid
graph TB
    subgraph EXTERNAL["External Clients"]
        MCP_CLIENT["MCP Clients<br/>(Claude, Cursor, etc.)"]
        BROWSER["Compliance Officer<br/>(Browser)"]
    end

    subgraph RISKLENS_DB["RISKLENS Database"]

        subgraph DATA["Data Layer — CORE Schema"]
            CUST["CUSTOMERS<br/>5,000 rows"]
            ACC["ACCOUNTS<br/>8,000 rows"]
            TXN["TRANSACTIONS<br/>100,110 rows"]
            LOANS["LOANS<br/>2,000 rows"]
            POS["POSITIONS<br/>360 rows"]
            WL["WATCHLIST<br/>10 entries"]
            RULES["RISK_RULES<br/>10 rules"]
        end

        subgraph SIGNALS["Signal Detection — SIGNALS Schema"]
            DT_STRUCT["DT_STRUCTURING<br/>Cash &lt; $10K threshold"]
            DT_LAYER["DT_LAYERING<br/>Rapid in-out wires"]
            DT_DORM["DT_DORMANT<br/>Reactivation"]
            DT_FAN["DT_FAN_OUT<br/>1-to-many transfers"]
            DT_WL["DT_WATCHLIST_HITS<br/>Sanctions matches"]
            DT_LCR["DT_LCR_MONITOR<br/>Liquidity ratio"]
            DT_CREDIT["DT_CREDIT_WARNING<br/>NPA + concentration"]
            DT_ALL["DT_CONSOLIDATED_ALERTS<br/>129 signals unified"]
        end

        subgraph REGULATORY["Knowledge Layer — REGULATORY Schema"]
            CHUNKS["REGULATORY_CHUNKS<br/>20 chunks / 6 documents"]
            CS["Cortex Search Service<br/>POLICY_SEARCH"]
        end

        subgraph AI["AI Layer — Cortex"]
            SV["Semantic View<br/>RISKLENS_COMPLIANCE<br/>6 tables, 10 VQRs"]
            ANALYST["Cortex Analyst<br/>(Text-to-SQL)"]
            AGENT["Cortex Agent<br/>COMPLIANCE_COPILOT<br/>7 Guardrails"]
            SKILLS_STAGE["Agent Skills<br/>fraud_detection.SKILL.md<br/>basel_metrics.SKILL.md<br/>str_generator.SKILL.md"]
        end

        subgraph SKILL_FNS["SQL Skills (UDTFs)"]
            SK1["SKILL_FRAUD_DETECTION<br/>Risk score + reason codes"]
            SK2["SKILL_AML_PATTERN_MATCH<br/>Typology → policy clause"]
            SK3["SKILL_BASEL_METRICS<br/>LCR / NPA / PCR in SQL"]
        end

        subgraph MCP_SVR["MCP Server"]
            MCP["RISKLENS_MCP<br/>5 tools exposed"]
        end

        subgraph UI["Presentation Layer"]
            ST["Streamlit App<br/>RISKLENS_APP"]
            PG1["Dashboard<br/>KPIs + Charts + Alerts"]
            PG2["Investigation<br/>NL Chat"]
            PG3["Evidence & Skills<br/>Run + Inspect"]
            PG4["Report Generator<br/>STR + LCR + Credit"]
        end

        subgraph GOV["Governance & Audit"]
            ROLES["3 Roles<br/>ANALYST → CO → MLRO"]
            MASK["3 Masking Policies<br/>Name / Email / Phone"]
            TAGS["3 Tag Types<br/>Sensitivity / Domain / PII"]
            AUDIT["COPILOT_AUDIT_LOG<br/>Every interaction"]
            CASE["CASE_NOTES<br/>Findings + Approvals"]
            TASK["DAILY_SIGNAL_MONITOR<br/>Scheduled 8am ET"]
        end
    end

    %% Data flows
    TXN --> DT_STRUCT & DT_LAYER & DT_DORM & DT_FAN
    TXN & WL --> DT_WL
    POS --> DT_LCR
    LOANS --> DT_CREDIT
    DT_STRUCT & DT_LAYER & DT_DORM & DT_FAN & DT_WL & DT_LCR & DT_CREDIT --> DT_ALL

    CHUNKS --> CS

    SV --> ANALYST
    ANALYST --> AGENT
    CS --> AGENT
    SKILLS_STAGE --> AGENT

    AGENT --> MCP
    MCP_CLIENT --> MCP

    SK1 & SK2 & SK3 --> ST

    AGENT --> ST
    BROWSER --> ST
    ST --> PG1 & PG2 & PG3 & PG4

    PG2 & PG3 & PG4 --> AUDIT
    PG4 --> CASE

    DT_ALL --> PG1
    TASK --> AUDIT

    MASK --> CUST
    TAGS --> CUST & TXN & LOANS & POS
    ROLES --> GOV
```

## 2. Signal Detection Flow

```mermaid
flowchart LR
    subgraph SOURCE["Source Data"]
        T["TRANSACTIONS<br/>100K+ rows"]
        L["LOANS<br/>2K rows"]
        P["POSITIONS<br/>360 rows"]
        W["WATCHLIST<br/>10 entries"]
    end

    subgraph AML_SIGNALS["AML / Fraud Signals"]
        S1["STRUCTURING<br/>Cash deposits $8K-$9.9K<br/>within 72h<br/><b>Rule: RR-001</b>"]
        S2["LAYERING<br/>In-out ratio &gt; 80%<br/>within 24h<br/><b>Rule: RR-002</b>"]
        S3["DORMANT<br/>12+ months inactive<br/>sudden activity<br/><b>Rule: RR-003</b>"]
        S4["FAN-OUT<br/>20+ unique recipients<br/>within 24h<br/><b>Rule: RR-004</b>"]
        S5["WATCHLIST<br/>Counterparty matches<br/>OFAC/UN/EU/PEP<br/><b>Rule: RR-005</b>"]
    end

    subgraph LIQ_SIGNALS["Liquidity Signals"]
        S6["LCR MONITOR<br/>HQLA / Net Outflows<br/>vs 100% threshold<br/><b>Rule: RR-007</b>"]
    end

    subgraph CREDIT_SIGNALS["Credit Signals"]
        S7["CREDIT WARNING<br/>NPA ratio &gt; 5%<br/>Concentration &gt; 25%<br/><b>Rules: RR-008/009</b>"]
    end

    T --> S1 & S2 & S3 & S4
    T & W --> S5
    P --> S6
    L --> S7

    S1 & S2 & S3 & S4 & S5 --> CONSOLIDATED
    S6 & S7 --> CONSOLIDATED

    CONSOLIDATED["DT_CONSOLIDATED_ALERTS<br/><b>129 signals</b><br/>35 CRITICAL | 13 HIGH | 81 MEDIUM"]

    CONSOLIDATED --> DASHBOARD["Alert Dashboard<br/>+ Queue"]

    style S1 fill:#f59e0b,color:#000
    style S2 fill:#f59e0b,color:#000
    style S3 fill:#d97706,color:#000
    style S4 fill:#f59e0b,color:#000
    style S5 fill:#ef4444,color:#fff
    style S6 fill:#8b5cf6,color:#fff
    style S7 fill:#ef4444,color:#fff
    style CONSOLIDATED fill:#1e40af,color:#fff
```

## 3. Query Flow (Question → Answer)

```mermaid
sequenceDiagram
    actor User as Compliance Officer
    participant ST as Streamlit App
    participant AG as Cortex Agent
    participant AN as Cortex Analyst<br/>(Semantic View)
    participant CS as Cortex Search<br/>(Policy Docs)
    participant AL as Audit Log

    User->>ST: "Why was ACC-00000050 flagged?"
    ST->>AG: Route question

    Note over AG: Guardrail check:<br/>Is this in-domain? ✓<br/>Needs data + policy? → use both tools

    AG->>AN: Query structured data
    AN-->>AG: SQL: SELECT FROM DT_CONSOLIDATED_ALERTS<br/>Result: 4 structuring signals, score 80

    AG->>CS: Search "structuring detection threshold"
    CS-->>AG: AML/CFT Policy v3.2, Section 3(a):<br/>"Multiple cash deposits below $10K..."

    Note over AG: Guardrail check:<br/>Numbers from SQL? ✓<br/>Citation from Search? ✓<br/>Confidence: HIGH

    AG-->>ST: Structured response:<br/>1. Finding (4 signals)<br/>2. Evidence (SQL shown)<br/>3. Citation (Section 3a)<br/>4. Risk: HIGH<br/>5. Recommend: File STR

    ST->>AL: Log: question, SQL, model,<br/>user, role, timestamp

    ST-->>User: Display with sources
```

## 4. Report Flow (Evidence → STR Filing)

```mermaid
flowchart TB
    START["Officer clicks<br/>'Generate STR'<br/>for ACC-00000050"]

    subgraph EVIDENCE["Evidence Gathering (SQL Skills)"]
        SK1["SKILL_FRAUD_DETECTION<br/>→ Score: 80/100, VERY_HIGH<br/>→ 4 signals, STRUCTURING"]
        SK2["SKILL_AML_PATTERN_MATCH<br/>→ 24 txns, $220K<br/>→ Policy: Section 3(a)"]
        CUST_Q["Customer Query<br/>→ Name, Risk Rating,<br/>Nationality, PEP status"]
        TXN_Q["Transaction Query<br/>→ Top 20 transactions<br/>→ Total amount"]
    end

    subgraph REPORT["STR Assembly"]
        R1["1. Subject Information"]
        R2["2. Suspicious Activity<br/>+ Policy Citations"]
        R3["3. Supporting Transactions"]
        R4["4. Recommendation"]
        R5["5. Filing Requirements<br/>7 days / MLRO / No tipping off"]
    end

    subgraph APPROVAL["Human-in-the-Loop"]
        APPROVE["✅ Approve & File"]
        REJECT["❌ Reject / Return"]
    end

    subgraph PERSIST["Audit Trail"]
        CASE["INSERT → CASE_NOTES<br/>status: APPROVED"]
        LOG["INSERT → AUDIT_LOG<br/>action: STR_APPROVED"]
    end

    START --> SK1 & SK2 & CUST_Q & TXN_Q
    SK1 & SK2 & CUST_Q & TXN_Q --> R1 & R2 & R3 & R4 & R5
    R1 & R2 & R3 & R4 & R5 --> APPROVE & REJECT

    APPROVE --> CASE & LOG
    REJECT --> LOG

    style APPROVE fill:#22c55e,color:#fff
    style REJECT fill:#ef4444,color:#fff
    style SK1 fill:#2563eb,color:#fff
    style SK2 fill:#2563eb,color:#fff
```

## 5. Three Risk Domains

```mermaid
graph TB
    subgraph AML["AML / Fraud Domain"]
        A1["Structuring Detection<br/>BSA/AML 31 CFR 1010.311"]
        A2["Layering Detection<br/>FATF Recommendation 20"]
        A3["Watchlist Screening<br/>OFAC / UN / EU"]
        A4["Dormant Reactivation<br/>RBI KYC Master Direction"]
        A5["Fan-out Patterns<br/>FATF Red Flag Indicators"]
        A_OUT["→ STR Filing<br/>→ Risk Rating Upgrade<br/>→ Account Freeze"]
    end

    subgraph LIQ["Liquidity Domain"]
        L1["LCR Computation<br/>Basel III Framework"]
        L2["HQLA Classification<br/>L1: 0% haircut<br/>L2A: 15% haircut"]
        L3["Stress Testing<br/>Base / Moderate / Severe"]
        L4["Contingency Funding<br/>Internal Policy"]
        L_OUT["→ LCR Report<br/>→ Threshold Alerts<br/>→ CFP Activation"]
    end

    subgraph CREDIT["Credit Risk Domain"]
        C1["NPA Ratio<br/>RBI IRAC Norms"]
        C2["DPD Migration<br/>Current→90+ tracking"]
        C3["Sector Concentration<br/>Basel III Large Exposure"]
        C4["Provision Coverage<br/>IFRS 9 / Ind AS 109"]
        C_OUT["→ Portfolio Report<br/>→ Sector Freeze<br/>→ Provision Adjustment"]
    end

    A1 & A2 & A3 & A4 & A5 --> A_OUT
    L1 & L2 & L3 & L4 --> L_OUT
    C1 & C2 & C3 & C4 --> C_OUT

    style AML fill:#fef3c7,color:#000
    style LIQ fill:#ede9fe,color:#000
    style CREDIT fill:#fce7f3,color:#000
    style A_OUT fill:#f59e0b,color:#000
    style L_OUT fill:#8b5cf6,color:#fff
    style C_OUT fill:#ec4899,color:#fff
```

## 6. Governance Model

```mermaid
graph LR
    subgraph ROLES["Role Hierarchy"]
        ANALYST["RISKLENS_ANALYST<br/>Read-only access"]
        CO["RISKLENS_COMPLIANCE_OFFICER<br/>+ Case note read"]
        MLRO["RISKLENS_MLRO<br/>+ Write + Approve + Full PII"]
        ADMIN["ACCOUNTADMIN"]

        ANALYST --> CO --> MLRO --> ADMIN
    end

    subgraph MASKING["PII Masking"]
        direction TB
        M1["ANALYST sees:<br/>J*** | S*** | ja***@email.com"]
        M2["MLRO sees:<br/>James | Smith | james.smith@email.com"]
    end

    subgraph TAGS_SEC["Object Tags"]
        T1["SENSITIVITY_LEVEL<br/>PUBLIC / INTERNAL /<br/>CONFIDENTIAL / RESTRICTED"]
        T2["DATA_DOMAIN<br/>AML / CREDIT_RISK /<br/>LIQUIDITY / KYC"]
        T3["PII<br/>TRUE / FALSE"]
    end

    subgraph AUDIT_SEC["Audit"]
        AU1["COPILOT_AUDIT_LOG<br/>Every question logged"]
        AU2["FK_INTEGRITY_CHECK<br/>0 orphan keys"]
        AU3["DAILY_SIGNAL_MONITOR<br/>Scheduled task 8am ET"]
    end

    ANALYST --> M1
    MLRO --> M2

    style ANALYST fill:#94a3b8,color:#000
    style CO fill:#60a5fa,color:#000
    style MLRO fill:#2563eb,color:#fff
    style ADMIN fill:#1e40af,color:#fff
```

## 7. MCP Server Topology

```mermaid
graph LR
    subgraph CLIENTS["External MCP Clients"]
        CL1["Claude Desktop"]
        CL2["Cursor IDE"]
        CL3["Custom App"]
    end

    subgraph MCP_SERVER["RISKLENS_MCP Server"]
        T1["compliance_copilot<br/>CORTEX_AGENT_RUN"]
        T2["policy_search<br/>CORTEX_SEARCH_QUERY"]
        T3["fraud_detection<br/>GENERIC (UDTF)"]
        T4["aml_pattern_match<br/>GENERIC (UDTF)"]
        T5["basel_metrics<br/>GENERIC (UDTF)"]
    end

    subgraph SNOWFLAKE["Snowflake Objects"]
        AG["Cortex Agent"]
        CS["Cortex Search"]
        F1["SKILL_FRAUD_DETECTION()"]
        F2["SKILL_AML_PATTERN_MATCH()"]
        F3["SKILL_BASEL_METRICS()"]
    end

    CL1 & CL2 & CL3 -->|MCP Protocol| T1 & T2 & T3 & T4 & T5
    T1 --> AG
    T2 --> CS
    T3 --> F1
    T4 --> F2
    T5 --> F3

    style MCP_SERVER fill:#1e293b,color:#fff
    style T1 fill:#2563eb,color:#fff
    style T2 fill:#8b5cf6,color:#fff
    style T3 fill:#f59e0b,color:#000
    style T4 fill:#f59e0b,color:#000
    style T5 fill:#f59e0b,color:#000
```

## 8. CoCo Build Flow

```mermaid
flowchart LR
    subgraph PLAN["1. Planning"]
        P1["Architecture<br/>blueprint"]
        P2["Data model<br/>design"]
        P3["AGENTS.md<br/>created"]
    end

    subgraph DEV["2. Development"]
        D1["Tables +<br/>Seed Data"]
        D2["Dynamic<br/>Tables (8)"]
        D3["Cortex Search<br/>+ Semantic View"]
        D4["SQL Skills<br/>(3 UDTFs)"]
        D5["Agent +<br/>Skills (3)"]
        D6["MCP Server"]
        D7["Streamlit<br/>App"]
        D8["Governance"]
    end

    subgraph EXEC["3. Execution"]
        E1["End-to-end<br/>demo flow"]
        E2["Scheduled<br/>monitoring"]
    end

    subgraph TEST["4. Testing"]
        T1["FK integrity<br/>0 orphans"]
        T2["Signal counts<br/>129 verified"]
        T3["Skill outputs<br/>validated"]
        T4["Golden Qs<br/>10 tested"]
    end

    P1 --> P2 --> P3 --> D1
    D1 --> D2 --> D3 --> D4 --> D5 --> D6 --> D7 --> D8
    D8 --> E1 --> E2 --> T1 --> T2 --> T3 --> T4

    style PLAN fill:#ede9fe,color:#000
    style DEV fill:#dbeafe,color:#000
    style EXEC fill:#d1fae5,color:#000
    style TEST fill:#fef3c7,color:#000
```
