import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nigeria Trade & Customs Dashboard", layout="wide")
st.title("Nigeria Trade & Customs Analytics Dashboard")

# --- Upload data ---
uploaded_file = st.file_uploader("Upload your cleaned import data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Convert date
    if 'Receipt Date' in df.columns:
        df['Receipt Date'] = pd.to_datetime(df['Receipt Date'], errors='coerce')
        
    # Strip whitespace
    df['Container Size'] = df['Container Size'].astype(str).str.strip()

    # Replace common unknown markers with NaN
    df['Container Size'] = df['Container Size'].replace(
        ['unknown', 'Unknown', 'UNKNOWN', '', 'nan', 'None'], pd.NA
    )


    # ----------- CALCULATIONS -------------
    # 1. Import Volume and Value KPIs
    total_fob = df['FOB Value (N)'].sum()
    total_cif = df['CIF Value (N)'].sum()
    avg_fob = df['FOB Value (N)'].mean()
    avg_cif = df['CIF Value (N)'].mean()
    avg_mass = df['Mass(KG)'].mean()
    top_countries = df.groupby('Country  of Origin')['CIF Value (N)'].sum().sort_values(ascending=False).head(10)
    top_importers = df.groupby('Importer')['Mass(KG)'].sum().sort_values(ascending=False).head(10)

    # 2. Taxation & Revenue KPIs
    total_tax = df['Total Tax(N)'].sum()
    avg_tax = df['Total Tax(N)'].mean()
    tax_to_value_ratio = total_tax / total_cif if total_cif > 0 else 0
    top_tax_importers = df.groupby('Importer')['Total Tax(N)'].sum().sort_values(ascending=False).head(10)

    # 3. Logistics and Shipment KPIs
    total_shipments = df['Reg Number'].nunique()
    avg_containers_per_importer = df['Nbr Of Containers'].sum() / df['Importer'].nunique()
    most_common_container_size = df['Container Size'].mode()[0] if df['Container Size'].notna().any() else "N/A"
    total_weight_by_country = df.groupby('Country  of Origin')['Mass(KG)'].sum().sort_values(ascending=False).head(10)

    # 4. Compliance and Processing KPIs
    transactions_per_office = df.groupby('Custom Office')['Reg Number'].nunique().sort_values(ascending=False)
    most_frequent_hs = df['HS Code'].value_counts().head(10)
    corr_data = df[["FOB Value (N)", "CIF Value (N)", "Mass(KG)", "Total Tax(N)"]]

    # Calculate correlation matrix
    corr_matrix = corr_data.corr(method="pearson")


    # Example high-risk countries list (customise for your use case)
    high_risk_countries = ['Afghanistan', 'Iran', 'North Korea']
    df['HighRisk'] = df['Country  of Origin'].isin(high_risk_countries)
    pct_high_risk = (df['HighRisk'].sum() / len(df)) if len(df) > 0 else 0

    # Timeliness of Tax Payments (requires a tax date field)
    # Here we just show % with missing Receipt Date as "late"
    if 'Receipt Date' in df.columns:
        pct_with_date = df['Receipt Date'].notna().mean()
        timeliness_metric = pct_with_date
    else:
        timeliness_metric = None

    # ----------- KPI CARDS -------------
    st.subheader("Import Volume & Value KPIs")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total FOB Value (₦ Million)", f"{total_fob/1_000_000:,.2f}")
    c2.metric("Total CIF Value (₦ Million)", f"{total_cif/1_000_000:,.2f}")
    c3.metric("Avg FOB per Transaction (₦)", f"{avg_fob:,.0f}")
    c4.metric("Avg CIF per Transaction (₦)", f"{avg_cif:,.0f}")
    c5.metric("Avg Mass per Transaction (KG)", f"{avg_mass:,.0f}")

    st.subheader("Taxation & Revenue KPIs")
    t1,t2,t3,t4 = st.columns(4)
    t1.metric("Total Tax Collected (₦ Million)", f"{total_tax/1_000_000:,.2f}")
    t2.metric("Avg Tax per Transaction (₦)", f"{avg_tax:,.0f}")
    t3.metric("Tax-to-Value Ratio", f"{tax_to_value_ratio:.2%}")
    t4.metric("Top Tax-Contributing Importers (see chart below)", "")

    st.subheader("Logistics & Shipment KPIs")
    l1,l2,l3,l4 = st.columns(4)
    l1.metric("Total Number of Shipments", f"{total_shipments:,}")
    l2.metric("Avg Containers per Importer", f"{avg_containers_per_importer:,.2f}")
    l3.metric("Most Common Container Size", f"{most_common_container_size}")
    l4.metric("Top Countries by Total Weight (see chart below)", "")

    st.subheader("Compliance & Processing KPIs")
    cp1,cp2,cp3,cp4 = st.columns(4)
    cp1.metric("No. of Transactions per Custom Office (see chart)", "")
    cp2.metric("Most Frequent HS Codes (see chart)", "")
    cp3.metric("% Imports from High-Risk Countries", f"{pct_high_risk:.2%}")
    if timeliness_metric is not None:
        cp4.metric("Timeliness of Tax Payments (have receipt date)", f"{timeliness_metric:.2%}")

    st.divider()

    # ----------- VISUALS -------------
    st.subheader("Top 10 Importing Countries by CIF Value (₦ Million)")
    fig1, ax1 = plt.subplots(figsize=(10,5))
    (top_countries/1_000_000).plot(kind='bar', ax=ax1, color='steelblue')
    ax1.set_ylabel("CIF Value (₦ Million)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

    st.subheader("Top 10 Importers by Volume (Mass KG)")
    fig2, ax2 = plt.subplots(figsize=(10,5))
    top_importers.plot(kind='bar', ax=ax2, color='green')
    ax2.set_ylabel("Mass (KG)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig2)

    st.subheader("Top 10 Tax-Contributing Importers (₦ Million)")
    fig3, ax3 = plt.subplots(figsize=(10,5))
    (top_tax_importers/1_000_000).plot(kind='bar', ax=ax3, color='indianred')
    ax3.set_ylabel("Tax (₦ Million)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig3)

    st.subheader("Total Weight of Imports by Country of Origin (KG)")
    fig4, ax4 = plt.subplots(figsize=(10,5))
    total_weight_by_country.plot(kind='bar', ax=ax4, color='purple')
    ax4.set_ylabel("Mass (KG)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig4)

    st.subheader("Number of Transactions per Custom Office")
    fig5, ax5 = plt.subplots(figsize=(10,5))
    transactions_per_office.plot(kind='bar', ax=ax5, color='grey')
    ax5.set_ylabel("Transactions")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig5)

    st.subheader("Most Frequent HS Codes")
    fig6, ax6 = plt.subplots(figsize=(10,5))
    most_frequent_hs.plot(kind='bar', ax=ax6, color='teal')
    ax6.set_ylabel("Frequency")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig6)
    
    st.subheader("Correlation between Values and Taxes")
    fig7, ax7 = plt.subplots(figsize=(10,5))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    st.pyplot(fig7)

    st.subheader("Number of Shipments Registered by each Custom Office")

    # Aggregate counts
    shipments_by_office = (
        df.groupby('Custom Office')['Reg Number']
        .nunique()  # count unique Reg Numbers
        .sort_values(ascending=False)
        .reset_index(name='Shipments')
    )

    fig8, ax8 = plt.subplots(figsize=(10,5))
    sns.barplot(data=shipments_by_office, 
                y='Custom Office', x='Shipments', color='steelblue', ax=ax8)
    ax8.set_xlabel("Number of Registered Shipments")
    ax8.set_ylabel("Custom Office")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig8)

    
    # Trend over time (CIF)
    if 'Receipt Date' in df.columns:
        st.subheader("Monthly CIF Value Trend (₦ Million)")
        df['YearMonth'] = df['Receipt Date'].dt.to_period('M')
        monthly_cif = df.groupby('YearMonth')['CIF Value (N)'].sum()
        fig9, ax9 = plt.subplots(figsize=(10,5))
        (monthly_cif/1_000_000).plot(marker='o', ax=ax9, color='darkorange')
        ax9.set_ylabel("CIF Value (₦ Million)")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig9)
else:
    st.info("Upload a CSV file to see the dashboard.")
