# 06 — Glossary

## Acronyms

| Acronym | Full Form | Definition |
|---------|-----------|------------|
| **AML** | Anti-Money Laundering | Laws, regulations, and procedures to prevent criminals from disguising illegally obtained funds as legitimate income |
| **BSA** | Bank Secrecy Act | US federal law requiring financial institutions to assist government agencies in detecting and preventing money laundering |
| **CDD** | Customer Due Diligence | The process of verifying a customer's identity, understanding their financial activities, and assessing risk |
| **CFT** | Counter Financing of Terrorism | Measures to detect and prevent the financing of terrorist activities |
| **CoCo** | Cortex Code | Snowflake's AI coding assistant (CLI and desktop app) used for planning, development, execution, and testing |
| **CTR** | Currency Transaction Report | A mandatory report filed for cash transactions exceeding $10,000 (US) or Rs. 10 lakh (India) |
| **DPD** | Days Past Due | The number of days a loan payment is overdue; used to classify loan quality |
| **DT** | Dynamic Table | A Snowflake object that materializes the result of a query and refreshes automatically as source data changes |
| **EDD** | Enhanced Due Diligence | Additional verification steps required for high-risk customers (PEPs, high-risk jurisdictions) |
| **FATF** | Financial Action Task Force | An intergovernmental body that sets international standards for combating money laundering and terrorist financing |
| **FIU** | Financial Intelligence Unit | A government agency that receives, analyzes, and disseminates suspicious transaction reports |
| **FK** | Foreign Key | A column in one table that references the primary key of another table, ensuring referential integrity |
| **HQLA** | High-Quality Liquid Assets | Assets that can be quickly and easily converted to cash with little or no loss of value; used in LCR calculation |
| **IFRS 9** | International Financial Reporting Standard 9 | Accounting standard for financial instruments, including the Expected Credit Loss (ECL) model |
| **IRAC** | Income Recognition and Asset Classification | RBI norms for how banks recognize income and classify assets (standard, sub-standard, doubtful, loss) |
| **KYC** | Know Your Customer | The process of verifying a customer's identity before and during the business relationship |
| **LCR** | Liquidity Coverage Ratio | Basel III metric: HQLA / Net Cash Outflows over 30 days. Must be >= 100% |
| **LLM** | Large Language Model | An AI model trained on large text datasets; used for natural language understanding and generation |
| **MCP** | Model Context Protocol | An open standard for AI agents to securely interact with business applications and external data systems |
| **MLRO** | Money Laundering Reporting Officer | The designated officer responsible for overseeing AML compliance and filing suspicious transaction reports |
| **NBFC** | Non-Banking Financial Company | A financial institution that provides banking services without holding a banking license |
| **NPA** | Non-Performing Asset | A loan where the borrower has stopped making interest or principal payments; typically 90+ days past due |
| **NSFR** | Net Stable Funding Ratio | Basel III metric: Available Stable Funding / Required Stable Funding. Must be >= 100% |
| **OFAC** | Office of Foreign Assets Control | US Treasury department that administers and enforces economic sanctions |
| **OVD** | Officially Valid Document | Government-issued identity documents accepted for KYC verification |
| **PEP** | Politically Exposed Person | An individual who holds or has held a prominent public position, subject to enhanced due diligence |
| **PII** | Personally Identifiable Information | Data that can identify an individual: name, email, phone, date of birth, address |
| **PK** | Primary Key | A column that uniquely identifies each row in a table |
| **RBAC** | Role-Based Access Control | Security model where permissions are assigned to roles, and users are assigned to roles |
| **RBI** | Reserve Bank of India | India's central bank and primary financial regulatory authority |
| **SDN** | Specially Designated Nationals | OFAC's list of individuals and entities with whom US persons are prohibited from transacting |
| **STR** | Suspicious Transaction Report | A mandatory filing when a financial institution suspects money laundering or terrorist financing |
| **UDTF** | User-Defined Table Function | A custom function in Snowflake that returns a set of rows (a table) |
| **VQR** | Verified Query Representation | A pre-validated SQL query attached to a semantic view that teaches Cortex Analyst how to answer specific questions |

## Domain Terms

| Term | Definition |
|------|------------|
| **Structuring** | Deliberately breaking large transactions into smaller ones to avoid reporting thresholds (also called "smurfing") |
| **Layering** | Moving illicit funds through multiple accounts or transactions to obscure their origin; the second stage of money laundering |
| **Fan-out** | A pattern where one account sends funds to many different recipients in a short time, potentially distributing illicit proceeds |
| **Dormant Reactivation** | When an account with no activity for an extended period (12+ months) suddenly receives large or frequent transactions |
| **Watchlist Screening** | The process of checking customers and counterparties against sanctions lists (OFAC SDN, UN, EU) and PEP databases |
| **Risk Rating** | A composite score assigned to each customer based on geography, product, channel, and customer type risk factors |
| **DPD Bucket** | A classification of loan delinquency: CURRENT, 1-30, 31-60, 61-90, 90+ days past due |
| **Provision** | An amount set aside by the bank to cover expected losses on loans; higher for riskier loans |
| **Haircut** | A percentage reduction applied to the market value of an asset when calculating HQLA for LCR purposes |
| **Runoff Rate** | The percentage of deposits or funding expected to be withdrawn under a 30-day stress scenario |
| **Collateral** | An asset pledged by a borrower to secure a loan; can be property, machinery, securities, or unsecured |
| **Concentration Risk** | The risk from having too much exposure to a single borrower, sector, or geography |
| **Case Note** | A documented finding by a compliance officer, including facts, evidence, and recommended action |
| **Tipping Off** | Alerting a suspect that they are under investigation; strictly prohibited under AML laws |

## Snowflake-Specific Terms

| Term | Definition |
|------|------------|
| **Dynamic Table** | A Snowflake table that automatically refreshes its contents based on a defining query and a target lag |
| **Cortex Analyst** | Snowflake's text-to-SQL service that converts natural language questions into SQL queries using a semantic view |
| **Cortex Search** | Snowflake's hybrid search service for retrieving relevant text chunks from unstructured data |
| **Cortex Agent** | Snowflake's orchestration layer that routes questions to the right tools (Analyst, Search, custom functions) |
| **Semantic View** | A Snowflake object that defines tables, columns, metrics, and verified queries for Cortex Analyst |
| **MCP Server** | A Snowflake-managed server that exposes Cortex tools (Agent, Analyst, Search, custom functions) via the MCP protocol |
| **Masking Policy** | A Snowflake object that conditionally transforms column values based on the executing role |
| **Object Tag** | A Snowflake metadata label applied to databases, schemas, tables, or columns for classification |
| **Streamlit in Snowflake** | Snowflake's hosted environment for running Streamlit Python applications on warehouse compute |
| **Agent Skill** | A SKILL.md file on a Snowflake stage that provides domain-specific instructions to a Cortex Agent |
| **Target Lag** | The maximum acceptable delay between source data changes and Dynamic Table refresh |
