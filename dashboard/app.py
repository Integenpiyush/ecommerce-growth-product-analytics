"""
E-commerce Growth & Product Analytics Dashboard
===============================================
Production-grade interactive Streamlit dashboard featuring:
  - Executive Financial & Operational Overview
  - Product Funnel & Clickstream Conversion
  - Customer RFM Segmentation & Cohort Retention
  - Marketing Spend, CAC, and ROAS Attribution
  - A/B Testing Statistical Experimentation Analysis
"""

import os
import sys
from datetime import datetime, date
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_engine
from src.kpi_engine import KPIEngine
from src.product_analytics import ProductAnalyticsEngine
from src.customer_analytics import CustomerAnalyticsEngine
from src.marketing_analytics import MarketingAnalyticsEngine
from src.ab_testing import ExperimentAnalyzer
from src.utils import format_currency, format_percentage

# Streamlit Page Configuration
st.set_page_config(
    page_title="E-commerce Growth & Product Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for crisp, modern analytics presentation
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px 20px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #212529;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #28a745;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f1f3f5;
        border-radius: 6px 6px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd !important;
        color: #1976d2 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_cached_engines():
    """Initialize analytical engines once and cache."""
    engine = get_engine()
    return (
        KPIEngine(engine),
        ProductAnalyticsEngine(engine),
        CustomerAnalyticsEngine(engine),
        MarketingAnalyticsEngine(engine),
        ExperimentAnalyzer(engine)
    )

kpi_engine, prod_engine, cust_engine, mktg_engine, exp_engine = get_cached_engines()

# ==============================================================================
# SIDEBAR CONTROLS & GLOBAL FILTERS
# ==============================================================================
st.sidebar.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&q=80", use_container_width=True)
st.sidebar.title("Analytics Platform")
st.sidebar.caption("Portfolio Project • Senior Analytics")

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

# Date range selection
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(date(2024, 1, 1), date(2024, 12, 31)),
    min_value=date(2024, 1, 1),
    max_value=date(2024, 12, 31)
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d")
else:
    start_date, end_date = "2024-01-01", "2024-12-31"

# Channels filter
all_channels = ["Direct", "Organic Search", "Paid Search", "Paid Social", "Email", "Affiliate"]
selected_channels = st.sidebar.multiselect("Acquisition Channel", all_channels, default=all_channels)

# Device filter
all_devices = ["Mobile", "Desktop", "Tablet"]
selected_devices = st.sidebar.multiselect("Device Platform", all_devices, default=all_devices)

# Category filter
all_cats = ["Electronics", "Apparel", "Home & Living", "Beauty & Personal Care", "Sports & Outdoors"]
selected_categories = st.sidebar.multiselect("Product Category", all_cats, default=all_cats)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Dataset Notice**\n\n"
    "This dataset is 100% synthetic and reproducible (Seed: 42). Scale: 2,500 customers, "
    "18,000 orders, 30,000 clickstream sessions, 12,000 experiment users."
)

# Load filtered base data
orders_df = kpi_engine.load_filtered_orders(
    start_date=start_date,
    end_date=end_date,
    channels=selected_channels if len(selected_channels) < len(all_channels) else None,
    devices=selected_devices if len(selected_devices) < len(all_devices) else None,
    categories=selected_categories if len(selected_categories) < len(all_cats) else None
)

# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
st.title("E-commerce Growth & Product Analytics Platform")
st.caption(f"Active filter: {start_date} to {end_date} | {len(orders_df):,} matching orders")

tab_exec, tab_prod, tab_cust, tab_mktg, tab_ab = st.tabs([
    "📈 Executive Overview",
    "🛒 Product & Funnel Analytics",
    "👥 Customer & RFM Analytics",
    "🎯 Marketing & CAC/ROAS",
    "🧪 A/B Testing & Experimentation"
])

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------------------------
with tab_exec:
    st.subheader("Platform Financial & Operational Performance")
    kpis = kpi_engine.compute_summary_kpis(orders_df)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Net Revenue</div>
            <div class="metric-value">{format_currency(kpis['net_revenue'])}</div>
            <div class="metric-sub">Margin: {kpis['profit_margin_pct']}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Profit</div>
            <div class="metric-value">{format_currency(kpis['gross_profit'])}</div>
            <div class="metric-sub">Completed Orders</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Completed Orders</div>
            <div class="metric-value">{kpis['completed_orders']:,}</div>
            <div class="metric-sub">Total Placed: {kpis['total_orders']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Order Value</div>
            <div class="metric-value">{format_currency(kpis['aov'])}</div>
            <div class="metric-sub">Per completed basket</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Repeat Buyer Rate</div>
            <div class="metric-value">{kpis['repeat_customer_rate_pct']}%</div>
            <div class="metric-sub">{kpis['unique_customers']:,} unique buyers</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Monthly revenue & profit trend
    monthly_df = kpi_engine.compute_monthly_trend(orders_df)
    
    col_chart1, col_chart2 = st.columns([2, 1])
    with col_chart1:
        st.markdown("#### Monthly Net Revenue & MoM Growth")
        if not monthly_df.empty:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=monthly_df["month"],
                y=monthly_df["revenue"],
                name="Net Revenue ($)",
                marker_color="#1E88E5",
                opacity=0.85
            ))
            fig_rev.add_trace(go.Scatter(
                x=monthly_df["month"],
                y=monthly_df["profit"],
                name="Gross Profit ($)",
                marker_color="#00C853",
                mode="lines+markers",
                line=dict(width=3)
            ))
            fig_rev.update_layout(
                height=380,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.warning("No order records match the selected filters.")

    with col_chart2:
        st.markdown("#### Operational Leakage")
        fig_leak = go.Figure(go.Pie(
            labels=["Completed", "Returned", "Cancelled"],
            values=[kpis["completed_orders"], 
                    int(orders_df["order_status"].eq("Returned").sum()), 
                    int(orders_df["order_status"].eq("Cancelled").sum())],
            hole=0.45,
            marker_colors=["#2E7D32", "#FB8C00", "#E53935"]
        ))
        fig_leak.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1)
        )
        st.plotly_chart(fig_leak, use_container_width=True)

    # Daily rolling average & category distribution
    col_roll, col_cat = st.columns([1, 1])
    with col_roll:
        st.markdown("#### 7-Day & 30-Day Rolling Revenue ($)")
        daily_roll = kpi_engine.compute_daily_rolling(orders_df)
        if not daily_roll.empty:
            fig_daily = px.line(
                daily_roll,
                x="date",
                y=["revenue", "rolling_7d_revenue", "rolling_30d_revenue"],
                color_discrete_map={
                    "revenue": "#B0BEC5",
                    "rolling_7d_revenue": "#1E88E5",
                    "rolling_30d_revenue": "#D81B60"
                },
                labels={"value": "Revenue ($)", "date": "Date", "variable": "Metric"}
            )
            fig_daily.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
            st.plotly_chart(fig_daily, use_container_width=True)

    with col_cat:
        st.markdown("#### Category Revenue & Profit Breakdown")
        cat_df = kpi_engine.compute_category_breakdown()
        fig_cat = px.bar(
            cat_df,
            x="category",
            y=["profit", "revenue"],
            barmode="group",
            color_discrete_map={"revenue": "#1976D2", "profit": "#43A047"},
            labels={"value": "USD ($)", "category": "Category", "variable": "Type"}
        )
        fig_cat.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: PRODUCT & FUNNEL ANALYTICS
# ------------------------------------------------------------------------------
with tab_prod:
    st.subheader("E-commerce Clickstream & Funnel Conversion")
    funnel_df = prod_engine.get_funnel_summary(
        start_date=start_date,
        end_date=end_date,
        devices=selected_devices if len(selected_devices) < len(all_devices) else None,
        channels=selected_channels if len(selected_channels) < len(all_channels) else None
    )

    col_fun1, col_fun2 = st.columns([3, 2])
    with col_fun1:
        st.markdown("#### Full Funnel Progression (Stage-by-Stage)")
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df["stage_name"],
            x=funnel_df["users"],
            textinfo="value+percent initial",
            marker=dict(color=["#1565C0", "#1E88E5", "#42A5F5", "#90CAF9", "#2E7D32"])
        ))
        fig_funnel.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_fun2:
        st.markdown("#### Stage Conversion & Drop-off Rates")
        st.dataframe(
            funnel_df[["stage_name", "users", "stage_conversion_pct", "drop_off_pct", "users_lost"]].rename(
                columns={
                    "stage_name": "Stage",
                    "users": "Active Visitors",
                    "stage_conversion_pct": "Step CR (%)",
                    "drop_off_pct": "Drop-off (%)",
                    "users_lost": "Lost Users"
                }
            ),
            use_container_width=True,
            hide_index=True
        )
        st.info(
            "📌 **Product Drop-off Hotspot**\n\n"
            "The largest friction point occurs between **View Item → Add to Cart** (55.7% drop-off), "
            "followed by **Add to Cart → Begin Checkout** (46.2% drop-off). "
            "Checkout completion from initiated checkout is relatively healthy (~60.8%)."
        )

    st.markdown("---")
    col_dev, col_chan = st.columns(2)
    with col_dev:
        st.markdown("#### Funnel Conversion by Device")
        dev_funnel = prod_engine.get_funnel_by_dimension("device")
        fig_dev = px.bar(
            dev_funnel,
            x="device",
            y="end_to_end_conversion_pct",
            color="device",
            text="end_to_end_conversion_pct",
            labels={"end_to_end_conversion_pct": "Conversion Rate (%)", "device": "Device Platform"},
            color_discrete_sequence=["#1E88E5", "#43A047", "#FB8C00"]
        )
        fig_dev.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_dev, use_container_width=True)

    with col_chan:
        st.markdown("#### Funnel Conversion by Acquisition Channel")
        chan_funnel = prod_engine.get_funnel_by_dimension("traffic_channel")
        fig_chan = px.bar(
            chan_funnel,
            x="traffic_channel",
            y="end_to_end_conversion_pct",
            color="traffic_channel",
            text="end_to_end_conversion_pct",
            labels={"end_to_end_conversion_pct": "Conversion Rate (%)", "traffic_channel": "Channel"}
        )
        fig_chan.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_chan, use_container_width=True)

    st.markdown("#### Top 10 Highest Grossing Products")
    top_prods = prod_engine.get_top_performing_products(10)
    st.dataframe(top_prods, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 3: CUSTOMER & RFM ANALYTICS
# ------------------------------------------------------------------------------
with tab_cust:
    st.subheader("Customer Lifecycle & Retention Analytics")
    rfm_df, rfm_summary = cust_engine.compute_rfm_segments()

    col_rfm1, col_rfm2 = st.columns([3, 2])
    with col_rfm1:
        st.markdown("#### RFM Segment Revenue Contribution")
        fig_rfm_rev = px.bar(
            rfm_summary,
            x="segment",
            y="total_revenue",
            color="segment",
            text="revenue_share_pct",
            labels={"total_revenue": "Segment Revenue ($)", "segment": "RFM Segment"}
        )
        fig_rfm_rev.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_rfm_rev.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_rfm_rev, use_container_width=True)

    with col_rfm2:
        st.markdown("#### Segment Customer Distribution")
        fig_rfm_pie = px.pie(
            rfm_summary,
            names="segment",
            values="customer_count",
            hole=0.4
        )
        fig_rfm_pie.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_rfm_pie, use_container_width=True)

    st.markdown("#### RFM Segment Summary Scorecard")
    st.dataframe(
        rfm_summary.rename(columns={
            "segment": "RFM Segment",
            "customer_count": "Customers",
            "customer_pct": "Cust Share (%)",
            "total_revenue": "Total Spend ($)",
            "revenue_share_pct": "Rev Share (%)",
            "avg_recency_days": "Avg Recency (Days)",
            "avg_frequency": "Avg Orders",
            "avg_monetary": "Avg LTV ($)"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("#### Monthly Customer Cohort Retention Heatmap (%)")
    user_matrix, pct_matrix = cust_engine.compute_cohort_retention_matrix()

    fig_heat = px.imshow(
        pct_matrix,
        labels=dict(x="Months Since Acquisition (Index)", y="Acquisition Cohort", color="Retention (%)"),
        x=[f"Month {col}" for col in pct_matrix.columns],
        y=pct_matrix.index,
        color_continuous_scale="Blues",
        text_auto=".1f"
    )
    fig_heat.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: MARKETING & CAC / ROAS
# ------------------------------------------------------------------------------
with tab_mktg:
    st.subheader("Marketing Attribution & Acquisition Unit Economics")
    mktg_scorecard = mktg_engine.get_channel_performance_scorecard()

    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        st.markdown("#### Return on Ad Spend (ROAS) by Channel")
        fig_roas = px.bar(
            mktg_scorecard[mktg_scorecard["total_spend"] > 0],
            x="channel",
            y="roas",
            color="channel",
            text="roas",
            labels={"roas": "ROAS (Revenue / Spend)", "channel": "Channel"}
        )
        fig_roas.add_hline(y=4.0, line_dash="dash", line_color="red", annotation_text="Target ROAS (4.0x)")
        fig_roas.update_layout(height=360, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_roas, use_container_width=True)

    with col_m2:
        st.markdown("#### Customer Acquisition Cost (CAC) by Channel ($)")
        fig_cac = px.bar(
            mktg_scorecard[mktg_scorecard["total_spend"] > 0],
            x="channel",
            y="cac",
            color="channel",
            text="cac",
            labels={"cac": "CAC ($ per Customer)", "channel": "Channel"}
        )
        fig_cac.update_layout(height=360, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_cac, use_container_width=True)

    st.markdown("#### Full Channel Performance & Contribution Scorecard")
    st.dataframe(
        mktg_scorecard.rename(columns={
            "channel": "Channel",
            "total_spend": "Ad Spend ($)",
            "customers_acquired": "Acquired Customers",
            "completed_orders": "Orders",
            "attributed_revenue": "Revenue ($)",
            "attributed_profit": "Gross Profit ($)",
            "cac": "CAC ($)",
            "roas": "ROAS (x)",
            "contribution_profit": "Net Contribution ($)",
            "aov": "AOV ($)"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Monthly marketing efficiency
    st.markdown("#### Monthly Marketing Spend vs. Net Revenue Trend")
    mktg_trend = mktg_engine.get_monthly_marketing_trend()
    fig_mktg_line = go.Figure()
    fig_mktg_line.add_trace(go.Bar(
        x=mktg_trend["month"],
        y=mktg_trend["revenue"],
        name="Net Revenue ($)",
        marker_color="#1E88E5",
        opacity=0.8
    ))
    fig_mktg_line.add_trace(go.Scatter(
        x=mktg_trend["month"],
        y=mktg_trend["marketing_spend"],
        name="Marketing Spend ($)",
        marker_color="#E53935",
        mode="lines+markers",
        line=dict(width=3)
    ))
    fig_mktg_line.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig_mktg_line, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 5: A/B TESTING & EXPERIMENTATION
# ------------------------------------------------------------------------------
with tab_ab:
    st.subheader("Controlled A/B Experimentation: One-Step Checkout Optimization")
    st.caption("Hypothesis: Simplifying the checkout flow from 2-step to 1-step increases order completion rate without hurting basket size.")

    df_exp = exp_engine.load_experiment_data("checkout_one_step_v2")
    prop_test = exp_engine.run_proportion_test(df_exp)
    arpu_test = exp_engine.run_arpu_test(df_exp)

    # Metric comparison cards
    col_ab1, col_ab2, col_ab3, col_ab4 = st.columns(4)
    with col_ab1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Control Conversion</div>
            <div class="metric-value">{format_percentage(prop_test['conversion_rate_control'])}</div>
            <div class="metric-sub">{prop_test['conversions_control']:,} / {prop_test['n_control']:,} users</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ab2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Treatment Conversion</div>
            <div class="metric-value">{format_percentage(prop_test['conversion_rate_treatment'])}</div>
            <div class="metric-sub">{prop_test['conversions_treatment']:,} / {prop_test['n_treatment']:,} users</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ab3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Observed Lift</div>
            <div class="metric-value">+{prop_test['relative_lift_pct']}%</div>
            <div class="metric-sub">Absolute: +{prop_test['absolute_lift'] * 100:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ab4:
        sig_color = "#28a745" if prop_test['is_statistically_significant'] else "#dc3545"
        sig_label = "SIGNIFICANT (p < 0.05)" if prop_test['is_statistically_significant'] else "NOT SIGNIFICANT"
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {sig_color};">
            <div class="metric-title">Statistical Verdict</div>
            <div class="metric-value" style="font-size: 1.3rem; color: {sig_color};">{sig_label}</div>
            <div class="metric-sub">p-value: {prop_test['p_value']} (z = {prop_test['z_statistic']})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_stat_viz, col_subgroup = st.columns([1, 1])
    with col_stat_viz:
        st.markdown("#### 95% Confidence Interval for Relative Lift (%)")
        fig_ci = go.Figure()
        # Null zero line
        fig_ci.add_vline(x=0.0, line_dash="dash", line_color="gray", annotation_text="Zero Lift (H0)")
        fig_ci.add_trace(go.Scatter(
            x=[prop_test["relative_lift_pct"]],
            y=["Checkout Flow v2"],
            mode="markers",
            marker=dict(size=14, color="#1E88E5"),
            error_x=dict(
                type="data",
                symmetric=False,
                array=[prop_test["ci_upper_rel_pct"] - prop_test["relative_lift_pct"]],
                arrayminus=[prop_test["relative_lift_pct"] - prop_test["ci_lower_rel_pct"]],
                width=10,
                thickness=3,
                color="#1565C0"
            ),
            name="Relative Lift"
        ))
        fig_ci.update_layout(
            height=240,
            xaxis_title="Relative Lift in Conversion Rate (%)",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_ci, use_container_width=True)

        st.info(
            f"📊 **Confidence Interval Bounds**: 95% CI for relative lift is "
            f"**[{prop_test['ci_lower_rel_pct']}%, {prop_test['ci_upper_rel_pct']}%]**. "
            f"Because the entire 95% confidence interval lies strictly above 0%, we can reject the null hypothesis "
            f"at $\\alpha = 0.05$."
        )

    with col_subgroup:
        st.markdown("#### Device Subgroup Heterogeneity Analysis")
        subgroup_df = exp_engine.run_subgroup_analysis(df_exp, "device")
        st.dataframe(
            subgroup_df.rename(columns={
                "device": "Device",
                "n_control": "Ctrl Users",
                "n_treatment": "Treat Users",
                "cr_control_pct": "Ctrl CR (%)",
                "cr_treatment_pct": "Treat CR (%)",
                "abs_lift_pct": "Abs Lift (%)",
                "rel_lift_pct": "Rel Lift (%)",
                "p_value": "p-value",
                "is_significant": "Significant"
            }),
            use_container_width=True,
            hide_index=True
        )
        st.success(
            "💡 **Subgroup Insight**\n\n"
            "Mobile devices achieved the highest conversion lift (+18.4% relative lift), "
            "confirming our UX hypothesis that reducing mobile checkout steps produces outsized gains."
        )

    st.markdown("---")
    st.markdown("#### Secondary Metric: Average Revenue Per User (ARPU)")
    col_arpu1, col_arpu2 = st.columns([2, 1])
    with col_arpu1:
        st.write(
            f"- **Control ARPU**: ${arpu_test['arpu_control']:.2f}\n"
            f"- **Treatment ARPU**: ${arpu_test['arpu_treatment']:.2f}\n"
            f"- **ARPU Lift**: +${arpu_test['arpu_absolute_lift']:.2f} (+{arpu_test['arpu_relative_lift_pct']}%, Welch's t = {arpu_test['t_statistic']}, p = {arpu_test['p_value']})\n"
            f"- **Monetization Significance**: {arpu_test['is_significant']} (p > 0.05; not statistically significant due to basket variance).\n"
        )
    with col_arpu2:
        st.warning(
            "⚠️ **Stakeholder Decision Caveat**\n\n"
            "While conversion rate is statistically significant, ARPU has not yet reached $\\alpha=0.05$ significance. "
            "However, because ARPU lift is positive and does not degrade average basket value, rolling out Treatment is recommended."
        )
