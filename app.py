import streamlit as st
import pandas as pd
import math
from io import BytesIO

# --- ASSETS ---
PSPCL_LOGO_URL = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"
INSTA_ICON = "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
FB_ICON = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg"
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

# --- REGULATORY RATES (BASE 2025) ---
RATE_CONNECTION_NORMATIVE = 1230.0  # Rs/kVA (Annexure-4)
RATE_COLONY_NORMATIVE = 1545.0      # Rs/kVA (Annexure-5)
RATE_SLC = 3370.0                  # Rs/kVA (Annexure-13)
INCREMENT_2026 = 1.06              # 6% increase for 2026 (CC 35/2025)

def main():
    st.set_page_config(page_title="PSPCL Connectivity Pro 2026", layout="wide")

    # Custom UI Styling
    st.markdown(f"""
        <style>
        .centered-logo {{ display: flex; justify-content: center; margin-bottom: 10px; }}
        .header-text {{ text-align: center; margin-bottom: 30px; }}
        .metric-card {{ background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }}
        .footer-container {{ text-align: center; padding: 40px; margin-top: 60px; border-top: 1px solid #e2e8f0; background: #f1f5f9; }}
        .social-icon {{ width: 25px; height: 25px; margin: 0 10px; }}
        .payable-amount {{ color: #059669; font-weight: bold; font-size: 1.5rem; }}
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f'<div class="centered-logo"><img src="{PSPCL_LOGO_URL}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header-text"><h1>PSPCL Load & NOC Dashboard (2026)</h1><p>Supply Code 2024 | CC 45/2024 | CC 35/2025 (6% Increment Applied)</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⚡ Individual Connection", "🏗️ Colony Developer NOC"])

    # --- TAB 1: INDIVIDUAL CONNECTION ---
    with tab1:
        st.subheader("Proportionate Cost for New Connection / Extension")
        c1, c2 = st.columns(2)
        with c1:
            conn_kva = st.number_input("Load/Demand (kVA)", min_value=0.0, step=1.0, key="conn_load")
            st.caption("For demand > 150 kVA [cite: 2374, 2375]")
        
        # Calculation for Connection
        revised_conn_rate = RATE_CONNECTION_NORMATIVE * INCREMENT_2026
        total_prop_cost = conn_kva * revised_conn_rate

        if conn_kva > 0:
            st.info(f"Revised Normative Rate (2026): ₹ {revised_conn_rate:.2f} per kVA")
            st.markdown(f"""
                <div class="metric-card">
                    <p style="margin:0;">Total Proportionate Cost Payable</p>
                    <div class="payable-amount">₹ {total_prop_cost:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # --- TAB 2: COLONY DEVELOPER NOC ---
    with tab2:
        st.subheader("NOC Charges & Bank Guarantee Computation")
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            colony_kva = st.number_input("Total Colony Load (kVA)", min_value=0.0, step=10.0, key="col_load")
            ld_system_cost = st.number_input("Estimated LD System Cost (₹)", min_value=0.0, step=1000.0)
        
        with col_in2:
            service_line_cost = st.number_input("Estimated Service Line Cost (₹)", min_value=0.0, step=1000.0)
            option_105 = st.checkbox("Apply 105% BG against incomplete LD system")

        # Core Rates for Colony (Inc 6%)
        revised_bg_normative = RATE_COLONY_NORMATIVE * INCREMENT_2026
        revised_slc = RATE_SLC * INCREMENT_2026
        revised_conn_normative = RATE_CONNECTION_NORMATIVE * INCREMENT_2026

        # 1. Calculation for 35% BG [cite: 707, 2245]
        # BG is calculated on (LD Cost + Normative Connectivity + SLC)
        total_base_for_bg = ld_system_cost + (colony_kva * revised_bg_normative) + (colony_kva * revised_slc)
        bg_35_amount = total_base_for_bg * 0.35

        # 2. Total NOC Payable Amount (JMA Krwane Yogya)
        # Includes SLC + Proportionate/Normative + Service Line + LD Cost (if executed by PSPCL)
        total_noc_cash = (colony_kva * revised_slc) + (colony_kva * revised_conn_normative) + service_line_cost
        
        if not option_105:
            total_noc_cash += ld_system_cost
        
        if colony_kva > 0:
            st.divider()
            res_c1, res_c2 = st.columns(2)
            
            with res_c1:
                st.markdown("### 🛡️ Guarantee Requirements")
                st.write(f"**Required 35% Bank Guarantee:**")
                st.warning(f"₹ {bg_35_amount:,.2f}")
                
                if option_105:
                    bg_105 = ld_system_cost * 1.05
                    st.write(f"**105% BG against LD System:**")
                    st.error(f"₹ {bg_105:,.2f}")

            with res_c2:
                st.markdown("### 💰 Cash Deposit (NOC)")
                st.write("**Total Amount to be Deposited (Cash/Draft):**")
                st.markdown(f'<div class="payable-amount">₹ {total_noc_cash:,.2f}</div>', unsafe_allow_html=True)
                
                with st.expander("View Cash Breakdown"):
                    st.write(f"SLC (₹ {revised_slc:.2f}/kVA): ₹ {colony_kva * revised_slc:,.2f}")
                    st.write(f"Prop. Cost (₹ {revised_conn_normative:.2f}/kVA): ₹ {colony_kva * revised_conn_normative:,.2f}")
                    st.write(f"Service Line Cost: ₹ {service_line_cost:,.2f}")
                    if not option_105:
                        st.write(f"LD System execution cost: ₹ {ld_system_cost:,.2f}")

    # --- FOOTER ---
    footer_html = f"""
    <div class="footer-container">
        <div style="font-size: 1.1rem; margin-bottom: 15px;">Made with <span style="color: #e11d48;">❤️</span> by <b>Er. Anuj Narang, JE PSPCL</b></div>
        <div style="margin-bottom: 25px;">
            <a href="https://instagram.com/iamanujnarang" target="_blank"><img src="{INSTA_ICON}" class="social-icon"></a>
            <a href="https://facebook.com/iamanujnarang" target="_blank"><img src="{FB_ICON}" class="social-icon"></a>
            <a href="https://x.com/iamanujnarang" target="_blank"><img src="{X_ICON}" class="social-icon"></a>
            <a href="https://linkedin.com/in/iamanujnarang" target="_blank"><img src="{LINKEDIN_ICON}" class="social-icon"></a>
        </div>
        <div style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">In Strategic Collaboration with</div>
        <a href="https://beeclue.com" target="_blank"><img src="{BEECLUE_LOGO_PNG}" class="beeclue-img" width="140"></a>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | Supply Code 2024 Guidelines | CC 35/2025</div>
    </div>"""
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
