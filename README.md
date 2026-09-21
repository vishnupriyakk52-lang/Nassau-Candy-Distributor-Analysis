# Nassau Candy Distributor Analysis

## Product Line Profitability & Margin Performance Analysis using Excel and Streamlit

## 🚀 Live Dashboard

[Open the Live Streamlit Dashboard](https://feyft59y5cmpzvaq7fjxzh.streamlit.app)


### 📌 Project Overview

This project analyzes the profitability and margin performance of Nassau Candy Distributor using sales, cost, units, gross profit, product, division, and order-date data.

The project combines an interactive Excel dashboard with a Streamlit web application to support product-level profitability analysis, division performance analysis, cost and margin diagnostics, and profit concentration analysis.

### 🎯 Objectives

- Analyze product-level profitability and margins
- Identify high-profit and high-margin products
- Identify high-sales but low-margin products
- Identify low-sales and low-profit products
- Compare revenue, gross profit, and margins across divisions
- Analyze cost versus sales and cost versus margin relationships
- Identify products with margin risk
- Measure profit and revenue concentration
- Analyze margin volatility over time
- Provide data-driven business recommendations

### 📊 Excel Dashboard

The Excel analysis includes:

- Total Sales
- Gross Profit
- Total Units
- Average Margin
- Margin Volatility
- Division Revenue vs Gross Profit
- Average Margin by Division
- Product Profitability Analysis
- Profit per Unit
- Revenue Contribution
- Profit Contribution
- Cost vs Sales Analysis
- Cost vs Margin Diagnostic
- Margin Risk Analysis
- Gross Profit Pareto Analysis
- Revenue Pareto Analysis
- Margin Volatility Over Time
- Product Profitability Classification
- Interactive slicers for Division, Product Name, and Order Date

### 🌐 Streamlit Dashboard

The Streamlit application provides interactive analytics through:

1. **Product Profitability Overview**
   - Product-level margin leaderboard
   - Profit contribution analysis
   - Product profitability classification

2. **Division Performance Dashboard**
   - Revenue vs Gross Profit comparison
   - Average margin by division

3. **Cost vs Margin Diagnostics**
   - Cost vs Sales analysis
   - Cost vs Margin scatter analysis
   - Margin risk identification

4. **Profit Concentration Analysis**
   - Gross Profit Pareto analysis
   - Revenue Pareto analysis
   - 80% profit and revenue dependency indicators

5. **Margin Volatility Analysis**
   - Monthly margin trend
   - Margin volatility measurement

6. **Business Recommendations**
   - Data-driven recommendations based on profitability and margin analysis

### 🔎 Interactive Filters

The Streamlit dashboard supports:

- Date Range Selector
- Division Filter
- Margin Threshold Slider
- Product Search

### 🛠️ Technologies Used

- Microsoft Excel
- Python
- Pandas
- Plotly
- Streamlit
- OpenPyXL

### 📁 Project Files

- `app.py` – Streamlit dashboard application
- `requirements.txt` – Python dependencies
- `Nassau Candy Distributor_final.xlsx` – Excel analysis and interactive dashboard
- `Nassau Candy Distributor Research Paper.pdf` – EDA, findings, and recommendations
- `Nassau Candy Executive Summary.pdf` – Executive summary of the analysis

### ▶️ How to Run the Streamlit Application

Install the required packages:

```bash
py -3.13 -m pip install -r requirements.txt
Run the application:

py -3.13 -m streamlit run app.py

The application will open in a web browser.

Key Results

- Total Sales: $141,783.63
- Gross Profit: $93,442.80
- Total Units: 38,654
- Overall Average Margin: 67%
- Margin Volatility: approximately 0.32 percentage points
- 5 products (33.33% of the portfolio) account for at least 80% of total profit.
- 5 products (33.33% of the portfolio) account for at least 80% of total revenue.

Documentation

The project includes a Research Paper containing the exploratory data analysis, key findings, business insights, and recommendations, along with an Executive Summary for stakeholder communication.
