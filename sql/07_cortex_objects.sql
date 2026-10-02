-- ============================================================
-- RiskLens — Cortex Search, Semantic View, Agent, MCP Server
-- ============================================================

-- Cortex Search Service
CREATE OR REPLACE CORTEX SEARCH SERVICE RISKLENS.REGULATORY.POLICY_SEARCH
    ON CHUNK_TEXT
    ATTRIBUTES DOC_NAME, DOC_TYPE, SECTION
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    AS (SELECT CHUNK_ID, DOC_NAME, DOC_TYPE, SECTION, CHUNK_TEXT FROM RISKLENS.REGULATORY.REGULATORY_CHUNKS);

-- Semantic View: generated via CoCo CLI
-- cortex agent-studio sv-generate --file-path /tmp/risklens_proto.json --out-path /tmp/risklens_response.json
-- cortex agent-studio sv-deploy --file-path RISKLENS_COMPLIANCE.sv.yaml --fqn RISKLENS.CORE.RISKLENS_COMPLIANCE

-- Agent
-- Created via: cortex agent-studio agent-deploy --file-path COMPLIANCE_COPILOT.agent.yaml --fqn RISKLENS.CORE.COMPLIANCE_COPILOT
-- See agent_spec.yaml for full specification

-- MCP Server
CREATE OR REPLACE MCP SERVER RISKLENS.CORE.RISKLENS_MCP
  FROM SPECIFICATION $$
  tools:
    - title: "RiskLens Compliance Copilot"
      name: "compliance_copilot"
      type: "CORTEX_AGENT_RUN"
      identifier: "RISKLENS.CORE.COMPLIANCE_COPILOT"
      description: "Governed compliance copilot for banking risk."
    - title: "Policy & Regulatory Search"
      name: "policy_search"
      type: "CORTEX_SEARCH_SERVICE_QUERY"
      identifier: "RISKLENS.REGULATORY.POLICY_SEARCH"
      description: "Search AML/CFT policies, Basel III, RBI KYC directions."
    - title: "Fraud Detection Skill"
      name: "fraud_detection"
      type: "GENERIC"
      description: "Run fraud signal detection on an account."
      config:
        type: "function"
        warehouse: "COMPUTE_WH"
        input_schema:
          type: "object"
          properties:
            P_ACCOUNT_ID:
              type: "string"
          required: ["P_ACCOUNT_ID"]
      identifier: "RISKLENS.CORE.SKILL_FRAUD_DETECTION"
    - title: "AML Pattern Matching"
      name: "aml_pattern_match"
      type: "GENERIC"
      description: "Match account against AML typologies."
      config:
        type: "function"
        warehouse: "COMPUTE_WH"
        input_schema:
          type: "object"
          properties:
            P_ACCOUNT_ID:
              type: "string"
          required: ["P_ACCOUNT_ID"]
      identifier: "RISKLENS.CORE.SKILL_AML_PATTERN_MATCH"
    - title: "Basel Metric Computation"
      name: "basel_metrics"
      type: "GENERIC"
      description: "Compute LCR, NPA ratio, provision coverage in SQL."
      config:
        type: "function"
        warehouse: "COMPUTE_WH"
        input_schema:
          type: "object"
          properties:
            P_POSITION_DATE:
              type: "string"
            P_STRESS_SCENARIO:
              type: "string"
          required: []
      identifier: "RISKLENS.CORE.SKILL_BASEL_METRICS"
  $$;

-- Streamlit App
CREATE OR REPLACE STAGE RISKLENS.CORE.STREAMLIT_STAGE DIRECTORY = (ENABLE = TRUE) ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
-- PUT file://streamlit/streamlit_app.py @RISKLENS.CORE.STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
CREATE OR REPLACE STREAMLIT RISKLENS.CORE.RISKLENS_APP
    ROOT_LOCATION = '@RISKLENS.CORE.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = COMPUTE_WH
    TITLE = 'RiskLens Compliance Copilot';
