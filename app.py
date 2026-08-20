import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import logging
import sys
import os
import io
from datetime import datetime
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_option_menu import option_menu

# --- Setup ---
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
sys.stderr = open(os.devnull, 'w')

# =============================================================
# PAGE CONFIG & MATERIAL-STYLE CSS
# =============================================================
st.set_page_config(
    page_title="Ultimate ETF Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Material-like CSS (Dark/Light adaptive)
st.markdown("""
<style>
    /* Global reset */
    .main { padding: 0; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1a237e, #0d47a1);
        padding: 1.2rem 2rem;
        border-radius: 20px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        margin-bottom: 1.5rem;
    }
    .app-header h1 { margin: 0; font-size: 2rem; font-weight: 500; letter-spacing: 0.5px; }
    .app-header .subtitle { font-size: 0.9rem; opacity: 0.85; }

    /* Metric Cards (Material-like) */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
        border-bottom: 4px solid #3f51b5;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #757575;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-top: 0.2rem;
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #1e293b;
            border-bottom-color: #5c6bc0;
        }
        .metric-card .label { color: #94a3b8; }
        .metric-card .value { color: #f1f5f9; }
        .app-header { background: linear-gradient(135deg, #0f172a, #1e293b); }
    }

    /* Sidebar styling */
    .css-1d391kg { background-color: #f8f9fa; }
    .css-1d391kg .stSelectbox, .css-1d391kg .stRadio { margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# =============================================================
# SIDEBAR WITH OPTION MENU
# =============================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/stock.png", width=80)
    st.title("📊 ETF Scanner")
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "ETF Ranking", "RRG Chart", "About"],
        icons=["house", "table", "bar-chart", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#3f51b5", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px 0"},
            "nav-link-selected": {"background-color": "#3f51b5", "font-weight": "600"},
        }
    )
    st.markdown("---")
    st.caption(f"🔄 Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# =============================================================
# 1. STATIC ETF LIST & MAPPING (EXACT ORIGINAL – compressed)
# =============================================================
# (Full ETF_LIST, ETF_SECTOR_MAP, MACRO_SECTOR_MAP – same as before)
# For brevity, assume they are defined here (copy from previous code).
# =============================================================

SCAN_ETFS = [e for e in ETF_LIST if e not in ["LIQUIDCASE", "GROWWLIQID"]]

# =============================================================
# 2. HELPER FUNCTIONS (same as original – omitted for space)
# =============================================================
# (calculate_rsi, supertrend, get_obv, etc. – paste the exact code from earlier)

# =============================================================
# 3. MAIN SCAN FUNCTION (cached)
# =============================================================
@st.cache_data(ttl=3600)
def run_scan_cached():
    # This is identical to the previous working version
    # (returns display_df, macro_avg, warnings_list)
    # We'll include the full body from the last fixed version.
    pass

# =============================================================
# 4. AUTO-RUN ON LOAD
# =============================================================
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.display_df = None
    st.session_state.macro_avg = None
    st.session_state.warnings = []

if not st.session_state.data_loaded:
    with st.spinner("🚀 Scanning all ETFs..."):
        display_df, macro_avg, warnings_list = run_scan_cached()
        if display_df is not None:
            st.session_state.display_df = display_df
            st.session_state.macro_avg = macro_avg
            st.session_state.warnings = warnings_list
            st.session_state.data_loaded = True
            st.rerun()
        else:
            st.error("No data found.")
            st.stop()

# =============================================================
# 5. DISPLAY BASED ON SIDEBAR SELECTION
# =============================================================
display_df = st.session_state.display_df
macro_avg = st.session_state.macro_avg

if selected == "Dashboard":
    # Header
    st.markdown("""
    <div class="app-header">
        <div>
            <h1>📈 Ultimate ETF Scanner</h1>
            <div class="subtitle">23 Filters • Macro RRG • Auto-updated</div>
        </div>
        <div style="font-size:0.9rem; opacity:0.8;">{}</div>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📊 ETFs Scanned</div>
            <div class="value">{len(display_df)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        avg_score = display_df['Filter_Score'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">⭐ Avg Score</div>
            <div class="value">{avg_score:.1f}/23</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        top_score = display_df['Filter_Score'].max()
        top_etf = display_df[display_df['Filter_Score']==top_score]['ETF'].values[0] if top_score>0 else 'N/A'
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">🏆 Best Score</div>
            <div class="value">{top_score} <span style="font-size:1rem;">({top_etf})</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        golden = len(display_df[display_df['Benchmark Result']=='🏆 Golden Chance'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">💎 Golden Chances</div>
            <div class="value">{golden}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick summary table (just top 10)
    st.subheader("📌 Top 10 ETFs by Filter Score")
    st.dataframe(display_df.head(10)[['ETF', 'Sector', 'Filter_Score', 'RRG - (Sector v/s Nifty)', 'Benchmark Result']], use_container_width=True)

    if st.session_state.warnings:
        with st.expander("⚠️ Scan Warnings"):
            for w in st.session_state.warnings[:15]:
                st.write(w)

elif selected == "ETF Ranking":
    st.subheader("📋 Full ETF Ranking")
    # AgGrid interactive table
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(display_df, gridOptions=gridOptions, height=600, width='100%', theme='streamlit', allow_unsafe_jscode=True)

    # Download
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        display_df.to_excel(writer, sheet_name='ETF Ranking', index=True)
        if macro_avg is not None:
            macro_avg.to_excel(writer, sheet_name='Macro_RRG', index=False)
    excel_buffer.seek(0)
    st.download_button(
        label="⬇️ Download Excel Report",
        data=excel_buffer,
        file_name=f"ETF_Scan_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

elif selected == "RRG Chart":
    st.subheader("📊 RRG Chart – Macro Sector Averages")
    st.caption("🔄 Hover over points for details | Zoom & Pan with mouse")
    if macro_avg is not None and not macro_avg.empty:
        fig = go.Figure()
        # Quadrant lines
        fig.add_hline(y=0, line_color="black", line_width=1)
        fig.add_vline(x=1, line_color="black", line_width=1)
        # Labels
        fig.update_layout(
            annotations=[
                dict(x=1.25, y=0.08, text="🏆 LEADING", showarrow=False, font=dict(size=16, color="green", family="Arial Black")),
                dict(x=0.75, y=0.08, text="🟢 IMPROVING", showarrow=False, font=dict(size=16, color="blue")),
                dict(x=0.75, y=-0.15, text="🔴 LAGGING", showarrow=False, font=dict(size=16, color="red")),
                dict(x=1.25, y=-0.15, text="🟡 WEAKENING", showarrow=False, font=dict(size=16, color="orange"))
            ]
        )
        for idx, row in macro_avg.iterrows():
            sector = row['Macro_Sector']
            x = row['RS_Ratio']
            y = row['RS_Momentum']
            if x > 1 and y > 0: color, symbol = 'green', 'triangle-up'
            elif x < 1 and y > 0: color, symbol = 'blue', 'square'
            elif x < 1 and y < 0: color, symbol = 'red', 'triangle-down'
            else: color, symbol = 'orange', 'circle'
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                name=sector,
                marker=dict(size=20, color=color, symbol=symbol, line=dict(width=2, color='black')),
                text=[sector],
                textposition='top center',
                hoverinfo='text',
                hovertext=f"{sector}<br>RS-Ratio: {x:.3f}<br>RS-Momentum: {y:.3f}"
            ))
        fig.update_layout(
            title=dict(text='📈 Relative Rotation Graph', font=dict(size=20)),
            xaxis=dict(title='RS-Ratio → 1 = Nifty Avg', range=[0.4, 1.6]),
            yaxis=dict(title='RS-Momentum (Speed)', range=[-0.4, 0.4]),
            template='plotly_white',
            height=700,
            hovermode='closest',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No macro sector data.")

else:
    st.subheader("ℹ️ About")
    st.markdown("""
    **Ultimate ETF Scanner** uses **23 technical filters** to rank Indian ETFs.
    
    - **RRG** (Relative Rotation Graph) compares each ETF against Nifty 50.
    - **RV** (Relative Valuation) shows if ETF is undervalued vs Nifty.
    - **Trend, Momentum, Volume, and Reversal** filters give a comprehensive view.
    - Data sourced from Yahoo Finance (yfinance).
    
    Built with ❤️ using Streamlit, Plotly, and AgGrid.
    """)

# Footer
st.markdown("---")
st.caption("🔄 Data cached for 1 hour. Reload page to refresh scan.")
