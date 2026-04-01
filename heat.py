import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supplier Risk Heat Map", layout="wide")

# --- CUSTOM CSS FOR LIGHT THEME ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #E0E0E0; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    .stDataFrame { border: 1px solid #E0E0E0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Supplier Risk Analyst")
st.caption("Strategic Sourcing Tool | Data-Driven Risk Assessment")

# --- SIDEBAR: REFINED WEIGHT INPUTS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.expander("📊 Likelihood Weights (%)", expanded=True):
        w_ncr = st.slider("NCR Rate", 0, 100, 40)
        w_resch = st.slider("Reschedule Rate", 0, 100, 25)
        w_past_ch = st.slider("Past Changes", 0, 100, 20)
        w_resp = st.slider("Responsiveness", 0, 100, 15)
    
    with st.expander("💥 Impact Weights (%)", expanded=False):
        w_avg_delay = st.number_input("Avg delay days", 0, 100, 15)
        w_max_delay = st.number_input("Max Delay Days", 0, 100, 15)
        w_otd = st.number_input("OTD %", 0, 100, 20)
        w_ncr_close = st.number_input("NCR closure time", 0, 100, 10)
        w_insp = st.number_input("Inspection cycle", 0, 100, 10)
        w_wo_cr = st.number_input("Site WO-CR", 0, 100, 10)
        w_ep_cr = st.number_input("E&P-CR", 0, 100, 10)
        w_po_cr = st.number_input("PO-CR", 0, 100, 10)

    l_sum = w_ncr + w_resch + w_past_ch + w_resp
    i_sum = w_avg_delay + w_max_delay + w_otd + w_ncr_close + w_insp + w_wo_cr + w_ep_cr + w_po_cr
    
    if l_sum != 100: st.sidebar.warning(f"Likelihood: {l_sum}%")
    if i_sum != 100: st.sidebar.warning(f"Impact: {i_sum}%")

# --- DATA INPUT ---
st.subheader("📝 Performance Input")
default_data = {
    "Supplier": ["S1", "S2", "S3", "S4", "S5"],
    "NCR Rate": [1, 3, 5, 2, 4], "Reschedule Rate": [2, 2, 4, 1, 5],
    "Past Changes": [1, 4, 3, 2, 5], "Responsiveness": [1, 2, 5, 1, 3],
    "Avg Delay": [2, 3, 5, 1, 4], "Max Delay": [2, 4, 5, 2, 5],
    "OTD Score": [1, 3, 4, 1, 5], "NCR Closure": [2, 2, 5, 2, 3],
    "Inspection Time": [1, 3, 4, 2, 4], "WO-CR": [1, 1, 3, 2, 5],
    "E&P-CR": [1, 2, 3, 1, 4], "PO-CR": [1, 3, 4, 2, 5],
}
df_input = pd.DataFrame(default_data)
edited_df = st.data_editor(df_input, hide_index=True, use_container_width=True)

# --- LOGIC ---
edited_df['Likelihood_Score'] = ((edited_df['NCR Rate']*(w_ncr/100))+(edited_df['Reschedule Rate']*(w_resch/100))+(edited_df['Past Changes']*(w_past_ch/100))+(edited_df['Responsiveness']*(w_resp/100)))
edited_df['Impact_Score'] = ((edited_df['Avg Delay']*(w_avg_delay/100))+(edited_df['Max Delay']*(w_max_delay/100))+(edited_df['OTD Score']*(w_otd/100))+(edited_df['NCR Closure']*(w_ncr_close/100))+(edited_df['Inspection Time']*(w_insp/100))+(edited_df['WO-CR']*(w_wo_cr/100))+(edited_df['E&P-CR']*(w_ep_cr/100))+(edited_df['PO-CR']*(w_po_cr/100)))

# --- VISUALS ---
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Risk Landscape")
    fig = px.scatter(edited_df, x="Likelihood_Score", y="Impact_Score", text="Supplier", range_x=[1, 5], range_y=[1, 5], template="plotly_white")
    
    # LIGHT COLORS (Pastels)
    fig.add_shape(type="rect", x0=1, y0=1, x1=2.5, y1=2.5, fillcolor="#E8F5E9", opacity=0.7, layer="below", line_width=0) # Light Green
    fig.add_shape(type="rect", x0=2.5, y0=1, x1=5, y1=2.5, fillcolor="#FFF3E0", opacity=0.7, layer="below", line_width=0) # Light Orange
    fig.add_shape(type="rect", x0=1, y0=2.5, x1=2.5, y1=5, fillcolor="#FFF3E0", opacity=0.7, layer="below", line_width=0) # Light Orange
    fig.add_shape(type="rect", x0=2.5, y0=2.5, x1=5, y1=5, fillcolor="#FFEBEE", opacity=0.7, layer="below", line_width=0) # Light Red
    
    fig.update_traces(marker=dict(size=18, color='#455A64', line=dict(width=1, color='white')), textposition='top center')
    fig.update_xaxes(showgrid=False, title_text="Likelihood (1-5)")
    fig.update_yaxes(showgrid=False, title_text="Impact (1-5)")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📈 Summary Table")
    styled_df = edited_df[['Supplier', 'Likelihood_Score', 'Impact_Score']].sort_values('Likelihood_Score', ascending=False)
    st.dataframe(styled_df.style.background_gradient(cmap="YlOrRd").format(precision=2), use_container_width=True, hide_index=True)
    
    avg_risk = (edited_df['Likelihood_Score'].mean() + edited_df['Impact_Score'].mean()) / 2
    st.metric("Portfolio Average Risk", round(avg_risk, 2), delta_color="inverse")
