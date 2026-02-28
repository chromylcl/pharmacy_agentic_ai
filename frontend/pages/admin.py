import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# 🔌 FETCH DATA (SWAP POINT)
# ══════════════════════════════════════════════════════════════════════════════

# SWAP THIS -- currently using dummy static data for the dashboard charts.
# When backend ready, replace this entire dummy block with:
#   from services.api_client import call_admin_stats
#   stats = call_admin_stats()
stats = {
    "inventory": {
      "Ibuprofen 400mg":   { "stock": 120, "restricted": False },
      "Oxycodone 10mg":    { "stock": 8,   "restricted": True  },
      "Paracetamol 500mg": { "stock": 45,  "restricted": False },
      "Amoxicillin 250mg": { "stock": 15,  "restricted": True  },
      "Loratadine 10mg":   { "stock": 0,   "restricted": False }
    },
    "avg_pdc_score": 0.72,
    "emergency_counts": {
      "chest pain":       4,
      "overdose":         2,
      "heart attack":     1,
      "stroke":           1,
      "allergic reaction": 0
    },
    "agent_latencies_ms": {
      "Pharmacist Agent":   1200,
      "Safety Agent":       980,
      "Fulfillment Agent":  750
    },
    "prescription_queue": [
      { "patient": "John Doe", "drug": "Oxycodone", "timestamp": "2026-02-28 14:32", "status": "pending" },
      { "patient": "Jane Smith", "drug": "Amoxicillin", "timestamp": "2026-02-28 09:15", "status": "approved" }
    ],
    "langfuse_metrics": {
      "total_tokens_today": 45200,
      "estimated_cost": "$0.45",
      "traces_logged": 142,
      "recent_traces": [
          {"trace_id": "lf_8a7b6c5", "intent": "Checkout Auth", "status": "Success"},
          {"trace_id": "lf_9d8e7f6", "intent": "Emergency Check", "status": "Diverted"},
          {"trace_id": "lf_1a2b3c4", "intent": "Symptom Check", "status": "Success"}
      ]
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("📊 Pharmacy Admin Dashboard")
    st.markdown("Live analytics, inventory tracking, and agent observability.")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.rerun()

st.markdown("---")

# Create Tabs for a cleaner UI
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", 
    "📦 Inventory", 
    "🛡️ Security & Rx", 
    "🧠 Langfuse Observability"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW (PDC & Emergencies)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("📈 Clinic PDC Risk Score")
        st.caption("Proportion of Days Covered (Average across all patients)")
        
        pdc = stats.get("avg_pdc_score", 0.0)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pdc * 100,
            number = {"suffix": "%", "font": {"color": "#e2e8f0"}},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "rgba(255,255,255,0.8)", 'thickness': 0.2},
                'bgcolor': "rgba(255,255,255,0.05)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': "#ef4444"},   # Vibrant Rose/Red
                    {'range': [50, 80], 'color': "#f59e0b"},  # Vibrant Amber
                    {'range': [80, 100], 'color': "#10b981"}  # Vibrant Emerald
                ],
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#e2e8f0"})
        st.plotly_chart(fig_gauge, use_container_width=True)

    with row2_col2:
        st.subheader("🚨 Red Route Analytics")
        st.caption("Emergency bypass triggers by keyword")
        
        em_data = stats.get("emergency_counts", {})
        df_em = pd.DataFrame(list(em_data.items()), columns=['Keyword', 'Triggers'])
        
        fig_bar = px.bar(df_em, x='Keyword', y='Triggers', text='Triggers')
        fig_bar.update_traces(
            marker_color='#f43f5e',           # Sleek Rose/Crimson
            marker_line_color='#be123c',      # Darker border
            marker_line_width=1.5, 
            opacity=0.85,
            textposition='outside',
            textfont_color='#e2e8f0'
        )
        fig_bar.update_layout(
            height=300, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="#94a3b8"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94a3b8")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: INVENTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📦 Live Stock Levels")
    
    inv_data = stats.get("inventory", {})
    df_inv = pd.DataFrame([
        {"Drug": name, "Stock": data["stock"], "Restricted": "Yes" if data["restricted"] else "No"}
        for name, data in inv_data.items()
    ])
    
    fig_inv = px.bar(
        df_inv, y='Drug', x='Stock', color='Stock', 
        orientation='h',
        color_continuous_scale=[(0, "#ef4444"), (0.5, "#f59e0b"), (1, "#10b981")], # Upgraded gradient
        range_color=[0, 100], text='Stock'
    )
    fig_inv.update_traces(
        marker_line_width=0, 
        textfont_color="white",
        textposition="inside"
    )
    fig_inv.update_layout(
        height=350, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        showlegend=False,
        coloraxis_showscale=False, # Hides the bulky color bar
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94a3b8"),
        yaxis=dict(showgrid=False, color="#e2e8f0", title="")
    )

    # Export Feature
    csv_inv = df_inv.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Inventory Report (CSV)", data=csv_inv, file_name="inventory_report.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: SECURITY & PRESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📋 Prescription Verification Queue")
    st.caption("Pending uploads for restricted drugs")
    
    queue_data = stats.get("prescription_queue", [])
    if not queue_data:
        st.info("No pending prescriptions to review.")
    else:
        df_queue = pd.DataFrame(queue_data)
        
        def highlight_pending(val):
            return 'background-color: #D97706; color: white;' if val == 'pending' else ''
            
        styled_queue = df_queue.style.applymap(highlight_pending, subset=['status'])
        st.dataframe(styled_queue, use_container_width=True, hide_index=True)

        # Export Feature
        csv_queue = df_queue.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Prescription Log (CSV)", data=csv_queue, file_name="rx_log.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: LANGFUSE OBSERVABILITY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🧠 LLM Performance & Tracing")
    st.caption("Powered by Langfuse")
    
    lf_metrics = stats.get("langfuse_metrics", {})
    latencies = stats.get("agent_latencies_ms", {})
    
    # Row 1: High Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("API Latency (Avg)", f"{(sum(latencies.values()) / len(latencies)):.0f} ms")
    m2.metric("Total Tokens (24h)", f"{lf_metrics.get('total_tokens_today', 0):,}")
    m3.metric("Est. LLM Cost", lf_metrics.get('estimated_cost', '$0.00'))
    m4.metric("Traces Logged", lf_metrics.get('traces_logged', 0))

    st.markdown("---")
    
    # Row 2: Latency per Agent & Trace Logs
    lf_col1, lf_col2 = st.columns([1, 1.5])
    
    with lf_col1:
        st.markdown("**Latency Breakdown (ms)**")
        df_lat = pd.DataFrame(list(latencies.items()), columns=["Agent", "Latency"])
        fig_lat = px.line_polar(df_lat, r='Latency', theta='Agent', line_close=True)
        fig_lat.update_traces(
            fill='toself', 
            fillcolor='rgba(124, 58, 237, 0.25)', # Transparent brand purple
            line_color='#a78bfa',                 # Bright violet glowing edge
            line_width=3
        )
        fig_lat.update_layout(
            height=270, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            margin=dict(t=30, b=30, l=30, r=30),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(showticklabels=False, gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0)'),
                angularaxis=dict(color="#e2e8f0", gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0)')
            )
        )
        st.plotly_chart(fig_lat, use_container_width=True)
        
    with lf_col2:
        st.markdown("**Recent Trace Logs**")
        df_traces = pd.DataFrame(lf_metrics.get("recent_traces", []))
        st.dataframe(df_traces, use_container_width=True, hide_index=True)
        
        # Open Real Langfuse Dashboard Button
        st.markdown(
            """
            <a href="https://cloud.langfuse.com" target="_blank">
                <button style="background-color:#1a0a2e; color:white; border:1px solid #7C3AED; padding:8px 16px; border-radius:6px; cursor:pointer;">
                    ↗ Open Langfuse Cloud
                </button>
            </a>
            """, unsafe_allow_html=True
        )