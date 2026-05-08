import streamlit as st
import pandas as pd
import math
from io import BytesIO

# Branding Assets
PSPCL_LOGO_URL = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"
INSTA_ICON = "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
FB_ICON = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg"
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

# Base Rates as per CC 51/2024 (For year 2025)
BASE_RATES = {
    "11kV_Line": 1230.0,    # Rs/kVA 
    "66kV_Line": 576.0,     # Rs/kVA 
    "SLC": 3370.0           # System Loading Charges Rs/kVA 
}

# Increment Logic as per CC 35/2025
# 6% increase effective from 01.01.2026 [cite: 45]
INCREMENT_FACTOR = 1.06 

def main():
    st.set_page_config(page_title="Developer Cost Calculator 2026", layout="wide")

    # Custom CSS for UI
    st.markdown(f"""
        <style>
        .centered-logo {{ display: flex; justify-content: center; margin-bottom: 10px; }}
        .header-text {{ text-align: center; margin-bottom: 30px; }}
        .metric-card {{ background: #f0f9ff; padding: 20px; border-radius: 12px; border: 1px solid #bae6fd; text-align: center; }}
        .footer-container {{ text-align: center; padding: 40px; margin-top: 60px; border-top: 1px solid #e2e8f0; }}
        .social-icon {{ width: 25px; height: 25px; margin: 0 10px; transition: 0.3s; }}
        .beeclue-img {{ width: 140px; margin-top: 15px; }}
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f'<div class="centered-logo"><img src="{PSPCL_LOGO_URL}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header-text"><h1>PSPCL Proportionate Cost Calculator (2026)</h1><p>Ref: CC 45/2024 & CC 35/2025 (Annual 6% Increase Included)</p></div>', unsafe_allow_html=True)

    # Input Section
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        load_kva = st.number_input("Total Estimated Load (kVA)", min_value=0.0, value=0.0, step=10.0)
    with col_in2:
        voltage = st.selectbox("Connectivity Voltage", ["11 kV", "66 kV"])

    st.divider()

    # Calculation Engine
    # 1. Determine Base Rate based on voltage
    base_line_rate = BASE_RATES["11kV_Line"] if voltage == "11 kV" else BASE_RATES["66kV_Line"]
    base_slc_rate = BASE_RATES["SLC"]

    # 2. Apply 2026 Increment (6%)
    revised_line_rate = base_line_rate * INCREMENT_FACTOR
    revised_slc_rate = base_slc_rate * INCREMENT_FACTOR

    # 3. Totals
    line_total = load_kva * revised_line_rate
    slc_total = load_kva * revised_slc_rate
    grand_total = line_total + slc_total

    # Display Results
    if load_kva > 0:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📋 Calculation Table")
            summary_data = {
                "Description": [f"Proportionate Line Cost ({voltage})", "System Loading Charges (SLC)", "GRAND TOTAL"],
                "2025 Base Rate (Rs/kVA)": [base_line_rate, base_slc_rate, base_line_rate + base_slc_rate],
                "2026 Revised Rate (Inc. 6%)": [revised_line_rate, revised_slc_rate, revised_line_rate + revised_slc_rate],
                "Total Amount (Rs)": [line_total, slc_total, grand_total]
            }
            df = pd.DataFrame(summary_data)
            st.table(df.style.format({
                "2025 Base Rate (Rs/kVA)": "{:.2f}",
                "2026 Revised Rate (Inc. 6%)": "{:.2f}",
                "Total Amount (Rs)": "{:,.2f}"
            }))

            # Excel Export
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='NOC_Charges')
            st.download_button(label="📥 Download Export (Excel)", data=output.getvalue(), file_name="PSPCL_Developer_Charges_2026.xlsx")

        with c2:
            st.subheader("💰 NOC Summary")
            st.markdown(f"""
                <div class="metric-card">
                    <p style="font-size: 1rem; color: #64748b; margin: 0;">Total Payable for NOC</p>
                    <h2 style="color: #0369a1; margin: 5px 0;">₹ {grand_total:,.2f}</h2>
                    <hr style="border: 0.5px solid #bae6fd;">
                    <p style="font-size: 0.9rem; color: #64748b; margin: 0;">Minimum 35% BG Component</p>
                    <h3 style="color: #0369a1; margin: 5px 0;">₹ {grand_total * 0.35:,.2f}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if load_kva > 10000: # 10 MVA
                st.warning("⚠️ Load exceeds 10 MVA. Developer must provide 1500 Sq. Yards land for Grid Substation[cite: 697, 2232].")

    else:
        st.info("Please enter the estimated load in kVA to see the computation.")

    # Footer
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
        <a href="https://beeclue.com" target="_blank"><img src="{BEECLUE_LOGO_PNG}" class="beeclue-img"></a>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | Supply Code 2024 Guidelines | CC 35/2025</div>
    </div>"""
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
