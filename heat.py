import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supplier Risk Dashboard", layout="wide")

# --- CUSTOM CSS FOR LIGHT THEME ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #e6f2ff; border-bottom: 2px solid #1f77b4; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Supplier Risk Dashboard")

# ==========================================
# 1. INITIALIZE SESSION STATE (MEMORY)
# ==========================================
if 'supplier_data' not in st.session_state:
    st.session_state.supplier_data = pd.DataFrame({
        "Supplier": ["S1", "S2", "S3", "S4", "S5"],
        "NCR Rate": [1, 3, 5, 2, 4], "Reschedule Rate": [2, 2, 4, 1, 5],
        "Past Changes": [1, 4, 3, 2, 5], "Responsiveness": [1, 2, 5, 1, 3],
        "Avg Delay": [2, 3, 5, 1, 4], "Max Delay": [2, 4, 5, 2, 5],
        "OTD Score": [1, 3, 4, 1, 5], "NCR Closure": [2, 2, 5, 2, 3],
        "Inspection Time": [1, 3, 4, 2, 4], "WO-CR": [1, 1, 3, 2, 5],
        "E&P-CR": [1, 2, 3, 1, 4], "PO-CR": [1, 3, 4, 2, 5],
    })

# ==========================================
# 2. WEIGHT CONFIGURATION (TOP SECTION)
# ==========================================
st.header("⚙️ 1. Weight Configuration (%)")

st.subheader("Likelihood Weights")
lc1, lc2, lc3, lc4 = st.columns(4)
w_ncr = lc1.number_input("NCR Rate", 0, 100, 40)
w_resch = lc2.number_input("Reschedule Rate", 0, 100, 25)
w_past_ch = lc3.number_input("Past Changes", 0, 100, 20)
w_resp = lc4.number_input("Responsiveness", 0, 100, 15)

st.subheader("Impact Weights")
ic1, ic2, ic3, ic4 = st.columns(4)
w_avg_delay = ic1.number_input("Avg delay days", 0, 100, 15)
w_max_delay = ic2.number_input("Max Delay Days", 0, 100, 15)
w_otd = ic3.number_input("OTD %", 0, 100, 20)
w_ncr_close = ic4.number_input("NCR closure time", 0, 100, 10)

ic5, ic6, ic7, ic8 = st.columns(4)
w_insp = ic5.number_input("Inspection cycle", 0, 100, 10)
w_wo_cr = ic6.number_input("Site WO-CR", 0, 100, 10)
w_ep_cr = ic7.number_input("E&P-CR", 0, 100, 10)
w_po_cr = ic8.number_input("PO-CR", 0, 100, 10)

# Validation
l_sum = w_ncr + w_resch + w_past_ch + w_resp
i_sum = w_avg_delay + w_max_delay + w_otd + w_ncr_close + w_insp + w_wo_cr + w_ep_cr + w_po_cr
if l_sum != 100: st.warning(f"⚠️ Likelihood Weights sum to {l_sum}%. Please adjust to 100%.")
if i_sum != 100: st.warning(f"⚠️ Impact Weights sum to {i_sum}%. Please adjust to 100%.")

st.divider()

# ==========================================
# 3. SUPPLIER DATA EDITOR (MIDDLE SECTION)
# ==========================================
st.header("📝 2. Supplier Data Input (Scores 1-5)")

# Selectbox to pick which supplier to edit
selected_supplier = st.selectbox("Select a Supplier to Edit:", st.session_state.supplier_data["Supplier"])

# Find the row index of the selected supplier
idx = st.session_state.supplier_data.index[st.session_state.supplier_data['Supplier'] == selected_supplier][0]

st.caption(f"Editing parameters for **{selected_supplier}**:")

# Create two columns for editing parameters
edit_col1, edit_col2 = st.columns(2)

with edit_col1:
    st.markdown("**Likelihood Parameters**")
    st.session_state.supplier_data.at[idx, "NCR Rate"] = st.number_input("NCR Rate Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "NCR Rate"]))
    st.session_state.supplier_data.at[idx, "Reschedule Rate"] = st.number_input("Reschedule Rate Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Reschedule Rate"]))
    st.session_state.supplier_data.at[idx, "Past Changes"] = st.number_input("Past Changes Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Past Changes"]))
    st.session_state.supplier_data.at[idx, "Responsiveness"] = st.number_input("Responsiveness Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Responsiveness"]))

with edit_col2:
    st.markdown("**Impact Parameters**")
    i_c1, i_c2 = st.columns(2)
    with i_c1:
        st.session_state.supplier_data.at[idx, "Avg Delay"] = st.number_input("Avg Delay Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Avg Delay"]))
        st.session_state.supplier_data.at[idx, "Max Delay"] = st.number_input("Max Delay Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Max Delay"]))
        st.session_state.supplier_data.at[idx, "OTD Score"] = st.number_input("OTD Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "OTD Score"]))
        st.session_state.supplier_data.at[idx, "NCR Closure"] = st.number_input("NCR Closure Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "NCR Closure"]))
    with i_c2:
        st.session_state.supplier_data.at[idx, "Inspection Time"] = st.number_input("Inspection Time Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "Inspection Time"]))
        st.session_state.supplier_data.at[idx, "WO-CR"] = st.number_input("WO-CR Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "WO-CR"]))
        st.session_state.supplier_data.at[idx, "E&P-CR"] = st.number_input("E&P-CR Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "E&P-CR"]))
        st.session_state.supplier_data.at[idx, "PO-CR"] = st.number_input("PO-CR Score", 1, 5, value=int(st.session_state.supplier_data.at[idx, "PO-CR"]))

st.divider()

# ==========================================
# 4. CALCULATIONS
# ==========================================
# Copy the session state data to a new dataframe for math operations
df = st.session_state.supplier_data.copy()

df['Likelihood_Score'] = ((df['NCR Rate']*(w_ncr/100))+(df['Reschedule Rate']*(w_resch/100))+(df['Past Changes']*(w_past_ch/100))+(df['Responsiveness']*(w_resp/100)))
df['Impact_Score'] = ((df['Avg Delay']*(w_avg_delay/100))+(df['Max Delay']*(w_max_delay/100))+(df['OTD Score']*(w_otd/100))+(df['NCR Closure']*(w_ncr_close/100))+(df['Inspection Time']*(w_insp/100))+(df['WO-CR']*(w_wo_cr/100))+(df['E&P-CR']*(w_ep_cr/100))+(df['PO-CR']*(w_po_cr/100)))

# ==========================================
# 5. TABS FOR VISUALIZATION
# ==========================================
st.header("📈 3. Results Analysis")

tab1, tab2 = st.tabs(["📊 Risk Heat Map", "📑 Summary Table"])

with tab1:
    fig = px.scatter(df, x="Likelihood_Score", y="Impact_Score", text="Supplier", range_x=[1, 5], range_y=[1, 5], template="plotly_white", height=600)
    
    # Background Shapes
    fig.add_shape(type="rect", x0=1, y0=1, x1=2.5, y1=2.5, fillcolor="#E8F5E9", opacity=0.7, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=2.5, y0=1, x1=5, y1=2.5, fillcolor="#FFF3E0", opacity=0.7, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=1, y0=2.5, x1=2.5, y1=5, fillcolor="#FFF3E0", opacity=0.7, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=2.5, y0=2.5, x1=5, y1=5, fillcolor="#FFEBEE", opacity=0.7, layer="below", line_width=0)
    
    fig.update_traces(marker=dict(size=18, color='#455A64', line=dict(width=1, color='white')), textposition='top center')
    fig.update_xaxes(showgrid=False, title_text="Likelihood (1-5)")
    fig.update_yaxes(showgrid=False, title_text="Impact (1-5)")
    
    # Render Plotly Chart inside Tab 1
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    styled_df = df[['Supplier', 'Likelihood_Score', 'Impact_Score']].sort_values('Likelihood_Score', ascending=False)
    
    # Render Dataframe inside Tab 2
    st.dataframe(styled_df.style.background_gradient(cmap="YlOrRd").format(precision=2), use_container_width=True, hide_index=True)
    
    # Show Portfolio Avg at the bottom of the table
    avg_risk = (df['Likelihood_Score'].mean() + df['Impact_Score'].mean()) / 2
    st.metric("Portfolio Average Risk", round(avg_risk, 2))
