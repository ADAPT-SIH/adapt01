import streamlit as st
import pandas as pd
import altair as alt

chart_df = pd.DataFrame({
    "Stage": ["Production (kg CO₂e/t)", "Transport (kg CO₂e/t)", "Total (kg CO₂e/t)"],
    "Value": [float(kgco2_per_kg) * 1000.0, float(transport_kgco2_per_ton), float(total_co2_per_tonne)]
})

st.subheader("Visual Representation")
# Streamlit's built-in bar chart — no external lib required
st.bar_chart(chart_df.set_index("Stage"))



st.set_page_config(page_title="SustainaMine - LCA for Metals", layout="wide")

SOURCES = {
    "CPCB_RedMud_Guidelines": "https://cpcb.nic.in/uploads/hwmd/Guidelines_HW_6.pdf",
    "Hazardous_Waste_Rules_2016": "https://www.npcindia.gov.in/NPC/Files/delhiOFC/EM/Hazardous-waste-management-rules-2016.pdf",
    "Minerals_Aluminium_page": "https://mines.gov.in/webportal/content/Aluminium",
    "RedMud_Brochure_JNARDDC": "https://www.jnarddc.gov.in/Files/Red_Mud_Brochure.pdf",
    "Indian_Minerals_Yearbook_Copper": "https://ibm.gov.in/writereaddata/files/1715685346664347e2b0816Copper_2022.pdf",
    "CPCB_Technical_Guidelines": "https://cpcb.nic.in/technical-guidelines/"
}

st.title("SustainaMine — AI-Driven LCA for Metals (India)")
st.markdown("""
**Purpose:** Prototype for Smart India Hackathon — AI-assisted Life Cycle Assessment (LCA)
tool for **Aluminium** and **Copper** with circularity, by-product valorization, and regulatory
compliance support for India.

**Note:** Default numbers are *illustrative*. Replace with validated local data for final deployment.
""")

st.info("""
**Pro-government framing:** This tool is designed to _support_ Government of India objectives — it helps industry
adhere to CPCB / MoEFCC guidelines, follow the Hazardous & Other Wastes Rules (2016), and advance circularity
aligned with National Mineral Policy goals. It **does not** replace statutory approvals — it **assists** compliance.
""")

st.header("India Context & Production (quick snapshot)")
col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Major Aluminium-producing states (India)")
    st.write("""
        Typical top-producing states: **Odisha, Gujarat, Maharashtra, Chhattisgarh, Jharkhand**.
        These states host large alumina/aluminium complexes (NALCO, Hindalco, Vedanta, BALCO).
        """)
    st.write(f"- CPCB / Guidelines: {SOURCES['CPCB_RedMud_Guidelines']}")
    st.write(f"- Ministry of Mines info: {SOURCES['Minerals_Aluminium_page']}")

with col2:
    st.subheader("Major Copper-producing regions (India)")
    st.write("""
        Notable copper regions: **Rajasthan, Madhya Pradesh, Jharkhand**. India also imports concentrates.
        Refer to the Indian Minerals Yearbook for details.
        """)
    st.write(f"- Copper Yearbook (IBM): {SOURCES['Indian_Minerals_Yearbook_Copper']}")

st.markdown("---")

st.header("Default LCA parameters (illustrative defaults)")
st.write("These baseline factors are placeholders for demo. Replace them with validated LCI data for final results.")

default_factors = {
    "aluminium_virgin_kgco2_per_kg": 16.0,
    "aluminium_recycled_kgco2_per_kg": 4.0,
    "copper_virgin_kgco2_per_kg": 8.0,
    "copper_recycled_kgco2_per_kg": 2.0,
    "red_mud_t_per_t_aluminium": 1.5,
    "so2_kg_per_t_copper": 25.0,
    "transport_kgco2_per_tkm": 0.05,
    "recycle_cost_usd_per_t_aluminium": 200.0,
    "recycle_cost_usd_per_t_copper": 300.0,
}
st.json(default_factors)
st.markdown("---")

st.header("Run an LCA Estimate (Demo Input)")
with st.form(key="input_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        metal = st.selectbox("Select metal", ["Aluminium", "Copper"])
        if metal == "Aluminium":
            state = st.selectbox("State of extraction", ["Odisha", "Gujarat", "Maharashtra", "Chhattisgarh", "Jharkhand", "Other"])
            ore_quality = st.selectbox("Bauxite quality (choose)", ["High (>45%)", "Medium (35–45%)", "Low (<35%)"])
        else:
            state = st.selectbox("State of extraction", ["Rajasthan", "Madhya Pradesh", "Jharkhand", "Other/Import"])
            ore_quality = st.selectbox("Copper ore grade (choose)", ["High (>2% Cu)", "Medium (1–2% Cu)", "Low (<1% Cu)"])
        production_route = st.selectbox("Production route", ["Virgin/Raw", "Recycled", "Mixed"])
        recycled_pct = st.slider("Recycled content (%)", 0, 100, 30)
    with col2:
        energy_source = st.selectbox("Energy source (select nearest)", ["Coal-based grid", "Mixed grid", "Renewable-heavy"])
        transport_km = st.number_input("Transport distance (km)", min_value=0, max_value=5000, value=200)
        transport_tonnes = st.number_input("Quantity to assess (tonnes of metal)", min_value=1, max_value=100000, value=1)
    with col3:
        eol_option = st.selectbox("End-of-life option", ["Landfill", "Recycling", "Reuse"])
        storage_practice = st.selectbox("Storage / residue handling", ["Proper authorized storage", "Temporary open storage", "Untreated disposal"])
        run_button = st.form_submit_button("Run LCA estimate")

if run_button:
    if metal == "Aluminium":
        if production_route == "Virgin/Raw":
            baseline = default_factors["aluminium_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["aluminium_recycled_kgco2_per_kg"]
        else:
            baseline = (default_factors["aluminium_virgin_kgco2_per_kg"] * (100 - recycled_pct) / 100
                        + default_factors["aluminium_recycled_kgco2_per_kg"] * recycled_pct / 100)
    else:
        if production_route == "Virgin/Raw":
            baseline = default_factors["copper_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["copper_recycled_kgco2_per_kg"]
        else:
            baseline = (default_factors["copper_virgin_kgco2_per_kg"] * (100 - recycled_pct) / 100
                        + default_factors["copper_recycled_kgco2_per_kg"] * recycled_pct / 100)

    red_mud_t, so2_kg_total = 0.0, 0.0
    if metal == "Aluminium":
        if "High" in ore_quality:
            quality_factor = 1.0
        elif "Medium" in ore_quality:
            quality_factor = 1.2
        else:
            quality_factor = 1.5
        red_mud_t = default_factors["red_mud_t_per_t_aluminium"] * transport_tonnes * quality_factor
    else:
        if "High" in ore_quality:
            so2_factor = 1.0
        elif "Medium" in ore_quality:
            so2_factor = 1.3
        else:
            so2_factor = 1.6
        so2_kg_total = default_factors["so2_kg_per_t_copper"] * transport_tonnes * so2_factor

    if energy_source == "Coal-based grid":
        energy_factor_multiplier = 1.2
    elif energy_source == "Mixed grid":
        energy_factor_multiplier = 1.0
    else:
        energy_factor_multiplier = 0.8

    kgco2_per_kg = baseline * energy_factor_multiplier
    transport_kgco2_per_ton = default_factors["transport_kgco2_per_tkm"] * transport_km * transport_tonnes
    total_co2_per_tonne = kgco2_per_kg * 1000 + default_factors["transport_kgco2_per_tkm"] * transport_km
    circularity = recycled_pct * 0.5
    if eol_option == "Recycling":
        circularity += 30
    elif eol_option == "Reuse":
        circularity += 40
    circularity = min(100, circularity)
    recycle_cost = (default_factors["recycle_cost_usd_per_t_aluminium"] if metal == "Aluminium"
                    else default_factors["recycle_cost_usd_per_t_copper"]) * transport_tonnes

    st.header("Estimated Results (Illustrative)")
    colA, colB = st.columns(2)
    with colA:
        st.metric("CO₂ (per kg of metal) - estimated", f"{kgco2_per_kg:.2f} kg CO₂e / kg")
        st.metric("CO₂ (per tonne incl transport) - est.", f"{total_co2_per_tonne:.0f} kg CO₂e / t (incl transport)")
    with colB:
        st.metric("Circularity Score (0-100)", f"{circularity:.1f}")
        st.metric("Estimated recycling cost (USD)", f"{recycle_cost:,.2f} (for {transport_tonnes} t)")

    st.subheader("Breakdown (per tonne basis)")
    breakdown_df = pd.DataFrame({
        "Stage": ["Production+smelting (kg CO2e/kg *1000)", "Transport (kg CO2e/t)", "Total (kg CO2e/t)"],
        "Value": [kgco2_per_kg * 1000, default_factors["transport_kgco2_per_tkm"] * transport_km, total_co2_per_tonne],
    })
    st.table(breakdown_df)

    st.subheader("By-product / Toxic emissions (illustrative)")
    if metal == "Aluminium":
        st.write(
            f"Red mud estimate: **{red_mud_t:.2f} tonnes** of red mud produced for {transport_tonnes} t of aluminium "
            f"(typical literature estimate ~1.5 t red mud / t Al, adjusted by ore quality)."
        )
        st.write("Valuable routes: cement substitute, pigment (iron oxides), rare earth recovery (pilot scale). See CPCB red mud guidelines.")
    else:
        st.write(f"Estimated SO₂ generation: **{so2_kg_total:.1f} kg** for {transport_tonnes} t of copper smelted (illustrative).")
        st.write("Captured SO₂ can be converted to sulfuric acid (H₂SO₄) — valuable industrial chemical (fertilizers, chemicals).")

    st.markdown("---")
    st.subheader("Compliance card (quick flags)")
    flags = []
    if storage_practice != "Proper authorized storage":
        flags.append(("Storage practice", "⚠️ Not authorized/temporary storage — requires review under Hazardous & Other Wastes Rules (2016)"))
    if metal == "Aluminium" and red_mud_t > 0:
        flags.append(("Red mud handling", "ℹ️ Red mud generation flagged — follow CPCB Guidelines for Handling & Management of Red Mud"))
    if metal == "Copper" and so2_kg_total > 0:
        flags.append(("Air emissions", "ℹ️ SO₂ emissions estimated — recommend gas capture & conversion to sulfuric acid"))
    if circularity < 40:
        flags.append(("Circularity", "⚠️ Low circularity score — consider increasing recycled input or infrastructure"))
    for f in flags:
        st.warning(f"{f[0]}: {f[1]}")

    st.markdown("---")
    st.subheader("Recommendations (illustrative & pro-government)")
    recs = [
        "Increase recycled feedstock where feasible — reduces primary extraction & supports National Mineral Policy objectives.",
        "Invest in red mud neutralization & valorization (cement substitution/pigments/REE recovery) — follow CPCB technical guidelines.",
    ]
    if metal == "Copper":
        recs.append("Install SO₂ capture + contact process to convert to sulfuric acid and supply local fertilizer/chemical plants.")
    recs.append("Engage with local SPCB/CPCB for authorization and safe handling steps (the tool generates a compliance checklist).")
    for r in recs:
        st.info(r)

    st.markdown("---")
    st.subheader("Export report (PDF)")
    pdf_filename = "SustainaMine_LCA_Summary.pdf"
    if st.button("Export PDF Summary"):
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.set_font("Arial", size=12)
        except:
            pdf.set_font("helvetica", size=12)
        pdf.cell(0, 8, "SustainaMine - LCA Summary (Illustrative)", ln=True, align="C")
        pdf.ln(4)
        pdf.multi_cell(
            0, 6,
            f"Inputs:\nMetal: {metal}\nState: {state}\nRoute: {production_route}\nRecycled%: {recycled_pct}\nEnergy: {energy_source}\nTransport: {transport_km} km x {transport_tonnes} t\nEnd-of-life: {eol_option}\nStorage: {storage_practice}\n"
        )
        pdf.ln(2)
        pdf.multi_cell(
            0, 6,
            f"Estimated outputs (illustrative):\nCO2 per kg: {kgco2_per_kg:.2f} kg CO2/kg\nCO2 per t (incl transport): {total_co2_per_tonne:.0f} kg CO2/t\nCircularity score: {circularity:.1f}/100\n"
        )
        if metal == "Aluminium":
            pdf.multi_cell(0, 6, f"Red mud generation estimate: {red_mud_t:.2f} t (for {transport_tonnes} t Al).\n")
        else:
            pdf.multi_cell(0, 6, f"SO2 estimate: {so2_kg_total:.1f} kg — recommend capture and conversion to sulfuric acid.\n")
        pdf.output(pdf_filename)
        with open(pdf_filename, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_filename)
        st.success(f"{pdf_filename} generated (ready for download).")

st.markdown("---")
st.header("Data sources & references (open links)")
for k, v in SOURCES.items():
    st.write(f"- **{k}** : {v}")

st.markdown(
    "**Important note:** This prototype provides *illustrative* computations and policy references. Replace default parameters with validated process data and local SPCB thresholds before using for compliance submission. This tool **assists** compliance — it does not replace statutory approvals."
)
