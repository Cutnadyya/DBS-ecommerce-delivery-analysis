# =========================================================
# DASHBOARD ANALISIS DATA E-COMMERCE OLIST
# Dicoding ID: cut_nadya_putri_khairunnisa_510M
# =========================================================

# Import Library
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
    }

    h1 {
        color: #1E3A8A;
    }

    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")

    # Convert datetime
    datetime_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col])

    return df

df = load_data()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("📌 Filter Dashboard")

# Filter tanggal
min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

start_date, end_date = st.sidebar.date_input(
    label="Filter Rentang Tanggal",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter state
state_options = sorted(df["customer_state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    label="Filter Customer State",
    options=state_options,
    default=state_options[:5]
)

# =========================================================
# FILTER DATA
# =========================================================
filtered_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date)
]

if selected_states:
    filtered_df = filtered_df[
        filtered_df["customer_state"].isin(selected_states)
    ]

# =========================================================
# HEADER
# =========================================================
st.title("📊 E-Commerce Public Dataset Dashboard")

st.markdown("""
Dashboard ini menampilkan analisis performa pengiriman dan tren revenue
berdasarkan dataset transaksi E-Commerce Olist tahun 2017–2018.
""")

# =========================================================
# METRIC CARDS
# =========================================================
total_orders = filtered_df["order_id"].nunique()
total_revenue = filtered_df["payment_value"].sum()
avg_payment = filtered_df["payment_value"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,}"
    )

with col2:
    st.metric(
        label="Total Revenue",
        value=f"R$ {total_revenue:,.2f}"
    )

with col3:
    st.metric(
        label="Average Payment",
        value=f"R$ {avg_payment:,.2f}"
    )

st.markdown("---")

# =========================================================
# VISUALISASI 1
# KETERLAMBATAN PENGIRIMAN
# =========================================================
st.subheader("📦 Delivery Delay Percentage by State")

# Membuat kolom delay
filtered_df["delivery_delay"] = (
    filtered_df["order_delivered_customer_date"] >
    filtered_df["order_estimated_delivery_date"]
)

# Top 5 states
top_states = (
    filtered_df.groupby("customer_state")["order_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(5)
    .index
)

delay_df = filtered_df[
    filtered_df["customer_state"].isin(top_states)
]

delay_analysis = (
    delay_df.groupby("customer_state")["delivery_delay"]
    .mean()
    .sort_values(ascending=False) * 100
)

# Plot
fig, ax = plt.subplots(figsize=(10,5))

colors = sns.color_palette("Reds_r", len(delay_analysis))

sns.barplot(
    x=delay_analysis.index,
    y=delay_analysis.values,
    palette=colors,
    ax=ax
)

ax.set_title("Percentage of Late Deliveries in Top States")
ax.set_xlabel("Customer State")
ax.set_ylabel("Late Delivery Percentage (%)")

for i, v in enumerate(delay_analysis.values):
    ax.text(i, v + 0.5, f"{v:.2f}%", ha='center')

st.pyplot(fig)

# Insight
highest_delay_state = delay_analysis.idxmax()
highest_delay_value = delay_analysis.max()

st.markdown(f"""
### 📌 Insight
State dengan tingkat keterlambatan tertinggi adalah **{highest_delay_state}**
dengan persentase keterlambatan sebesar **{highest_delay_value:.2f}%**.

Hal ini menunjukkan bahwa wilayah dengan volume transaksi tinggi
cenderung memiliki tekanan logistik yang lebih besar.
Perusahaan dapat mempertimbangkan evaluasi kurir dan optimalisasi distribusi
di wilayah tersebut.
""")

st.markdown("---")

# =========================================================
# VISUALISASI 2
# TREN REVENUE BULANAN
# =========================================================
st.subheader("💰 Monthly Revenue Trend")

# Membuat kolom bulan
filtered_df["purchase_month"] = (
    filtered_df["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

monthly_revenue = (
    filtered_df.groupby("purchase_month")["payment_value"]
    .sum()
    .reset_index()
)

# Plot line chart
fig2, ax2 = plt.subplots(figsize=(14,6))

sns.lineplot(
    data=monthly_revenue,
    x="purchase_month",
    y="payment_value",
    marker="o",
    linewidth=2.5,
    color="#2563EB",
    ax=ax2
)

ax2.set_title("Monthly Revenue Trend (2017–2018)")
ax2.set_xlabel("Month")
ax2.set_ylabel("Revenue")

plt.xticks(rotation=45)

st.pyplot(fig2)

# Insight revenue
peak_month = monthly_revenue.loc[
    monthly_revenue["payment_value"].idxmax()
]

st.markdown(f"""
### 📌 Insight
Revenue perusahaan menunjukkan tren yang cenderung meningkat
selama periode analisis.

Revenue tertinggi terjadi pada bulan **{peak_month['purchase_month']}**
dengan total revenue sebesar
**R$ {peak_month['payment_value']:,.2f}**.

Hal ini mengindikasikan adanya pertumbuhan aktivitas transaksi pelanggan.
Perusahaan dapat memanfaatkan pola seasonal sales dan meningkatkan promosi
pada bulan dengan revenue rendah.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption(
    "Dashboard Analisis Data E-Commerce Olist • "
    "Dicoding Submission Project"
)
