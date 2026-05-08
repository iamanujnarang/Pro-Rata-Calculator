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
RATE_CONNECTION_NORMATIVE = 1230.0  # Rs/kVA (Annexure-4) [cite: 217, 2409]
RATE_COLONY_NORMATIVE = 1545.0      # Rs/kVA (Annexure-5) [cite: 220]
RATE_SLC = 3370.0                   # Rs/kVA (Annexure-13) [cite: 264]
INCREMENT_2026 = 1.06               # 6% increase for 2026 (CC 35/2025) [cite: 44, 45]

def format_indian_currency(number):
    """Formats a number into the Indian numbering system (Lakhs, Crores)"""
    s = str(round(number, 2))
    out = ""
    parts = s.split(".")
    num = parts[0]
    
    if len(num) <= 3:
        out = num
    else:
        last_three = num[-3:]
        remaining = num[:-3]
        out = last_three
        while len(remaining) > 0:
            if len(remaining) > 1:
                out = remaining[-2:] + "," + out
                remaining = remaining[:-2]
            else:
                out = remaining + "," + out
                remaining = ""
    
    if len(parts) > 1:
        return out + "." + parts[1].ljust(2, '0')
    return out + ".00"

def to_excel(df, sheet_name="Report"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def main():
    st.set_page_config(page_title="PSPCL Pro Rata Calculator", layout="wide")

    # Custom UI Styling
    st.markdown(f"""
        <style>
        .centered-logo {{ display: flex; justify-content: center; margin-bottom: 10px; }}
        .header-text {{ text-align: center; margin-bottom: 30px; }}
        .metric-card {{ background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        .footer-container {{ text-align: center; padding: 40px; margin-top: 60px; border-top: 1px solid #e2e8f0; background: #f1f5f9; }}
        .social-icon {{ width: 25px; height: 25px; margin: 0 10px; transition: 0.3s; }}
        .social-icon:hover {{ transform: scale(1.2); }}
        .payable-amount {{ color: #059669; font-weight: bold; font-size: 1.5rem; }}
        .bg-amount {{ color: #d97706; font-weight: bold; font-size: 1.5rem; }}
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f'<div class="centered-logo"><img src="{PSPCL_LOGO_URL}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header-text"><h1>PSPCL Multipurpose PRO Rata Calculator</h1><p>Supply Code 2024 | CC 45/2024 | CC 51/2024 | CC 35/2025 |(Annual 6% Compounded Increase)</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⚡ Individual Connection / Extension", "🏗️ Colony Developer NOC"])

    # --- TAB 1: INDIVIDUAL CONNECTION ---
    with tab1:
        st.subheader("Proportionate Cost Calculation")
        c1, c2 = st.columns(2)
        with c1:
            conn_kva = st.number_input("Load/Demand (kVA)", min_value=0.0, step=1.0, key="conn_load")
            st.caption("Applicable for demand exceeding 150 kVA [cite: 2374, 2375]")
        
        revised_conn_rate = RATE_CONNECTION_NORMATIVE * INCREMENT_2026
        total_prop_cost = conn_kva * revised_conn_rate

        if conn_kva > 0:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="margin:0; font-weight: bold; color: #64748b;">Total Proportionate Cost Payable (2026)</p>
                    <div class="payable-amount">₹ {format_indian_currency(total_prop_cost)}</div>
                    <p style="margin-top:10px; font-size: 0.9rem; color: #94a3b8;">Rate: ₹ {RATE_CONNECTION_NORMATIVE} (Base) × 1.06 (Increment) = ₹ {revised_conn_rate:.2f} per kVA</p>
                </div>
            """, unsafe_allow_html=True)

            df_conn = pd.DataFrame({
                "Description": ["Load (kVA)", "Normative Rate (Base 2025)", "Revised Rate (2026)", "Total Payable (₹)"],
                "Value": [conn_kva, RATE_CONNECTION_NORMATIVE, revised_conn_rate, format_indian_currency(total_prop_cost)]
            })
            st.download_button("📥 Export Connection Report to Excel", data=to_excel(df_conn, "Connection_Report"), file_name="PSPCL_Connection_Report.xlsx")

    # --- TAB 2: COLONY DEVELOPER NOC ---
    with tab2:
        st.subheader("NOC Charges & Bank Guarantee Computation")
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            colony_kva = st.number_input("Total Estimated Colony Load (kVA)", min_value=0.0, step=10.0, key="col_load")
            ld_system_cost = st.number_input("Estimated Internal LD System Cost (₹)", min_value=0.0, step=1000.0)
        
        with col_in2:
            service_line_cost = st.number_input("Estimated Service Line Cost (₹) [Point B to Consumer]", min_value=0.0, step=1000.0)
            option_105 = st.checkbox("Apply 105% BG against LD system (if executed by Developer)")

        # Core Rates for Colony (Inc 6%) [cite: 44, 45, 220, 264]
        rev_bg_norm = RATE_COLONY_NORMATIVE * INCREMENT_2026
        rev_slc = RATE_SLC * INCREMENT_2026
        rev_conn_norm = RATE_CONNECTION_NORMATIVE * INCREMENT_2026

        # 1. Calculation for 35% BG [cite: 707, 2245]
        total_connectivity_for_bg = colony_kva * (rev_bg_norm + rev_slc)
        total_base_for_bg = ld_system_cost + total_connectivity_for_bg
        bg_35_amount = total_base_for_bg * 0.35

        # 2. Total NOC Payable Amount
        total_slc_cash = colony_kva * rev_slc
        total_prop_cash = colony_kva * rev_conn_norm
        total_noc_cash = total_slc_cash + total_prop_cash + service_line_cost
        if not option_105:
            total_noc_cash += ld_system_cost
        
        if colony_kva > 0:
            st.divider()
            res_c1, res_c2 = st.columns(2)
            
            with res_c1:
                st.markdown("### 🛡️ Bank Guarantee Requirements")
                st.write("**Required 35% Bank Guarantee:**")
                st.markdown(f'<div class="bg-amount">₹ {format_indian_currency(bg_35_amount)}</div>', unsafe_allow_html=True)
                
                with st.expander("🔍 Click to see How 35% BG is Calculated"):
                    st.write("As per Regulation 12(4) & CC 45/2024: [cite: 707, 2245]")
                    st.markdown(f"""
                    * **Internal LD Cost:** ₹ {format_indian_currency(ld_system_cost)}
                    * **Normative Connectivity (1545 × 1.06):** ₹ {rev_bg_norm:.2f} × {colony_kva} kVA = ₹ {format_indian_currency(colony_kva * rev_bg_norm)}
                    * **System Loading Charges (3370 × 1.06):** ₹ {rev_slc:.2f} × {colony_kva} kVA = ₹ {format_indian_currency(colony_kva * rev_slc)}
                    * **Sum Total:** ₹ {format_indian_currency(total_base_for_bg)}
                    * **35% of Sum Total:** ₹ {format_indian_currency(total_base_for_bg)} × 0.35 = **₹ {format_indian_currency(bg_35_amount)}**
                    """)
                
                if option_105:
                    bg_105 = ld_system_cost * 1.05
                    st.write(f"**Required 105% BG (Against Incomplete LD):**")
                    st.markdown(f'<div style="color: #dc2626; font-weight: bold; font-size: 1.2rem;">₹ {format_indian_currency(bg_105)}</div>', unsafe_allow_html=True)

            with res_c2:
                st.markdown("### 💰 Amount to be Deposited after issuance of NOC")
                st.write("**Total Draft to be Deposited:**")
                st.markdown(f'<div class="payable-amount">₹ {format_indian_currency(total_noc_cash)}</div>', unsafe_allow_html=True)
                
                with st.expander("🔍 View Cash Breakdown"):
                    st.write(f"1. **SLC** (₹ {rev_slc:.2f}/kVA): ₹ {format_indian_currency(total_slc_cash)}")
                    st.write(f"2. **Prop. Cost** (₹ {rev_conn_norm:.2f}/kVA): ₹ {format_indian_currency(total_prop_cash)}")
                    st.write(f"3. **Service Line Cost**: ₹ {format_indian_currency(service_line_cost)}")
                    if not option_105:
                        st.write(f"4. **LD System Cost** (Executed by PSPCL): ₹ {format_indian_currency(ld_system_cost)}")
                    else:
                        st.write("4. **LD System Cost**: Excluded (Covered by 105% BG)")

            df_noc = pd.DataFrame([
                ["Colony Load (kVA)", colony_kva],
                ["Internal LD Cost (₹)", format_indian_currency(ld_system_cost)],
                ["Service Line Cost (₹)", format_indian_currency(service_line_cost)],
                ["35% Bank Guarantee (₹)", format_indian_currency(bg_35_amount)],
                ["105% BG (if applicable) (₹)", format_indian_currency(ld_system_cost * 1.05) if option_105 else "0.00"],
                ["Total Cash Deposit (₹)", format_indian_currency(total_noc_cash)]
            ], columns=["Description", "Value"])
            st.download_button("📥 Export NOC Computation to Excel", data=to_excel(df_noc, "NOC_Report"), file_name="PSPCL_NOC_Report.xlsx")

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
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | Supply Code 2024 | PSPCL Guidelines | Ver 2.1</div>
    </div>"""
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
