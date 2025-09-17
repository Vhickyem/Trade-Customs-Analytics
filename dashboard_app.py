import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nigeria Trade & Customs Dashboard", layout="wide")
st.title("Nigeria Trade & Customs Analytics Dashboard")

# --- Upload data ---
df = pd.read_csv("cleaned_import_data.csv")

# Convert date
if 'Receipt Date' in df.columns:
    df['Receipt Date'] = pd.to_datetime(df['Receipt Date'], errors='coerce')
    
# Strip whitespace
df['Container Size'] = df['Container Size'].astype(str).str.strip()

# Replace common unknown markers with NaN
df['Container Size'] = df['Container Size'].replace(
    ['unknown', 'Unknown', 'UNKNOWN', '', 'nan', 'None'], pd.NA
)

# Sidebar title
st.sidebar.title("Filters")
st.sidebar.markdown("**Trade & Customs Dashboard**")
st.sidebar.markdown("Use the controls below to filter data.")

# Sidebar controls
# Helper to build options with "All"
def make_options(series):
    opts = sorted(series.dropna().unique().tolist())
    return ["All"] + opts

country_options = make_options(df['Country  of Origin'])
selected_countries = st.sidebar.multiselect(
    "Select Countries (or All)",
    country_options,
    default=["All"]  # preselect All
)

# --- Importers ---
importer_options = make_options(df['Importer'])
selected_importers = st.sidebar.multiselect(
    "Importers",
    importer_options,
    default=["All"]
)

# --- HS Codes ---
hs_options = make_options(df['HS Code'])
selected_hs = st.sidebar.multiselect(
    "HS Codes",
    hs_options,
    default=["All"]
)

# --- Container Size ---
size_options = make_options(df['Container Size'])
selected_size = st.sidebar.multiselect(
    "Container Size",
    size_options,
    default=["All"]
)

# --- Custom Office ---
office_options = make_options(df['Custom Office'])
selected_office = st.sidebar.multiselect(
    "Custom Office",
    office_options,
    default=["All"]
)

# get all available years from the date column
years = sorted(df['Receipt Date'].dt.year.dropna().unique())

# create a slider for a year range
year_min = int(min(years))
year_max = int(max(years))

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)  # default selects the whole range
)

# Start with all data
filtered_df = df.copy()

# Country filter
if not ("All" in selected_countries or not selected_countries):
    filtered_df = filtered_df[filtered_df['Country  of Origin'].isin(selected_countries)]

# Importers filter
if not ("All" in selected_importers or not selected_importers):
    filtered_df = filtered_df[filtered_df['Importer'].isin(selected_importers)]

# HS Codes filter
if not ("All" in selected_hs or not selected_hs):
    filtered_df = filtered_df[filtered_df['HS Code'].isin(selected_hs)]

# Container Size filter
if not ("All" in selected_size or not selected_size):
    filtered_df = filtered_df[filtered_df['Container Size'].isin(selected_size)]

# Custom Office filter
if not ("All" in selected_office or not selected_office):
    filtered_df = filtered_df[filtered_df['Custom Office'].isin(selected_office)]

start_year, end_year = selected_years

if 'Receipt Date' in filtered_df.columns:
    filtered_df = filtered_df[
        (
            (filtered_df['Receipt Date'].dt.year >= start_year) &
            (filtered_df['Receipt Date'].dt.year <= end_year)
        )
        |
        (filtered_df['Receipt Date'].isna())  # <--- include missing dates
    ]
    
st.markdown(
    f"**Showing {len(filtered_df):,} of {len(df):,} rows from {start_year} to {end_year}"
    f"({len(filtered_df)/len(df):.1%})**"
)


# ----------- CALCULATIONS -------------
# 1. Import Volume and Value KPIs
total_fob = filtered_df['FOB Value (N)'].sum()
total_cif = filtered_df['CIF Value (N)'].sum()
avg_fob = filtered_df['FOB Value (N)'].mean()
avg_cif = filtered_df['CIF Value (N)'].mean()
avg_mass = filtered_df['Mass(KG)'].mean()
top_countries = filtered_df.groupby('Country  of Origin')['CIF Value (N)'].sum().sort_values(ascending=False).head(10)
top_importers = filtered_df.groupby('Importer')['Mass(KG)'].sum().sort_values(ascending=False).head(10)

# 2. Taxation & Revenue KPIs
total_tax = filtered_df['Total Tax(N)'].sum()
avg_tax = filtered_df['Total Tax(N)'].mean()
tax_to_value_ratio = total_tax / total_cif if total_cif > 0 else 0
top_tax_importers = filtered_df.groupby('Importer')['Total Tax(N)'].sum().sort_values(ascending=False).head(10)

# 3. Logistics and Shipment KPIs
total_shipments = filtered_df['Reg Number'].nunique()
avg_containers_per_importer = filtered_df['Nbr Of Containers'].sum() / filtered_df['Importer'].nunique()
most_common_container_size = filtered_df['Container Size'].mode()[0] if filtered_df['Container Size'].notna().any() else "N/A"
total_weight_by_country = filtered_df.groupby('Country  of Origin')['Mass(KG)'].sum().sort_values(ascending=False).head(10)

# 4. Compliance and Processing KPIs
transactions_per_office = filtered_df.groupby('Custom Office')['Reg Number'].nunique().sort_values(ascending=False)
most_frequent_hs = filtered_df['HS Code'].value_counts().head(10)
corr_data = filtered_df[["FOB Value (N)", "CIF Value (N)", "Mass(KG)", "Total Tax(N)"]]

# Calculate correlation matrix
corr_matrix = corr_data.corr(method="pearson")


# Example high-risk countries list (customise for your use case)
high_risk_countries = ['Afghanistan', 'Iran', 'North Korea']
filtered_df['HighRisk'] = filtered_df['Country  of Origin'].isin(high_risk_countries)
pct_high_risk = (filtered_df['HighRisk'].sum() / len(filtered_df)) if len(filtered_df) > 0 else 0

# Timeliness of Tax Payments (requires a tax date field)
# Here we just show % with missing Receipt Date as "late"
if 'Receipt Date' in filtered_df.columns:
    pct_with_date = filtered_df['Receipt Date'].notna().mean()
    timeliness_metric = pct_with_date
else:
    timeliness_metric = None

st.subheader("📦 Import Volume & Value KPIs")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total FOB Value (₦ Million)", f"{total_fob/1_000_000:,.2f}")
c2.metric("Total CIF Value (₦ Million)", f"{total_cif/1_000_000:,.2f}")
c3.metric("Avg FOB per Transaction (₦)", f"{avg_fob:,.0f}")
c4.metric("Avg CIF per Transaction (₦)", f"{avg_cif:,.0f}")
c5.metric("Avg Mass per Transaction (KG)", f"{avg_mass:,.0f}")

# Trend over time (CIF)
if 'Receipt Date' in filtered_df.columns:
    st.subheader("Monthly CIF Value Trend (₦ Million)")
    filtered_df['YearMonth'] = filtered_df['Receipt Date'].dt.to_period('M')
    monthly_cif = filtered_df.groupby('YearMonth')['CIF Value (N)'].sum()
    fig9, ax9 = plt.subplots(figsize=(6,4))
    (monthly_cif/1_000_000).plot(marker='o', ax=ax9, color='darkorange')
    ax9.set_ylabel("CIF Value (₦ Million)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig9)

st.subheader("Top 10 Importers by Volume (Mass KG)")
fig2, ax2 = plt.subplots(figsize=(6,4))
top_importers.plot(kind='bar', ax=ax2, color='green')
ax2.set_ylabel("Mass (KG)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig2)

st.divider()

st.subheader("💰 Taxation & Revenue KPIs")
t1,t2,t3,t4 = st.columns(4)
t1.metric("Total Tax Collected (₦ Million)", f"{total_tax/1_000_000:,.2f}")
t2.metric("Avg Tax per Transaction (₦)", f"{avg_tax:,.0f}")
t3.metric("Tax-to-Value Ratio", f"{tax_to_value_ratio:.2%}")
t4.metric("Top Tax-Contributing Importers (see chart below)", "")

st.subheader("Top 10 Importing Countries by CIF Value (₦ Million)")
fig1, ax1 = plt.subplots(figsize=(6,4))
(top_countries/1_000_000).plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_ylabel("CIF Value (₦ Million)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.subheader("Top 10 Tax-Contributing Importers (₦ Million)")
fig3, ax3 = plt.subplots(figsize=(10,5))
(top_tax_importers/1_000_000).plot(kind='bar', ax=ax3, color='indianred')
ax3.set_ylabel("Tax (₦ Million)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig3)

st.divider()

st.subheader("🚢 Logistics & Shipment KPIs")
l1,l2,l3,l4 = st.columns(4)
l1.metric("Total Number of Shipments", f"{total_shipments:,}")
l2.metric("Avg Containers per Importer", f"{avg_containers_per_importer:,.2f}")
l3.metric("Most Common Container Size", f"{most_common_container_size}")
l4.metric("Top Countries by Total Weight (see chart below)", "")

st.subheader("Total Weight of Imports by Country of Origin (KG)")
fig4, ax4 = plt.subplots(figsize=(6,4))
total_weight_by_country.plot(kind='bar', ax=ax4, color='purple')
ax4.set_ylabel("Mass (KG)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig4)

st.subheader("Number of Transactions per Custom Office")
fig5, ax5 = plt.subplots(figsize=(6,4))
transactions_per_office.plot(kind='bar', ax=ax5, color='grey')
ax5.set_ylabel("Transactions")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig5)

st.divider()

st.subheader("🛡️ Compliance & Processing KPIs")
cp1,cp2,cp3,cp4 = st.columns(4)
cp1.metric("No. of Transactions per Custom Office (see chart)", "")
cp2.metric("Most Frequent HS Codes (see chart)", "")
cp3.metric("% Imports from High-Risk Countries", f"{pct_high_risk:.2%}")
if timeliness_metric is not None:
    cp4.metric("Timeliness of Tax Payments (have receipt date)", f"{timeliness_metric:.2%}")

st.subheader("Most Frequent HS Codes")
fig6, ax6 = plt.subplots(figsize=(6,4))
most_frequent_hs.plot(kind='bar', ax=ax6, color='teal')
ax6.set_ylabel("Frequency")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig6)

st.subheader("Correlation between Values and Taxes")
fig7, ax7 = plt.subplots(figsize=(6,4))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
st.pyplot(fig7)

st.subheader("Number of Shipments Registered by each Custom Office")

# Aggregate counts
shipments_by_office = (
    filtered_df.groupby('Custom Office')['Reg Number']
    .nunique()  # count unique Reg Numbers
    .sort_values(ascending=False)
    .reset_index(name='Shipments')
)

fig8, ax8 = plt.subplots(figsize=(6,4))
sns.barplot(data=shipments_by_office, 
            y='Custom Office', x='Shipments', color='steelblue', ax=ax8)
ax8.set_xlabel("Number of Registered Shipments")
ax8.set_ylabel("Custom Office")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig8)
