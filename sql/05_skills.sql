-- ============================================================
-- RiskLens — Skills (SQL Table Functions)
-- ============================================================

-- Skill 1: Fraud Signal Detection
CREATE OR REPLACE FUNCTION RISKLENS.CORE.SKILL_FRAUD_DETECTION(P_ACCOUNT_ID VARCHAR)
RETURNS TABLE (
    ACCOUNT_ID VARCHAR, TOTAL_SIGNALS INT, CRITICAL_SIGNALS INT, HIGH_SIGNALS INT,
    RISK_SCORE INT, RISK_LEVEL VARCHAR, SIGNAL_DETAILS ARRAY, REASON_CODES ARRAY, RECOMMENDATION VARCHAR
)
LANGUAGE SQL AS $$
    WITH signal_summary AS (
        SELECT ENTITY_ID, COUNT(*) AS total_signals,
            SUM(CASE WHEN SEVERITY = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_signals,
            SUM(CASE WHEN SEVERITY = 'HIGH' THEN 1 ELSE 0 END) AS high_signals,
            ARRAY_AGG(OBJECT_CONSTRUCT('signal_type', SIGNAL_TYPE, 'severity', SEVERITY,
                'rule_id', RULE_ID, 'evidence', EVIDENCE_JSON, 'detected_at', DETECTED_AT::VARCHAR)) AS signal_details,
            ARRAY_AGG(DISTINCT SIGNAL_TYPE) AS reason_codes
        FROM RISKLENS.SIGNALS.DT_CONSOLIDATED_ALERTS WHERE ENTITY_ID = P_ACCOUNT_ID GROUP BY ENTITY_ID
    )
    SELECT P_ACCOUNT_ID, COALESCE(s.total_signals, 0), COALESCE(s.critical_signals, 0), COALESCE(s.high_signals, 0),
        LEAST(100, COALESCE(s.critical_signals*30 + s.high_signals*15 + s.total_signals*5, 0)),
        CASE WHEN COALESCE(s.critical_signals*30+s.high_signals*15+s.total_signals*5,0) >= 80 THEN 'VERY_HIGH'
             WHEN COALESCE(s.critical_signals*30+s.high_signals*15+s.total_signals*5,0) >= 60 THEN 'HIGH'
             WHEN COALESCE(s.critical_signals*30+s.high_signals*15+s.total_signals*5,0) >= 30 THEN 'MEDIUM' ELSE 'LOW' END,
        s.signal_details, s.reason_codes,
        CASE WHEN COALESCE(s.critical_signals,0) > 0 THEN 'IMMEDIATE: Block account, file STR within 24 hours, escalate to MLRO and legal'
             WHEN COALESCE(s.high_signals,0) > 0 THEN 'URGENT: File STR within 7 days, upgrade risk rating, enhanced monitoring'
             WHEN COALESCE(s.total_signals,0) > 0 THEN 'MONITOR: Place on enhanced monitoring, review in next CDD cycle'
             ELSE 'NO_ACTION: No active signals detected' END
    FROM (SELECT 1 AS dummy) d LEFT JOIN signal_summary s ON 1=1
$$;

-- Skill 2: AML Pattern Matching
CREATE OR REPLACE FUNCTION RISKLENS.CORE.SKILL_AML_PATTERN_MATCH(P_ACCOUNT_ID VARCHAR)
RETURNS TABLE (
    ACCOUNT_ID VARCHAR, PATTERN_TYPE VARCHAR, PATTERN_DESCRIPTION VARCHAR,
    MATCHED_TRANSACTIONS INT, TOTAL_AMOUNT NUMBER(18,2), SEVERITY VARCHAR,
    APPLICABLE_RULE VARCHAR, REGULATORY_REFERENCE VARCHAR, POLICY_CLAUSE VARCHAR
)
LANGUAGE SQL AS $$
    SELECT P_ACCOUNT_ID, 'STRUCTURING',
        'Multiple cash deposits below $10,000 CTR threshold within 72 hours',
        COUNT(*), SUM(AMOUNT), 'HIGH', 'RR-001: Structuring Detection',
        'BSA/AML - 31 CFR 1010.311',
        'Internal AML/CFT Policy v3.2, Section 3(a): Structuring - multiple cash transactions just below the $10,000 CTR reporting threshold within 72 hours'
    FROM RISKLENS.CORE.TRANSACTIONS
    WHERE ACCOUNT_ID = P_ACCOUNT_ID AND TXN_CATEGORY = 'CASH_DEPOSIT'
      AND AMOUNT BETWEEN 8000 AND 9999 AND TXN_TIMESTAMP >= DATEADD(HOUR, -72, CURRENT_TIMESTAMP())
    HAVING COUNT(*) >= 3
    UNION ALL
    SELECT P_ACCOUNT_ID, 'LAYERING',
        'Rapid pass-through: funds received and moved out within hours via wire transfers',
        cr.cnt + db.cnt, GREATEST(cr.total_amt, db.total_amt), 'HIGH', 'RR-002: Rapid Layering',
        'FATF Recommendation 20',
        'Internal AML/CFT Policy v3.2, Section 3(b): Rapid movement (layering) - funds received and transferred out within 24 hours with >80% passthrough ratio'
    FROM (SELECT COUNT(*) cnt, SUM(AMOUNT) total_amt FROM RISKLENS.CORE.TRANSACTIONS
          WHERE ACCOUNT_ID=P_ACCOUNT_ID AND TXN_TYPE='CREDIT' AND TXN_CATEGORY='WIRE_TRANSFER'
            AND TXN_TIMESTAMP >= DATEADD(HOUR,-24,CURRENT_TIMESTAMP())) cr,
         (SELECT COUNT(*) cnt, SUM(AMOUNT) total_amt FROM RISKLENS.CORE.TRANSACTIONS
          WHERE ACCOUNT_ID=P_ACCOUNT_ID AND TXN_TYPE='DEBIT' AND TXN_CATEGORY='WIRE_TRANSFER'
            AND TXN_TIMESTAMP >= DATEADD(HOUR,-24,CURRENT_TIMESTAMP())) db
    WHERE cr.cnt >= 3 AND db.cnt >= 3 AND db.total_amt/NULLIF(cr.total_amt,0) > 0.8
    UNION ALL
    SELECT P_ACCOUNT_ID, 'WATCHLIST_MATCH',
        'Transaction counterparty matches sanctioned/watchlisted entity: ' || w.ENTITY_NAME,
        COUNT(*), SUM(t.AMOUNT), 'CRITICAL', 'RR-005: Watchlist Match',
        'OFAC Compliance Requirements / ' || w.LIST_SOURCE,
        'Internal AML/CFT Policy v3.2, Section 5: Sanctions Screening - True matches must be escalated immediately. Transactions must be blocked and reported within 24 hours.'
    FROM RISKLENS.CORE.TRANSACTIONS t JOIN RISKLENS.CORE.WATCHLIST w ON t.COUNTERPARTY_NAME ILIKE '%' || w.ENTITY_NAME || '%'
    WHERE t.ACCOUNT_ID = P_ACCOUNT_ID AND w.IS_ACTIVE = TRUE GROUP BY w.ENTITY_NAME, w.LIST_SOURCE
    UNION ALL
    SELECT P_ACCOUNT_ID, 'FAN_OUT',
        'Single account distributing funds to 20+ unique recipients within 24 hours',
        COUNT(*), SUM(AMOUNT), 'HIGH', 'RR-004: Fan-Out Transfers', 'FATF Red Flag Indicators',
        'Internal AML/CFT Policy v3.2, Section 3(f): Fan-out patterns - single account distributing funds to 20+ unique recipients within 24 hours'
    FROM RISKLENS.CORE.TRANSACTIONS
    WHERE ACCOUNT_ID=P_ACCOUNT_ID AND TXN_TYPE='DEBIT' AND TXN_TIMESTAMP >= DATEADD(HOUR,-24,CURRENT_TIMESTAMP())
    HAVING COUNT(DISTINCT COUNTERPARTY_ACCOUNT) >= 20
$$;

-- Skill 3: Basel Metric Computation (LCR, NPA, Provision Coverage — all in SQL)
CREATE OR REPLACE FUNCTION RISKLENS.CORE.SKILL_BASEL_METRICS(P_POSITION_DATE DATE DEFAULT CURRENT_DATE(), P_STRESS_SCENARIO VARCHAR DEFAULT 'BASE')
RETURNS TABLE (
    METRIC_NAME VARCHAR, METRIC_VALUE NUMBER(18,2), THRESHOLD NUMBER(18,2),
    STATUS VARCHAR, COMPONENTS OBJECT, REGULATORY_REFERENCE VARCHAR, COMPUTATION_NOTE VARCHAR
)
LANGUAGE SQL AS $$
    WITH lcr_components AS (
        SELECT SUM(CASE WHEN CATEGORY='HQLA_L1' THEN AMOUNT*(1-HAIRCUT_PCT/100) ELSE 0 END) AS hqla_l1,
            SUM(CASE WHEN CATEGORY='HQLA_L2A' THEN AMOUNT*(1-HAIRCUT_PCT/100) ELSE 0 END) AS hqla_l2a,
            SUM(CASE WHEN CATEGORY='HQLA_L2B' THEN AMOUNT*(1-HAIRCUT_PCT/100) ELSE 0 END) AS hqla_l2b,
            SUM(CASE WHEN CATEGORY='CASH_OUTFLOW' THEN AMOUNT*RUNOFF_RATE_PCT/100 ELSE 0 END) AS total_outflows,
            SUM(CASE WHEN CATEGORY='CASH_INFLOW' THEN AMOUNT ELSE 0 END) AS total_inflows
        FROM RISKLENS.CORE.POSITIONS WHERE POSITION_DATE=P_POSITION_DATE AND STRESS_SCENARIO=P_STRESS_SCENARIO
    ), lcr_calc AS (
        SELECT *, hqla_l1+hqla_l2a+hqla_l2b AS total_hqla,
            total_outflows-LEAST(total_inflows,total_outflows*0.75) AS net_outflows,
            ROUND((hqla_l1+hqla_l2a+hqla_l2b)/NULLIF(total_outflows-LEAST(total_inflows,total_outflows*0.75),0)*100,2) AS lcr_ratio
        FROM lcr_components
    ), credit_metrics AS (
        SELECT ROUND(SUM(CASE WHEN NPA_FLAG THEN OUTSTANDING_AMOUNT ELSE 0 END)/NULLIF(SUM(OUTSTANDING_AMOUNT),0)*100,2) AS npa_ratio,
            SUM(OUTSTANDING_AMOUNT) AS total_outstanding, SUM(CASE WHEN NPA_FLAG THEN OUTSTANDING_AMOUNT ELSE 0 END) AS npa_amount,
            SUM(PROVISION_AMOUNT) AS total_provisions,
            ROUND(SUM(PROVISION_AMOUNT)/NULLIF(SUM(CASE WHEN NPA_FLAG THEN OUTSTANDING_AMOUNT ELSE 0 END),0)*100,2) AS provision_coverage
        FROM RISKLENS.CORE.LOANS
    )
    SELECT 'LCR', lcr_ratio, 100.00,
        CASE WHEN lcr_ratio >= 110 THEN 'GREEN' WHEN lcr_ratio >= 100 THEN 'AMBER' ELSE 'RED' END,
        OBJECT_CONSTRUCT('hqla_l1',hqla_l1,'hqla_l2a',hqla_l2a,'total_hqla',total_hqla,
            'total_outflows',total_outflows,'net_outflows',net_outflows,'stress_scenario',P_STRESS_SCENARIO),
        'Basel III LCR Framework - Min 100%; Internal min 110%',
        'LCR = HQLA / Net Outflows (30d stress). Inflows capped at 75% of outflows.'
    FROM lcr_calc
    UNION ALL
    SELECT 'GROSS_NPA_RATIO', npa_ratio, 5.00,
        CASE WHEN npa_ratio <= 3 THEN 'GREEN' WHEN npa_ratio <= 5 THEN 'AMBER' ELSE 'RED' END,
        OBJECT_CONSTRUCT('total_outstanding',total_outstanding,'npa_amount',npa_amount,'provisions',total_provisions),
        'RBI IRAC Norms - Board threshold 5%', 'NPA Ratio = Gross NPAs / Gross Advances * 100'
    FROM credit_metrics
    UNION ALL
    SELECT 'PROVISION_COVERAGE', provision_coverage, 70.00,
        CASE WHEN provision_coverage >= 70 THEN 'GREEN' WHEN provision_coverage >= 50 THEN 'AMBER' ELSE 'RED' END,
        OBJECT_CONSTRUCT('provisions',total_provisions,'npa_amount',npa_amount),
        'RBI guidelines - Min 70% coverage recommended', 'PCR = Provisions / Gross NPAs * 100'
    FROM credit_metrics
$$;

-- Live Regulatory Lookup
CREATE OR REPLACE FUNCTION RISKLENS.REGULATORY.LIVE_REGULATORY_LOOKUP(P_QUERY VARCHAR, P_SOURCE VARCHAR)
RETURNS TABLE (DOC_NAME VARCHAR, SECTION VARCHAR, CHUNK_TEXT VARCHAR, SOURCE_URL VARCHAR, RETRIEVAL_TIMESTAMP VARCHAR, IS_CACHED BOOLEAN)
LANGUAGE SQL AS $$
    SELECT DOC_NAME, SECTION, CHUNK_TEXT,
        CASE P_SOURCE WHEN 'RBI' THEN 'https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx'
            WHEN 'FATF' THEN 'https://www.fatf-gafi.org/en/recommendations.html'
            WHEN 'BASEL' THEN 'https://www.bis.org/bcbs/publ/d295.htm'
            ELSE 'https://docs.regulatory-source.example.com' END,
        CURRENT_TIMESTAMP()::VARCHAR, TRUE
    FROM RISKLENS.REGULATORY.REGULATORY_CHUNKS
    WHERE CHUNK_TEXT ILIKE '%' || P_QUERY || '%' OR SECTION ILIKE '%' || P_QUERY || '%' OR DOC_NAME ILIKE '%' || P_QUERY || '%'
    LIMIT 5
$$;
