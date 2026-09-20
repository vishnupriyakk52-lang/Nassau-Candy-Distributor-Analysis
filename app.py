import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)


# ---------------------------------------------------------
# FIND EXCEL FILE
# ---------------------------------------------------------

BASE_DIR = Path(__file__).parent

excel_files = list(BASE_DIR.glob("*.xlsx")) + list(BASE_DIR.glob("*.xlsm"))

if not excel_files:
    st.error("No Excel workbook was found in the Nassau_Candy_Streamlit folder.")
    st.stop()

# Prefer the Nassau Candy workbook
nassau_files = [
    f for f in excel_files
    if "nassau" in f.name.lower()
]

if nassau_files:
    EXCEL_FILE = nassau_files[0]
else:
    EXCEL_FILE = excel_files[0]


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data(file_path):

    df = pd.read_excel(
        file_path,
        sheet_name="Nassau Candy Distributor"
    )

    return df


try:
    df = load_data(EXCEL_FILE)
except Exception as e:
    st.error(f"Could not read the Excel workbook: {e}")
    st.stop()


# ---------------------------------------------------------
# CLEAN COLUMN NAMES
# ---------------------------------------------------------

df.columns = df.columns.str.strip()


required_columns = [
    "Order Date",
    "Division",
    "Product Name",
    "Sales",
    "Cost",
    "Units",
    "Gross Profit"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "The following required columns are missing from the Excel sheet: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ---------------------------------------------------------
# DATA PREPARATION
# ---------------------------------------------------------

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)

numeric_columns = [
    "Sales",
    "Cost",
    "Units",
    "Gross Profit"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=[
        "Order Date",
        "Division",
        "Product Name",
        "Sales",
        "Cost",
        "Units",
        "Gross Profit"
    ]
)

# Margin %
df["Margin %"] = (
    df["Gross Profit"] / df["Sales"].replace(0, pd.NA)
) * 100

# Profit per Unit
df["Profit per Unit"] = (
    df["Gross Profit"] / df["Units"].replace(0, pd.NA)
)

df["Margin %"] = pd.to_numeric(
    df["Margin %"],
    errors="coerce"
)

df["Profit per Unit"] = pd.to_numeric(
    df["Profit per Unit"],
    errors="coerce"
)

df = df.replace(
    [float("inf"), float("-inf")],
    pd.NA
)

df = df.dropna(
    subset=["Margin %"]
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title(
    "🍬 Nassau Candy Distributor"
)

st.subheader(
    "Product Line Profitability & Margin Performance Analysis"
)

st.caption(
    "Interactive Streamlit dashboard for product, division, "
    "cost, margin and profit-concentration analysis."
)


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")


# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_df = df[
        (df["Order Date"] >= start_date)
        &
        (df["Order Date"] <= end_date)
    ].copy()

else:
    filtered_df = df.copy()


# Division filter
divisions = sorted(
    filtered_df["Division"].dropna().unique().tolist()
)

selected_divisions = st.sidebar.multiselect(
    "Division",
    options=divisions,
    default=divisions
)

if selected_divisions:
    filtered_df = filtered_df[
        filtered_df["Division"].isin(selected_divisions)
    ]


# Margin threshold
margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)


# Product search
product_search = st.sidebar.text_input(
    "Product Search",
    placeholder="Type product name..."
)

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .astype(str)
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ]


if filtered_df.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()


# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_units = filtered_df["Units"].sum()

average_margin = filtered_df["Margin %"].mean()

profit_per_unit = (
    total_profit / total_units
    if total_units != 0
    else 0
)


# Margin volatility
monthly_margin = (
    filtered_df
    .assign(
        YearMonth=filtered_df["Order Date"].dt.to_period("M")
    )
    .groupby("YearMonth")["Margin %"]
    .mean()
)

margin_volatility = (
    monthly_margin.std()
    if len(monthly_margin) > 1
    else 0
)


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.markdown("## 📌 Key Performance Indicators")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Total Sales",
    f"${total_sales:,.2f}"
)

k2.metric(
    "Gross Profit",
    f"${total_profit:,.2f}"
)

k3.metric(
    "Total Units",
    f"{total_units:,.0f}"
)

k4.metric(
    "Average Margin",
    f"{average_margin:.0f}%"
)

k5.metric(
    "Margin Volatility",
    f"{margin_volatility:.2f}%"
)


# ---------------------------------------------------------
# PRODUCT PROFITABILITY OVERVIEW
# ---------------------------------------------------------

st.markdown("---")
st.header("1️⃣ Product Profitability Overview")


product_summary = (
    filtered_df
    .groupby("Product Name", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
        Average_Margin=("Margin %", "mean")
    )
)

product_summary["Profit_per_Unit"] = (
    product_summary["Gross_Profit"]
    / product_summary["Units"].replace(0, pd.NA)
)

product_summary["Revenue_Contribution"] = (
    product_summary["Sales"]
    / product_summary["Sales"].sum()
    * 100
)

product_summary["Profit_Contribution"] = (
    product_summary["Gross_Profit"]
    / product_summary["Gross_Profit"].sum()
    * 100
)


# Product profitability table
st.subheader("Product-Level Margin Leaderboard")

leaderboard = product_summary.sort_values(
    "Gross_Profit",
    ascending=False
).copy()

leaderboard_display = leaderboard[
    [
        "Product Name",
        "Sales",
        "Gross_Profit",
        "Average_Margin",
        "Profit_per_Unit",
        "Revenue_Contribution",
        "Profit_Contribution"
    ]
].copy()

leaderboard_display.columns = [
    "Product",
    "Sales",
    "Gross Profit",
    "Average Margin %",
    "Profit per Unit",
    "Revenue Contribution %",
    "Profit Contribution %"
]

st.dataframe(
    leaderboard_display.style.format({
        "Sales": "${:,.2f}",
        "Gross Profit": "${:,.2f}",
        "Average Margin %": "{:.1f}%",
        "Profit per Unit": "${:,.2f}",
        "Revenue Contribution %": "{:.1f}%",
        "Profit Contribution %": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)


# Top profit products
top_profit = leaderboard.head(10)

fig_profit = px.bar(
    top_profit.sort_values("Gross_Profit"),
    x="Gross_Profit",
    y="Product Name",
    orientation="h",
    title="Top Products by Gross Profit",
    labels={
        "Gross_Profit": "Gross Profit",
        "Product Name": "Product"
    }
)

st.plotly_chart(
    fig_profit,
    use_container_width=True
)


# ---------------------------------------------------------
# PRODUCT PROFITABILITY CLASSIFICATION
# ---------------------------------------------------------

st.subheader("Product Profitability Classification")

median_sales = product_summary["Sales"].median()

median_profit = product_summary["Gross_Profit"].median()

median_margin = product_summary["Average_Margin"].median()


def classify_product(row):

    if (
        row["Gross_Profit"] >= median_profit
        and row["Average_Margin"] >= median_margin
    ):
        return "High Profit / High Margin"

    elif (
        row["Sales"] >= median_sales
        and row["Average_Margin"] < median_margin
    ):
        return "High Sales / Low Margin"

    elif (
        row["Sales"] < median_sales
        and row["Gross_Profit"] < median_profit
    ):
        return "Low Sales / Low Profit"

    else:
        return "Other"


product_summary["Classification"] = (
    product_summary.apply(
        classify_product,
        axis=1
    )
)


classification_counts = (
    product_summary["Classification"]
    .value_counts()
    .reset_index()
)

classification_counts.columns = [
    "Classification",
    "Products"
]

fig_classification = px.bar(
    classification_counts,
    x="Classification",
    y="Products",
    title="Product Profitability Classification",
    text="Products"
)

st.plotly_chart(
    fig_classification,
    use_container_width=True
)


# ---------------------------------------------------------
# DIVISION PERFORMANCE DASHBOARD
# ---------------------------------------------------------

st.markdown("---")
st.header("2️⃣ Division Performance Dashboard")


division_summary = (
    filtered_df
    .groupby("Division", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Margin=("Margin %", "mean")
    )
)


col1, col2 = st.columns(2)


with col1:

    fig_division = px.bar(
        division_summary,
        x="Division",
        y=["Sales", "Gross_Profit"],
        barmode="group",
        title="Revenue vs Gross Profit by Division",
        labels={
            "value": "Amount",
            "variable": "Metric"
        }
    )

    st.plotly_chart(
        fig_division,
        use_container_width=True
    )


with col2:

    fig_division_margin = px.bar(
        division_summary,
        x="Division",
        y="Average_Margin",
        title="Average Margin % by Division",
        labels={
            "Average_Margin": "Average Margin %"
        },
        text_auto=".1f"
    )

    st.plotly_chart(
        fig_division_margin,
        use_container_width=True
    )


st.dataframe(
    division_summary.style.format({
        "Sales": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Average_Margin": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# COST VS MARGIN DIAGNOSTICS
# ---------------------------------------------------------

st.markdown("---")
st.header("3️⃣ Cost vs Margin Diagnostics")


cost_margin = (
    filtered_df
    .groupby("Product Name", as_index=False)
    .agg(
        Cost=("Cost", "sum"),
        Sales=("Sales", "sum"),
        Average_Margin=("Margin %", "mean"),
        Gross_Profit=("Gross Profit", "sum")
    )
)


fig_cost_margin = px.scatter(
    cost_margin,
    x="Cost",
    y="Average_Margin",
    size="Gross_Profit",
    hover_name="Product Name",
    title="Cost vs Margin Diagnostic",
    labels={
        "Cost": "Total Cost",
        "Average_Margin": "Average Margin %"
    }
)

fig_cost_margin.add_hline(
    y=margin_threshold,
    line_dash="dash",
    annotation_text=f"Margin Threshold: {margin_threshold}%"
)

st.plotly_chart(
    fig_cost_margin,
    use_container_width=True
)


# Cost vs Sales
fig_cost_sales = px.scatter(
    cost_margin,
    x="Cost",
    y="Sales",
    size="Gross_Profit",
    hover_name="Product Name",
    title="Cost vs Sales Diagnostic",
    labels={
        "Cost": "Total Cost",
        "Sales": "Total Sales"
    }
)

st.plotly_chart(
    fig_cost_sales,
    use_container_width=True
)


# Margin risk products
risk_products = product_summary[
    product_summary["Average_Margin"] <= margin_threshold
].sort_values(
    "Average_Margin"
)

st.subheader(
    f"Margin Risk Flags — Products ≤ {margin_threshold}% Margin"
)

if risk_products.empty:

    st.success(
        "No products are below the selected margin threshold."
    )

else:

    risk_display = risk_products[
        [
            "Product Name",
            "Sales",
            "Gross_Profit",
            "Average_Margin"
        ]
    ].copy()

    risk_display.columns = [
        "Product",
        "Sales",
        "Gross Profit",
        "Average Margin %"
    ]

    st.dataframe(
        risk_display.style.format({
            "Sales": "${:,.2f}",
            "Gross Profit": "${:,.2f}",
            "Average Margin %": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# PROFIT CONCENTRATION ANALYSIS
# ---------------------------------------------------------

st.markdown("---")
st.header("4️⃣ Profit Concentration Analysis")


# Profit Pareto
profit_pareto = (
    product_summary
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .copy()
)

profit_pareto["Cumulative_Profit"] = (
    profit_pareto["Gross_Profit"].cumsum()
    / profit_pareto["Gross_Profit"].sum()
    * 100
)

fig_pareto = go.Figure()

fig_pareto.add_trace(
    go.Bar(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Gross_Profit"],
        name="Gross Profit"
    )
)

fig_pareto.add_trace(
    go.Scatter(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Cumulative_Profit"],
        name="Cumulative %",
        yaxis="y2",
        mode="lines+markers"
    )
)

fig_pareto.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="80% Profit"
)

fig_pareto.update_layout(
    title="Gross Profit Pareto Analysis",
    xaxis_title="Product",
    yaxis_title="Gross Profit",
    yaxis2=dict(
        title="Cumulative Profit %",
        overlaying="y",
        side="right",
        range=[0, 100]
    )
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)


# Revenue Pareto
revenue_pareto = (
    product_summary
    .sort_values(
        "Sales",
        ascending=False
    )
    .copy()
)

revenue_pareto["Cumulative_Revenue"] = (
    revenue_pareto["Sales"].cumsum()
    / revenue_pareto["Sales"].sum()
    * 100
)

fig_revenue_pareto = go.Figure()

fig_revenue_pareto.add_trace(
    go.Bar(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Sales"],
        name="Revenue"
    )
)

fig_revenue_pareto.add_trace(
    go.Scatter(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Cumulative_Revenue"],
        name="Cumulative %",
        yaxis="y2",
        mode="lines+markers"
    )
)

fig_revenue_pareto.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="80% Revenue"
)

fig_revenue_pareto.update_layout(
    title="Revenue Pareto Analysis",
    xaxis_title="Product",
    yaxis_title="Revenue",
    yaxis2=dict(
        title="Cumulative Revenue %",
        overlaying="y",
        side="right",
        range=[0, 100]
    )
)

st.plotly_chart(
    fig_revenue_pareto,
    use_container_width=True
)


# ---------------------------------------------------------
# 80% DEPENDENCY INDICATORS
# ---------------------------------------------------------

def products_for_80_percent(series):

    sorted_values = series.sort_values(
        ascending=False
    )

    cumulative = (
        sorted_values.cumsum()
        / sorted_values.sum()
    )

    count = int(
        (cumulative < 0.80).sum() + 1
    )

    count = min(
        count,
        len(sorted_values)
    )

    percentage = (
        count / len(sorted_values) * 100
        if len(sorted_values) > 0
        else 0
    )

    return count, percentage


profit_80_count, profit_80_pct = (
    products_for_80_percent(
        product_summary["Gross_Profit"]
    )
)

revenue_80_count, revenue_80_pct = (
    products_for_80_percent(
        product_summary["Sales"]
    )
)


d1, d2 = st.columns(2)

with d1:

    st.metric(
        "Products generating 80% of Profit",
        f"{profit_80_count}"
    )

    st.caption(
        f"{profit_80_pct:.2f}% of the product portfolio"
    )


with d2:

    st.metric(
        "Products generating 80% of Revenue",
        f"{revenue_80_count}"
    )

    st.caption(
        f"{revenue_80_pct:.2f}% of the product portfolio"
    )


# ---------------------------------------------------------
# MARGIN VOLATILITY
# ---------------------------------------------------------

st.markdown("---")
st.header("📉 Margin Volatility Over Time")


monthly = (
    filtered_df
    .assign(
        YearMonth=filtered_df["Order Date"].dt.to_period("M")
    )
    .groupby("YearMonth", as_index=False)
    .agg(
        Average_Margin=("Margin %", "mean")
    )
)

monthly["YearMonth"] = (
    monthly["YearMonth"].astype(str)
)


fig_margin = px.line(
    monthly,
    x="YearMonth",
    y="Average_Margin",
    markers=True,
    title="Monthly Average Margin Trend",
    labels={
        "YearMonth": "Month",
        "Average_Margin": "Average Margin %"
    }
)

st.plotly_chart(
    fig_margin,
    use_container_width=True
)


# ---------------------------------------------------------
# FINAL RECOMMENDATIONS
# ---------------------------------------------------------

st.markdown("---")
st.header("💡 Business Recommendations")


recommendations = []

recommendations.append(
    f"Profit concentration: {profit_80_pct:.2f}% of products "
    f"generate 80% of total profit. Monitor these high-contribution "
    f"products closely for availability, cost and margin changes."
)

recommendations.append(
    f"Revenue concentration: {revenue_80_pct:.2f}% of products "
    f"generate 80% of total revenue. Monitor these products for "
    f"revenue dependency risk."
)

recommendations.append(
    f"Margin risk: {average_margin:.1f}% is the current average "
    f"margin. Products at or below {margin_threshold}% should be "
    f"reviewed for pricing or cost-reduction opportunities."
)

high_sales_low_margin = (
    product_summary["Classification"]
    .eq("High Sales / Low Margin")
    .sum()
)

recommendations.append(
    f"Product strategy: {high_sales_low_margin} products are "
    f"classified as High Sales / Low Margin and should be reviewed "
    f"for pricing, supplier costs or margin improvement."
)

recommendations.append(
    "Division performance should be evaluated using revenue, "
    "gross profit and average margin together rather than sales alone."
)

recommendations.append(
    "Products with low sales and low profit should be reviewed "
    "for their strategic importance, demand and contribution "
    "before portfolio decisions are made."
)


for i, recommendation in enumerate(
    recommendations,
    start=1
):

    st.write(
        f"**{i}.** {recommendation}"
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "Nassau Candy Distributor | Product Line Profitability "
    "& Margin Performance Analysis"
)