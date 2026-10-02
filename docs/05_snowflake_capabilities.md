# 05 — Snowflake Capabilities Used

## Feature Map

| # | Snowflake Feature | How RiskLens Uses It | Object Name |
|---|-------------------|---------------------|-------------|
| 1 | **Dynamic Tables** | 8 DTs detect fraud signals in near-real-time (1h lag): structuring, layering, dormant reactivation, fan-out, watchlist hits, LCR monitor, credit early warning, consolidated alerts | `RISKLENS.SIGNALS.DT_*` |
| 2 | **Cortex Analyst** | Text-to-SQL over a semantic view covering 6 tables. Compliance officers ask NL questions and get governed SQL + results | Via `COMPLIANCE_COPILOT` agent |
| 3 | **Semantic View** | 6 tables (CUSTOMERS, ACCOUNTS, TRANSACTIONS, LOANS, POSITIONS, DT_CONSOLIDATED_ALERTS) with 10 verified queries (VQRs) and metric definitions | `RISKLENS.CORE.RISKLENS_COMPLIANCE` |
| 4 | **Cortex Search** | Retrieves regulatory policy clauses with citations (document name, section). 20 chunks across 6 documents | `RISKLENS.REGULATORY.POLICY_SEARCH` |
| 5 | **Cortex Agent** | Orchestrates between Analyst (data) and Search (policy). Has 7 guardrails, 3 attached SKILL.md files, and sample questions | `RISKLENS.CORE.COMPLIANCE_COPILOT` |
| 6 | **Agent Skills (SKILL.md)** | 3 reusable skills on a named stage: fraud_detection, basel_metrics, str_generator. Each follows the SKILL.md spec with YAML frontmatter | `@RISKLENS.CORE.SKILLS_STAGE` |
| 7 | **Cortex COMPLETE** | LLM (llama3.1-70b) powers the Investigation Chat for narrative generation. Never used for computation | Via Streamlit chat page |
| 8 | **MCP Server** | Snowflake-managed MCP server exposes 5 tools: agent, search, fraud detection, AML match, Basel metrics. External MCP clients can connect | `RISKLENS.CORE.RISKLENS_MCP` |
| 9 | **SQL UDTFs** | 3 table functions as discrete skills: SKILL_FRAUD_DETECTION, SKILL_AML_PATTERN_MATCH, SKILL_BASEL_METRICS. All computation in SQL | `RISKLENS.CORE.SKILL_*` |
| 10 | **Streamlit in Snowflake** | 4-page dashboard: Alert Dashboard, Investigation Chat, Evidence & Skills, Report Generator. Runs on warehouse | `RISKLENS.CORE.RISKLENS_APP` |
| 11 | **Masking Policies** | 3 policies: MASK_PII_NAME (first/last name), MASK_EMAIL, MASK_PHONE. ANALYST sees masked; MLRO sees full | `RISKLENS.GOVERNANCE.MASK_*` |
| 12 | **Object Tags** | 3 tag types: SENSITIVITY_LEVEL (PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED), DATA_DOMAIN (AML/CREDIT/LIQUIDITY/KYC), PII (TRUE/FALSE) | `RISKLENS.GOVERNANCE.*` |
| 13 | **Roles (RBAC)** | 3 custom roles in hierarchy: RISKLENS_ANALYST → RISKLENS_COMPLIANCE_OFFICER → RISKLENS_MLRO | Role hierarchy |
| 14 | **Tasks (Scheduled)** | Daily signal monitoring at 8am ET. Logs alert counts and Basel metrics to audit log | `RISKLENS.CORE.DAILY_SIGNAL_MONITOR` |
| 15 | **Stages** | 2 stages: STREAMLIT_STAGE (app code), SKILLS_STAGE (SKILL.md files), POLICY_DOCS (regulatory documents) | `RISKLENS.CORE.*_STAGE` |
| 16 | **Views** | FK_INTEGRITY_CHECK validates all foreign key relationships (0 orphan keys) | `RISKLENS.AUDIT.FK_INTEGRITY_CHECK` |

## Why Each Feature Matters

### Dynamic Tables (not Streams + Tasks)
We chose Dynamic Tables over Streams + Tasks because:
- **Declarative**: define the query, Snowflake handles the refresh
- **Incremental**: only processes new data (where supported)
- **Observable**: built-in lag monitoring
- **Composable**: DT_CONSOLIDATED_ALERTS unions all other DTs

### Cortex Agent (not raw LLM calls)
The agent provides:
- **Tool routing**: automatically decides between Analyst and Search
- **Guardrails**: system prompt enforced across all interactions
- **Skills**: reusable SKILL.md files on stage
- **Audit**: every tool call is traceable

### SQL Skills (not LLM computation)
All metrics are in SQL UDTFs because:
- **Reproducible**: same input always produces same output
- **Auditable**: the SQL is logged and can be re-run
- **Precise**: no floating-point drift from LLM estimation
- **Fast**: executes on warehouse compute, not LLM inference

### MCP Server (not just internal use)
The MCP server enables:
- External compliance tools to query our agent
- Claude Desktop, Cursor, or other MCP clients to investigate accounts
- Cross-tool orchestration without custom API development

### Masking Policies (not application-level filtering)
Snowflake masking policies enforce PII protection at the platform level:
- No application code can bypass them
- They apply to direct SQL queries too
- Different roles see different data from the same query
