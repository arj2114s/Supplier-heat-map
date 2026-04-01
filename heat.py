import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supplier Risk Heat Map", layout="wide")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Interactive Supplier Risk Analyst")

# --- SIDEBAR: WEIGHT INPUTS ---
with st.sidebar:
    st.header("⚖️ Weight Configuration")
    
    st.subheader("Likelihood Weights (%)")
    w_ncr = st.number_input("1. Non conformance rate (NCR)", 0, 100, 40)
    w_resch = st.number_input("2. Reschedule rate", 0, 100, 25)
    w_past_ch = st.number_input("3. No of past changes", 0, 100, 20)
    w_resp = st.number_input("4. Responsiveness", 0, 100, 15)
    
    st.divider()
    
    st.subheader("Impact Weights (%)")
    w_avg_delay = st.number_input("1. Avg delay days", 0, 100, 15)
    w_max_delay = st.number_input("2. Max past Delay Days", 0, 100, 15)
    w_otd = st.number_input("3. On time delivery %", 0, 100, 20)
    w_ncr_close = st.number_input("4. Avg NCR closure time", 0, 100, 10)
    w_insp = st.number_input("5. Inspection cycle time", 0, 100, 10)
    w_wo_cr = st.number_input("6. Site WO-CR", 0, 100, 10)
    w_ep_cr = st.number_input("7. E&P-CR", 0, 100, 10)
    w_po_cr = st.number_input("8. PO-CR", 0, 100, 10)

    # Weight Validation
    l_sum = w_ncr + w_resch + w_past_ch + w_resp
    i_sum = w_avg_delay + w_max_delay + w_otd + w_ncr_close + w_insp + w_wo_cr + w_ep_cr + w_po_cr
    
    if l_sum != 100: st.error(f"Likelihood Weights sum to {l_sum}%. Must be 100%!")
    if i_sum != 100: st.error(f"Impact Weights sum to {i_sum}%. Must be 100%!")

# --- MAIN SECTION: DATA INPUT ---
st.header("📝 Supplier Raw Data (Scores 1-5)")
st.caption("Edit the cells below to change raw performance scores for each supplier (1 = Best, 5 = Worst Risk).")

# Initial Dataframe for S1-S5
default_data = {
    "Supplier": ["S1", "S2", "S3", "S4", "S5"],
    "NCR Rate": [1, 3, 5, 2, 4],
    "Reschedule Rate": [2, 2, 4, 1, 5],
    "Past Changes": [1, 4, 3, 2, 5],
    "Responsiveness": [1, 2, 5, 1, 3],
    "Avg Delay": [2, 3, 5, 1, 4],
    "Max Delay": [2, 4, 5, 2, 5],
    "OTD Score": [1, 3, 4, 1, 5],
    "NCR Closure": [2, 2, 5, 2, 3],
    "Inspection Time": [1, 3, 4, 2, 4],
    "WO-CR": [1, 1, 3, 2, 5],
    "E&P-CR": [1, 2, 3, 1, 4],
    "PO-CR": [1, 3, 4, 2, 5],
}
df_input = pd.DataFrame(default_data)

# Use Data Editor for user input
edited_df = st.data_editor(df_input, hide_index=True, use_container_width=True)

# --- CALCULATION LOGIC ---
# Likelihood Calculation
edited_df['Likelihood_Score'] = (
    (edited_df['NCR Rate'] * (w_ncr/100)) +
    (edited_df['Reschedule Rate'] * (w_resch/100)) +
    (edited_df['Past Changes'] * (w_past_ch/100)) +
    (edited_df['Responsiveness'] * (w_resp/100))
)

# Impact Calculation
edited_df['Impact_Score'] = (
    (edited_df['Avg Delay'] * (w_avg_delay/100)) +
    (edited_df['Max Delay'] * (w_max_delay/100)) +
    (edited_df['OTD Score'] * (w_otd/100)) +
    (edited_df['NCR Closure'] * (w_ncr_close/100)) +
    (edited_df['Inspection Time'] * (w_insp/100)) +
    (edited_df['WO-CR'] * (w_wo_cr/100)) +
    (edited_df['E&P-CR'] * (w_ep_cr/100)) +
    (edited_df['PO-CR'] * (w_po_cr/100))
)

# --- VISUALIZATION ---
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Risk Heat Map")
    fig = px.scatter(
        edited_df, x="Likelihood_Score", y="Impact_Score", text="Supplier",
        range_x=[1, 5], range_y=[1, 5],
        labels={"Likelihood_Score": "Likelihood (Probability)", "Impact_Score": "Impact (Severity)"},
        height=600
    )
    
    # Background Shapes for Heat Map Zones
    fig.add_shape(type="rect", x0=1, y0=1, x1=2.5, y1=2.5, fillcolor="green", opacity=0.2, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=2.5, y0=1, x1=5, y1=2.5, fillcolor="orange", opacity=0.2, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=1, y0=2.5, x1=2.5, y1=5, fillcolor="orange", opacity=0.2, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=2.5, y0=2.5, x1=5, y1=5, fillcolor="red", opacity=0.2, layer="below", line_width=0)
    
    fig.update_traces(marker=dict(size=20, line=dict(width=2, color='DarkSlateGrey')), textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📈 Final Risk Scores")
    # Styling the table to show colors based on scores
    st.dataframe(
        edited_df[['Supplier', 'Likelihood_Score', 'Impact_Score']].style.background_gradient(cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True
    )
    
    avg_risk = (edited_df['Likelihood_Score'].mean() + edited_df['Impact_Score'].mean()) / 2
    st.metric("Portfolio Risk Avg", round(avg_risk, 2))