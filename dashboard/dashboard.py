# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="DBS E-Commerce Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to bottom, #F8FAFC, #EEF2FF);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #0F172A, #1E293B);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 6px 18px rgba(15, 23, 42, 0.08);
    }

    h1 {
        color: #0F172A;
        font-weight: 700;
    }

    h2, h3 {
        color: #1E293B;
    }

    div[data-baseweb="tab-list"] {
        gap: 12px;
    }

    button[data-baseweb="tab"] {
        background-color: white;
        border-radius: 12px;
        padding: 10px 18px;
        border: 1px solid #CBD5E1;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        color: white !important;
    }

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }
</style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data

def load_data():
    df = pd.read_csv("dashboard/all_data_2017.csv")
    return df


df = load_data()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3081/3081559.png",
    width=120
)

st.sidebar.title("📌 Profil Dashboard")

st.sidebar.markdown("### 👩‍💻 Nama")
st.sidebar.write("CUT NADYA PUTRI KHAIRUNNISA")

st.sidebar.markdown("### 🎓 Universitas")
st.sidebar.write("IPB University")

st.sidebar.markdown("### 📊 Project")
st.sidebar.write("E-Commerce Data Analysis")

st.sidebar.markdown("---")

# FILTER

default_states = ["SP", "RJ", "MG"]

selected_state = st.sidebar.multiselect(
    "📍 Pilih State",
    options=sorted(df["customer_state"].dropna().unique()),
    default=default_states
)

filtered_df = df[
    df["customer_state"].isin(selected_state)
]

# =====================================================
# HEADER
# =====================================================

st.title("📦 DBS E-Commerce Performance Dashboard")

st.markdown(
    """
    Dashboard ini digunakan untuk menganalisis performa transaksi e-commerce tahun 2017 berdasarkan wilayah pelanggan, tingkat kepuasan pelanggan, serta potensi nilai transaksi pada setiap state.
    """
)

st.markdown("---")

# =====================================================
# KPI SECTION
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🛒 Total Orders",
        f"{filtered_df['order_id'].nunique():,}"
    )

with col2:
    st.metric(
        "⭐ Average Review",
        round(filtered_df['review_score'].mean(), 2)
    )

with col3:
    st.metric(
        "💰 Average Payment",
        f"${round(filtered_df['payment_value'].mean(), 2)}"
    )

with col4:
    st.metric(
        "👥 Total Customers",
        f"{filtered_df['customer_unique_id'].nunique():,}"
    )

st.markdown("---")

# =====================================================
# TABS
# =====================================================


tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Order Analysis",
    "⭐ Review Analysis",
    "💰 Payment Analysis",
    "📈 Monthly Trend"
])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.subheader("Top State Based on Total Orders")

    state_orders = (
        filtered_df
        .groupby("customer_state")["order_id"]
        .nunique()
        .reset_index()
        .sort_values(by="order_id", ascending=False)
    )

    fig_orders = px.bar(
        state_orders,
        x="customer_state",
        y="order_id",
        color="order_id",
        text_auto=True,
        color_continuous_scale="Tealgrn",
        title="Total Orders per State"
    )

    st.plotly_chart(fig_orders, use_container_width=True)

    st.info(
        "State dengan jumlah order tertinggi menunjukkan wilayah dengan aktivitas transaksi terbesar selama tahun 2017."
    )

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.subheader("Average Review Score per State")

    review_state = (
        filtered_df
        .groupby("customer_state")["review_score"]
        .mean()
        .reset_index()
        .sort_values(by="review_score", ascending=False)
    )

    fig_review = px.bar(
        review_state,
        x="customer_state",
        y="review_score",
        color="review_score",
        text_auto='.2f',
        color_continuous_scale="Purp",
        title="Review Score per State"
    )

    st.plotly_chart(fig_review, use_container_width=True)

    st.warning(
        "State dengan review score rendah perlu menjadi perhatian karena menunjukkan tingkat kepuasan pelanggan yang belum optimal."
    )

# =====================================================
# TAB 3
# =====================================================

with tab3:

    st.subheader("Average Payment Value per State")

    payment_state = (
        filtered_df
        .groupby("customer_state")["payment_value"]
        .mean()
        .reset_index()
        .sort_values(by="payment_value", ascending=False)
    )

    fig_payment = px.pie(
        payment_state.head(10),
        names="customer_state",
        values="payment_value",
        title="Payment Contribution by State",
        hole=0.4
    )

    st.plotly_chart(fig_payment, use_container_width=True)

    st.success(
        "State dengan average payment value tinggi memiliki potensi kontribusi revenue yang lebih besar."
    )

# =====================================================
# TAB 4
# =====================================================

with tab4:

    st.subheader("Monthly Order Trend")

    if "purchase_month_name" in filtered_df.columns:

        monthly_orders = (
            filtered_df
            .groupby("purchase_month_name")["order_id"]
            .nunique()
            .reset_index()
        )

        fig_month = px.line(
            monthly_orders,
            x="purchase_month_name",
            y="order_id",
            markers=True,
            title="Monthly Orders Trend"
        )

        fig_month.update_traces(
            line_color="#7C3AED",
            marker=dict(size=11)
        )

        st.plotly_chart(fig_month, use_container_width=True)

# =====================================================
# TOP 10 TABLE
# =====================================================

st.markdown("---")

st.subheader("🏆 Top 10 States")


top10 = (
    filtered_df
    .groupby("customer_state")["order_id"]
    .nunique()
    .reset_index()
    .sort_values(by="order_id", ascending=False)
    .head(10)
)

st.dataframe(top10, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "DBS Coding Camp 2026 | E-Commerce Analysis Dashboard by CUT NADYA PUTRI KHAIRUNNISA"
)

