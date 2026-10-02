import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="RiskLens", layout="wide")
session = get_active_session()

# ── Styling ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Modern font stack */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    code, pre, div[data-testid="stCode"] {
        font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
    }

    /* Tighten layout */
    .block-container { padding-top: 1.2rem; padding-bottom: 0; }

    /* Metric cards */
    div[data-testid="stMetricValue"] > div {
        font-size: 28px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #6b7280 !important;
    }
    div[data-testid="stMetricDelta"] > div {
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* Table styling */
    table {
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    thead tr th {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 10px 14px !important;
        border: none !important;
        position: sticky;
        top: 0;
    }
    thead tr th:first-child { border-radius: 8px 0 0 0; }
    thead tr th:last-child { border-radius: 0 8px 0 0; }
    tbody tr td {
        padding: 8px 14px !important;
        border-bottom: 1px solid #e5e7eb !important;
        font-size: 13px !important;
    }
    tbody tr:hover td {
        background-color: #f0f4ff !important;
    }
    tbody tr:last-child td:first-child { border-radius: 0 0 0 8px; }
    tbody tr:last-child td:last-child { border-radius: 0 0 8px 0; }

    /* Dataframe container */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Chart container */
    div[data-testid="stVegaLiteChart"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 8px;
        background: #fafbfc;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* Section titles */
    h4, h5 {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.3px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] h2 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Citation box */
    .cite-box {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 13px;
        line-height: 1.6;
        color: #1e3a5f;
    }

    /* Info/success/warning boxes */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 14px !important;
    }

    /* Buttons */
    button[kind="primary"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        background: #1e293b !important;
        color: #94a3b8 !important;
        padding: 9px 14px !important;
        margin-bottom: 2px !important;
        text-align: center !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: #334155 !important;
        color: #f1f5f9 !important;
    }
    /* Hide the disabled button (active page shown via HTML instead) */
    section[data-testid="stSidebar"] button[disabled] {
        display: none !important;
    }

    /* Main buttons */
    button[kind="primary"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }

    /* Expander */
    details {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    details summary {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def run_query(sql):
    return session.sql(sql).to_pandas()


def log_to_audit(question, generated_sql, model_used, response_text):
    try:
        safe_q = question.replace("'", "''")[:2000]
        safe_r = (response_text or "").replace("'", "''")[:5000]
        safe_sql = (generated_sql or "").replace("'", "''")[:5000]
        session.sql(
            f"""INSERT INTO RISKLENS.AUDIT.COPILOT_AUDIT_LOG
                (SESSION_ID, USER_NAME, USER_ROLE, QUESTION_TEXT, GENERATED_SQL,
                 MODEL_USED, RESPONSE_TEXT)
                SELECT '{uuid.uuid4()}', CURRENT_USER(), CURRENT_ROLE(),
                       '{safe_q}', '{safe_sql}', '{model_used}', '{safe_r}'"""
        ).collect()
    except Exception:
        pass


def styled_table(df, accent_col=None, fmt_map=None):
    """Render a pandas DataFrame as a styled HTML table."""
    if df.empty:
        st.info("No data.")
        return
    html = '<div style="overflow-x:auto;margin-bottom:8px;">'
    html += '<table style="width:100%;border-collapse:collapse;">'
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th style="background:#1e40af;color:#ffffff;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;padding:9px 10px;border:1px solid #1e3a8a;">{col}</th>'
    html += '</tr></thead><tbody>'
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#f1f5f9" if i % 2 == 0 else "#ffffff"
        html += f'<tr style="background:{bg};">'
        for col in df.columns:
            val = row[col]
            style = f"padding:7px 10px;border:1px solid #e2e8f0;font-size:13px;color:#1e293b;"
            if fmt_map and col in fmt_map:
                val = fmt_map[col](val)
            if accent_col and col == accent_col:
                try:
                    fv = float(val) if not isinstance(val, str) else 0
                    if fv > 5:
                        style = f"padding:7px 10px;border:1px solid #e2e8f0;font-size:13px;color:#dc2626;font-weight:700;"
                    elif fv > 3:
                        style = f"padding:7px 10px;border:1px solid #e2e8f0;font-size:13px;color:#d97706;font-weight:700;"
                    else:
                        style = f"padding:7px 10px;border:1px solid #e2e8f0;font-size:13px;color:#16a34a;font-weight:700;"
                except (ValueError, TypeError):
                    pass
            html += f'<td style="{style}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)


# ── Sidebar ──
audit_count = run_query("SELECT COUNT(*) AS CNT FROM RISKLENS.AUDIT.COPILOT_AUDIT_LOG")
audit_n = int(audit_count.iloc[0]["CNT"]) if not audit_count.empty else 0
role_df = run_query("SELECT CURRENT_ROLE() AS R, CURRENT_USER() AS U")
user_role = role_df.iloc[0]["R"] if not role_df.empty else ""
user_name = role_df.iloc[0]["U"] if not role_df.empty else ""

# Logo + title — SVG female eye with lashes
st.sidebar.markdown("""
<div style="padding:18px 0 8px 0;text-align:center;">
    <div style="display:inline-block;width:56px;height:56px;border-radius:14px;
                background:linear-gradient(135deg,#2563eb,#7c3aed);
                padding:8px;box-sizing:border-box;">
        <svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">
            <!-- Upper lashes -->
            <line x1="8" y1="18" x2="4" y2="8" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="13" y1="15" x2="10" y2="5" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="20" y1="13" x2="20" y2="3" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="27" y1="15" x2="30" y2="5" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="32" y1="18" x2="36" y2="8" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
            <!-- Eye shape -->
            <path d="M4 22 Q20 8 36 22 Q20 34 4 22 Z" fill="none" stroke="#fff" stroke-width="2"/>
            <!-- Iris -->
            <circle cx="20" cy="22" r="7" fill="#a78bfa"/>
            <!-- Pupil -->
            <circle cx="20" cy="22" r="3.5" fill="#1e1b4b"/>
            <!-- Pupil highlight -->
            <circle cx="22" cy="20" r="1.5" fill="#fff" opacity="0.9"/>
            <!-- Lower lash line -->
            <path d="M8 26 Q20 32 32 26" fill="none" stroke="#fff" stroke-width="1" opacity="0.5"/>
        </svg>
    </div>
    <div style="margin-top:8px;font-size:20px;font-weight:700;color:#f1f5f9;
                letter-spacing:-0.5px;">RiskLens</div>
    <div style="font-size:10px;color:#94a3b8;font-weight:500;letter-spacing:1.5px;
                text-transform:uppercase;margin-top:2px;">Compliance Copilot</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin:12px 0;height:1px;background:linear-gradient(90deg,transparent,#334155,transparent);"></div>', unsafe_allow_html=True)

# Navigation with active indicator
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"

NAV = [
    ("Dashboard",         "📊"),
    ("Investigation",     "🔎"),
    ("Evidence & Skills", "🧬"),
    ("Report Generator",  "📋"),
]

for label, icon in NAV:
    is_active = st.session_state.nav_page == label
    if is_active:
        st.sidebar.markdown(
            f'<div style="background:#2563eb;color:#fff;font-size:13px;font-weight:600;'
            f'padding:9px 14px;border-radius:10px;margin-bottom:4px;text-align:center;">'
            f'{icon}  {label}</div>',
            unsafe_allow_html=True,
        )
    if st.sidebar.button(
        f"{icon}  {label}" if not is_active else f"   {label}  ✓",
        key=f"nav_{label}",
        use_container_width=True,
        disabled=is_active,
    ):
        st.session_state.nav_page = label
        st.experimental_rerun()

page = st.session_state.nav_page

st.sidebar.markdown('<div style="margin:12px 0;height:1px;background:linear-gradient(90deg,transparent,#334155,transparent);"></div>', unsafe_allow_html=True)

# Audit card
st.sidebar.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px 16px;margin-bottom:10px;">
    <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:#94a3b8;">
        Audit Trail</div>
    <div style="font-size:26px;font-weight:700;color:#a78bfa;margin:4px 0 2px 0;">{audit_n}</div>
    <div style="font-size:11px;color:#94a3b8;">entries logged</div>
</div>
""", unsafe_allow_html=True)

# Session card
st.sidebar.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px 16px;margin-bottom:10px;">
    <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:#94a3b8;">
        Session</div>
    <div style="margin-top:8px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
            <span style="font-size:11px;color:#94a3b8;">Role</span>
            <span style="font-size:11px;color:#f1f5f9;font-weight:600;">{user_role}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="font-size:11px;color:#94a3b8;">User</span>
            <span style="font-size:11px;color:#f1f5f9;font-weight:600;">{user_name}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin:12px 0;height:1px;background:linear-gradient(90deg,transparent,#334155,transparent);"></div>', unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="text-align:center;padding:6px 0;">
    <div style="font-size:10px;color:#64748b;">Built with Snowflake Cortex</div>
    <div style="font-size:10px;color:#64748b;margin-top:2px;">AML/KYC · Basel III · Credit Risk</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════
if page == "Dashboard":

    st.markdown("#### Risk Overview")

    # Load data
    alerts_df = run_query(
        "SELECT SEVERITY, COUNT(*) AS CNT FROM RISKLENS.SIGNALS.DT_CONSOLIDATED_ALERTS GROUP BY SEVERITY"
    )
    total_alerts = int(alerts_df["CNT"].sum()) if not alerts_df.empty else 0
    crit = int(alerts_df.loc[alerts_df["SEVERITY"] == "CRITICAL", "CNT"].sum()) if not alerts_df.empty else 0
    high = int(alerts_df.loc[alerts_df["SEVERITY"] == "HIGH", "CNT"].sum()) if not alerts_df.empty else 0
    med = int(alerts_df.loc[alerts_df["SEVERITY"] == "MEDIUM", "CNT"].sum()) if not alerts_df.empty else 0

    metrics_df = run_query(
        "SELECT METRIC_NAME, METRIC_VALUE, STATUS FROM TABLE(RISKLENS.CORE.SKILL_BASEL_METRICS(CURRENT_DATE(), 'BASE'))"
    )
    lcr = npa = pcr = 0.0
    for _, r in metrics_df.iterrows():
        if r["METRIC_NAME"] == "LCR": lcr = float(r["METRIC_VALUE"])
        elif r["METRIC_NAME"] == "GROSS_NPA_RATIO": npa = float(r["METRIC_VALUE"])
        elif r["METRIC_NAME"] == "PROVISION_COVERAGE": pcr = float(r["METRIC_VALUE"])

    txn_cnt = int(run_query("SELECT COUNT(*) AS C FROM RISKLENS.CORE.TRANSACTIONS").iloc[0]["C"])

    # ── KPI Row 1: Alerts ──
    st.markdown("##### Signal Summary")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Total Alerts", f"{total_alerts}")
    a2.metric("Critical", f"{crit}", delta=f"{crit} need action", delta_color="inverse")
    a3.metric("High", f"{high}", delta=f"{high} urgent")
    a4.metric("Medium", f"{med}")

    # ── KPI Row 2: Regulatory Metrics ──
    st.markdown("##### Regulatory Metrics (SQL-computed)")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("LCR (Basel III)", f"{lcr:.0f}%",
              delta="Compliant" if lcr >= 100 else "BREACH", delta_color="normal" if lcr >= 100 else "inverse")
    r2.metric("NPA Ratio", f"{npa:.1f}%",
              delta="Above 5% threshold" if npa > 5 else "Within limit",
              delta_color="inverse" if npa > 5 else "normal")
    r3.metric("Provision Coverage", f"{pcr:.1f}%",
              delta="Below 70% target" if pcr < 70 else "Adequate",
              delta_color="inverse" if pcr < 70 else "normal")
    r4.metric("Transactions (90d)", f"{txn_cnt:,}")

    st.markdown("---")

    # ── Charts ──
    st.markdown("##### Signal Distribution & Trends")
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("**Alerts by Signal Type**")
        type_df = run_query(
            "SELECT SIGNAL_TYPE, COUNT(*) AS COUNT FROM RISKLENS.SIGNALS.DT_CONSOLIDATED_ALERTS GROUP BY SIGNAL_TYPE ORDER BY COUNT DESC"
        )
        if not type_df.empty:
            st.bar_chart(type_df.set_index("SIGNAL_TYPE"))

    with ch2:
        st.markdown("**LCR Trend (30 Days)**")
        lcr_trend = run_query(
            "SELECT POSITION_DATE, LCR_RATIO FROM RISKLENS.SIGNALS.DT_LCR_MONITOR ORDER BY POSITION_DATE LIMIT 30"
        )
        if not lcr_trend.empty:
            st.line_chart(lcr_trend.set_index("POSITION_DATE"))

    st.markdown("---")

    # ── Bottom: Sector + DPD + Alert Queue ──
    st.markdown("##### Portfolio Health")
    p1, p2 = st.columns(2)

    with p1:
        st.markdown("**Sector Concentration & NPA**")
        sector_df = run_query(
            """SELECT SECTOR,
                      ROUND(SUM(OUTSTANDING_AMOUNT)/1e6, 1) AS AMT_M,
                      ROUND(SUM(OUTSTANDING_AMOUNT)/NULLIF((SELECT SUM(OUTSTANDING_AMOUNT) FROM RISKLENS.CORE.LOANS),0)*100,1) AS CONC,
                      ROUND(SUM(CASE WHEN NPA_FLAG THEN OUTSTANDING_AMOUNT ELSE 0 END)/NULLIF(SUM(OUTSTANDING_AMOUNT),0)*100,2) AS NPA
               FROM RISKLENS.CORE.LOANS GROUP BY SECTOR ORDER BY CONC DESC"""
        )
        if not sector_df.empty:
            styled_table(sector_df, accent_col="NPA")

    with p2:
        st.markdown("**DPD Distribution**")
        dpd_df = run_query(
            """SELECT DPD_BUCKET AS DPD, COUNT(*) AS LOANS, ROUND(SUM(OUTSTANDING_AMOUNT)/1e6,1) AS AMT_M
               FROM RISKLENS.CORE.LOANS GROUP BY DPD_BUCKET
               ORDER BY CASE DPD_BUCKET WHEN 'CURRENT' THEN 1 WHEN '1-30' THEN 2
                   WHEN '31-60' THEN 3 WHEN '61-90' THEN 4 WHEN '90+' THEN 5 END"""
        )
        if not dpd_df.empty:
            styled_table(dpd_df)

    st.markdown("---")

    st.markdown("##### Alert Queue")
    sev_filter = st.multiselect("Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                 default=["CRITICAL", "HIGH"], key="d_sev")
    if sev_filter:
        sev_list = ", ".join([f"'{s}'" for s in sev_filter])
        queue_df = run_query(
            f"""SELECT SIGNAL_TYPE, SEVERITY, ENTITY_ID, RULE_ID, DETECTED_AT
                FROM RISKLENS.SIGNALS.DT_CONSOLIDATED_ALERTS
                WHERE SEVERITY IN ({sev_list}) ORDER BY DETECTED_AT DESC LIMIT 30"""
        )
        if not queue_df.empty:
            styled_table(queue_df)


# ══════════════════════════════════════════════
# PAGE 2: INVESTIGATION
# ══════════════════════════════════════════════
elif page == "Investigation":
    st.markdown("#### Compliance Investigation")
    st.caption("Ask questions — the copilot cites policy and shows evidence.")

    SUGGESTIONS = [
        "How many active alerts are there by severity and signal type?",
        "Why was account ACC-00000050 flagged? Show the transactions and applicable policy.",
        "What is our current NPA ratio by sector? Which sectors are above 5%?",
        "What does our AML policy say about structuring detection?",
        "What is the current LCR and are we above the Basel III minimum of 100%?",
        "Show high-value international wire transfers over $50,000 in the last 7 days.",
    ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for entry in st.session_state.chat_history:
        st.info(f"**You:** {entry['question']}")
        st.success(f"**RiskLens:** {entry['answer']}")
        st.markdown("---")

    selected_q = st.selectbox("Quick questions:", ["(Type your own below)"] + SUGGESTIONS)
    user_input = st.text_input("Or type your question:")
    prompt = user_input.strip() if user_input.strip() else (selected_q if selected_q != "(Type your own below)" else "")

    if st.button("Ask RiskLens", type="primary") and prompt:
        with st.spinner("Analyzing..."):
            try:
                escaped = prompt.replace("'", "''")
                result = session.sql(
                    f"""SELECT SNOWFLAKE.CORTEX.COMPLETE(
                         'llama3.1-70b',
                         'You are RiskLens, a banking compliance copilot. '
                         || 'CRITICAL: Never compute numbers yourself - all numbers must come from SQL. '
                         || 'Always cite the specific policy section and regulatory reference. '
                         || 'Format with clear sections and bullet points. '
                         || 'Question: {escaped}'
                       ) AS RESPONSE"""
                ).to_pandas()
                response = result.iloc[0]["RESPONSE"]
            except Exception as e:
                response = f"Error: {str(e)}"

        log_to_audit(prompt, None, "llama3.1-70b", response)
        st.session_state.chat_history.append({"question": prompt, "answer": response})
        st.experimental_rerun()


# ══════════════════════════════════════════════
# PAGE 3: EVIDENCE & SKILLS
# ══════════════════════════════════════════════
elif page == "Evidence & Skills":
    st.markdown("#### Evidence Panel")
    st.caption("Run discrete SQL skills to gather structured, audit-ready evidence.")

    account_id = st.text_input("Account ID", value="ACC-00000050")
    safe_id = account_id.replace("'", "''")

    st.markdown("---")

    tab_fraud, tab_aml, tab_basel = st.tabs([
        "Fraud Detection",
        "AML Pattern Match",
        "Basel Metrics",
    ])

    with tab_fraud:
        if st.button("Run Fraud Detection", type="primary", key="btn_fraud"):
            with st.spinner("Running..."):
                df = run_query(f"SELECT * FROM TABLE(RISKLENS.CORE.SKILL_FRAUD_DETECTION('{safe_id}'))")
                if not df.empty:
                    row = df.iloc[0]
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("Risk Score", f"{row['RISK_SCORE']}/100")
                    f2.metric("Risk Level", row["RISK_LEVEL"])
                    f3.metric("Total Signals", int(row["TOTAL_SIGNALS"]))
                    f4.metric("Critical", int(row["CRITICAL_SIGNALS"]))

                    st.warning(f"**Recommendation:** {row['RECOMMENDATION']}")

                    if row["REASON_CODES"]:
                        codes = json.loads(row["REASON_CODES"])
                        st.markdown("**Reason Codes:** " + " | ".join(codes))

                    if row["SIGNAL_DETAILS"]:
                        st.markdown("**Signal Details:**")
                        styled_table(pd.DataFrame(json.loads(row["SIGNAL_DETAILS"])))

                    log_to_audit(f"SKILL_FRAUD_DETECTION({account_id})",
                                 f"SKILL_FRAUD_DETECTION('{safe_id}')", "SQL_SKILL", row["RECOMMENDATION"])
                else:
                    st.info("No signals detected for this account.")

    with tab_aml:
        if st.button("Run AML Pattern Match", type="primary", key="btn_aml"):
            with st.spinner("Running..."):
                df = run_query(
                    f"""SELECT PATTERN_TYPE, PATTERN_DESCRIPTION, MATCHED_TRANSACTIONS,
                               TOTAL_AMOUNT, SEVERITY, APPLICABLE_RULE, POLICY_CLAUSE, REGULATORY_REFERENCE
                        FROM TABLE(RISKLENS.CORE.SKILL_AML_PATTERN_MATCH('{safe_id}'))"""
                )
                if not df.empty:
                    for _, row in df.iterrows():
                        st.markdown(f"**{row['PATTERN_TYPE']}** — {row['SEVERITY']}")
                        c1, c2 = st.columns(2)
                        c1.metric("Matched Transactions", int(row["MATCHED_TRANSACTIONS"]))
                        c2.metric("Total Amount", f"${row['TOTAL_AMOUNT']:,.2f}")
                        st.markdown(f"**Description:** {row['PATTERN_DESCRIPTION']}")
                        st.markdown(f"**Rule:** {row['APPLICABLE_RULE']}")
                        st.markdown(f"**Regulatory Ref:** {row['REGULATORY_REFERENCE']}")
                        st.markdown(f'<div class="cite-box"><b>Policy Citation:</b> {row["POLICY_CLAUSE"]}</div>',
                                    unsafe_allow_html=True)
                        st.markdown("---")

                    log_to_audit(f"SKILL_AML_PATTERN_MATCH({account_id})",
                                 f"SKILL_AML_PATTERN_MATCH('{safe_id}')", "SQL_SKILL", f"{len(df)} patterns")
                else:
                    st.info("No AML patterns detected.")

    with tab_basel:
        if st.button("Run Basel Metrics", type="primary", key="btn_basel"):
            with st.spinner("Computing..."):
                df = run_query(
                    """SELECT METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS,
                              COMPONENTS, REGULATORY_REFERENCE, COMPUTATION_NOTE
                       FROM TABLE(RISKLENS.CORE.SKILL_BASEL_METRICS(CURRENT_DATE(), 'BASE'))"""
                )
                if not df.empty:
                    cols = st.columns(len(df))
                    for i, (_, row) in enumerate(df.iterrows()):
                        with cols[i]:
                            delta_txt = "OK" if row["STATUS"] == "GREEN" else "BREACH"
                            delta_clr = "normal" if row["STATUS"] == "GREEN" else "inverse"
                            st.metric(row["METRIC_NAME"], f"{row['METRIC_VALUE']:.1f}%",
                                      delta=f"vs {row['THRESHOLD']:.0f}% ({delta_txt})", delta_color=delta_clr)

                    for _, row in df.iterrows():
                        st.markdown(f"**{row['METRIC_NAME']}:** {row['REGULATORY_REFERENCE']}")
                        st.caption(row["COMPUTATION_NOTE"])
                        if row["COMPONENTS"]:
                            with st.expander(f"View {row['METRIC_NAME']} breakdown"):
                                st.json(json.loads(row["COMPONENTS"]))

                    log_to_audit("SKILL_BASEL_METRICS", "SKILL_BASEL_METRICS()", "SQL_SKILL", "computed")


# ══════════════════════════════════════════════
# PAGE 4: REPORT GENERATOR
# ══════════════════════════════════════════════
elif page == "Report Generator":
    st.markdown("#### Audit-Ready Report Generator")

    report_type = st.selectbox("Report Type", [
        "Suspicious Transaction Report (STR)",
        "LCR / Liquidity Summary",
        "Credit Risk Portfolio Summary",
    ])

    if report_type == "Suspicious Transaction Report (STR)":
        account_id = st.text_input("Account ID", value="ACC-00000050")

        if st.button("Generate STR", type="primary"):
            with st.spinner("Assembling evidence..."):
                safe_id = account_id.replace("'", "''")
                fraud_df = run_query(f"SELECT * FROM TABLE(RISKLENS.CORE.SKILL_FRAUD_DETECTION('{safe_id}'))")
                aml_df = run_query(f"SELECT * FROM TABLE(RISKLENS.CORE.SKILL_AML_PATTERN_MATCH('{safe_id}'))")
                cust_df = run_query(
                    f"""SELECT c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.RISK_RATING,
                               c.NATIONALITY, c.PEP_FLAG, c.OCCUPATION
                        FROM RISKLENS.CORE.CUSTOMERS c
                        JOIN RISKLENS.CORE.ACCOUNTS a ON c.CUSTOMER_ID = a.CUSTOMER_ID
                        WHERE a.ACCOUNT_ID = '{safe_id}'"""
                )
                txn_df = run_query(
                    f"""SELECT TXN_ID, TXN_TIMESTAMP, TXN_TYPE, TXN_CATEGORY, AMOUNT,
                               COUNTERPARTY_NAME, COUNTERPARTY_COUNTRY, CHANNEL
                        FROM RISKLENS.CORE.TRANSACTIONS
                        WHERE ACCOUNT_ID = '{safe_id}' ORDER BY TXN_TIMESTAMP DESC LIMIT 20"""
                )

                report_id = f"STR-{uuid.uuid4().hex[:8].upper()}"
                st.markdown(f"### Suspicious Transaction Report")
                st.caption(f"Report ID: {report_id} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Account: {account_id}")

                if not fraud_df.empty:
                    fr = fraud_df.iloc[0]
                    f1, f2, f3 = st.columns(3)
                    f1.metric("Risk Score", f"{fr['RISK_SCORE']}/100")
                    f2.metric("Risk Level", fr["RISK_LEVEL"])
                    f3.metric("Signals", int(fr["TOTAL_SIGNALS"]))

                st.markdown("---")

                if not cust_df.empty:
                    row = cust_df.iloc[0]
                    st.markdown("##### 1. Subject Information")
                    s1, s2, s3 = st.columns(3)
                    s1.markdown(f"**Name:** {row['FIRST_NAME']} {row['LAST_NAME']}")
                    s1.markdown(f"**Customer ID:** {row['CUSTOMER_ID']}")
                    s2.markdown(f"**Risk Rating:** {row['RISK_RATING']}")
                    s2.markdown(f"**Nationality:** {row['NATIONALITY']}")
                    s3.markdown(f"**PEP:** {'Yes' if row['PEP_FLAG'] else 'No'}")
                    s3.markdown(f"**Occupation:** {row['OCCUPATION']}")

                if not aml_df.empty:
                    st.markdown("##### 2. Suspicious Activity")
                    for _, p in aml_df.iterrows():
                        st.markdown(f"**{p['PATTERN_TYPE']}** ({p['SEVERITY']})")
                        st.markdown(f"- {p['PATTERN_DESCRIPTION']}")
                        st.markdown(f"- **{p['MATCHED_TRANSACTIONS']}** transactions totaling **${p['TOTAL_AMOUNT']:,.2f}**")
                        st.markdown(f"- Rule: {p['APPLICABLE_RULE']} | Ref: {p['REGULATORY_REFERENCE']}")
                        st.markdown(f'<div class="cite-box">{p["POLICY_CLAUSE"]}</div>', unsafe_allow_html=True)

                if not txn_df.empty:
                    st.markdown(f"##### 3. Supporting Transactions (${txn_df['AMOUNT'].sum():,.2f} total)")
                    styled_table(txn_df)

                if not fraud_df.empty:
                    st.markdown("##### 4. Recommendation")
                    st.warning(fraud_df.iloc[0]["RECOMMENDATION"])

                st.markdown("##### 5. Filing")
                st.markdown("File with FIU within **7 business days** | MLRO review required | Tipping off **prohibited** | Ref: AML/CFT Policy v3.2 Section 4")

                st.markdown("---")
                col_a, col_r, _ = st.columns([1, 1, 3])
                with col_a:
                    if st.button("Approve & File", type="primary"):
                        rec = fraud_df.iloc[0]["RECOMMENDATION"].replace("'", "''") if not fraud_df.empty else "Review"
                        session.sql(
                            f"""INSERT INTO RISKLENS.CORE.CASE_NOTES
                                (SIGNAL_TYPE, ENTITY_ID, ENTITY_TYPE, FACTS, RULE_TRIGGERED,
                                 EVIDENCE_SUMMARY, RECOMMENDED_ACTION, STATUS, CREATED_BY)
                                VALUES ('STR_FILING', '{safe_id}', 'ACCOUNT',
                                'STR {report_id} for {account_id}', 'Multiple rules',
                                'Full evidence chain via RiskLens', '{rec}',
                                'APPROVED', CURRENT_USER())"""
                        ).collect()
                        log_to_audit(f"STR APPROVED: {report_id}", "INSERT CASE_NOTES", "HUMAN", "Approved")
                        st.success(f"STR {report_id} APPROVED. Case note created. Audit log updated.")
                with col_r:
                    if st.button("Reject"):
                        log_to_audit(f"STR REJECTED: {report_id}", None, "HUMAN", "Rejected")
                        st.warning("Returned for review. Audit log updated.")

    elif report_type == "LCR / Liquidity Summary":
        if st.button("Generate LCR Report", type="primary"):
            with st.spinner("Computing..."):
                df = run_query(
                    """SELECT METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS,
                              COMPONENTS, REGULATORY_REFERENCE, COMPUTATION_NOTE
                       FROM TABLE(RISKLENS.CORE.SKILL_BASEL_METRICS(CURRENT_DATE(), 'BASE'))
                       WHERE METRIC_NAME = 'LCR'"""
                )
                if not df.empty:
                    row = df.iloc[0]
                    l1, l2 = st.columns(2)
                    l1.metric("LCR Ratio", f"{row['METRIC_VALUE']:.1f}%",
                              delta="Compliant" if row["METRIC_VALUE"] >= 100 else "BREACH",
                              delta_color="normal" if row["METRIC_VALUE"] >= 100 else "inverse")
                    l2.metric("Regulatory Min", "100%", delta="Basel III")

                    st.markdown(f"**Reference:** {row['REGULATORY_REFERENCE']}")
                    st.caption(row["COMPUTATION_NOTE"])

                    if row["COMPONENTS"]:
                        with st.expander("HQLA Components"):
                            st.json(json.loads(row["COMPONENTS"]))

                    lcr_trend = run_query(
                        "SELECT POSITION_DATE, LCR_RATIO FROM RISKLENS.SIGNALS.DT_LCR_MONITOR ORDER BY POSITION_DATE LIMIT 30"
                    )
                    if not lcr_trend.empty:
                        st.markdown("**LCR Trend**")
                        st.line_chart(lcr_trend.set_index("POSITION_DATE"))

                log_to_audit("LCR Report", "SKILL_BASEL_METRICS", "SQL_SKILL", "LCR report")

    elif report_type == "Credit Risk Portfolio Summary":
        if st.button("Generate Credit Report", type="primary"):
            with st.spinner("Analyzing..."):
                m_df = run_query(
                    """SELECT METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS
                       FROM TABLE(RISKLENS.CORE.SKILL_BASEL_METRICS(CURRENT_DATE(), 'BASE'))
                       WHERE METRIC_NAME IN ('GROSS_NPA_RATIO', 'PROVISION_COVERAGE')"""
                )
                if not m_df.empty:
                    cols = st.columns(len(m_df))
                    for i, (_, row) in enumerate(m_df.iterrows()):
                        with cols[i]:
                            st.metric(row["METRIC_NAME"], f"{row['METRIC_VALUE']:.1f}%",
                                      delta=f"vs {row['THRESHOLD']:.0f}%",
                                      delta_color="normal" if row["STATUS"] == "GREEN" else "inverse")

                s_df = run_query(
                    """SELECT SECTOR, COUNT(*) AS LOANS,
                              ROUND(SUM(OUTSTANDING_AMOUNT)/1e6,1) AS OUTSTANDING_M,
                              ROUND(SUM(OUTSTANDING_AMOUNT)/NULLIF(
                                  (SELECT SUM(OUTSTANDING_AMOUNT) FROM RISKLENS.CORE.LOANS),0)*100,1) AS CONC_PCT,
                              ROUND(SUM(CASE WHEN NPA_FLAG THEN OUTSTANDING_AMOUNT ELSE 0 END)
                                    /NULLIF(SUM(OUTSTANDING_AMOUNT),0)*100,2) AS NPA_PCT
                       FROM RISKLENS.CORE.LOANS GROUP BY SECTOR ORDER BY CONC_PCT DESC"""
                )
                st.markdown("**Sector Concentration & NPA**")
                if not s_df.empty:
                    styled_table(s_df, accent_col="NPA_PCT")

                d_df = run_query(
                    """SELECT DPD_BUCKET, COUNT(*) AS LOANS,
                              ROUND(SUM(OUTSTANDING_AMOUNT)/1e6,1) AS OUTSTANDING_M
                       FROM RISKLENS.CORE.LOANS GROUP BY DPD_BUCKET
                       ORDER BY CASE DPD_BUCKET WHEN 'CURRENT' THEN 1 WHEN '1-30' THEN 2
                           WHEN '31-60' THEN 3 WHEN '61-90' THEN 4 WHEN '90+' THEN 5 END"""
                )
                st.markdown("**DPD Distribution**")
                if not d_df.empty:
                    st.bar_chart(d_df.set_index("DPD_BUCKET")["LOANS"])

                log_to_audit("Credit Report", "Portfolio queries", "SQL_SKILL", "Credit report")
