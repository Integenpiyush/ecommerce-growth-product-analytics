# 03. Analytics Fundamentals & Metric Mathematics

This guide teaches the theoretical foundations and exact mathematical formulas behind every metric utilized in this portfolio project.

---

## 1. Financial & Operational Metrics

### Gross Revenue vs. Net Revenue vs. Gross Profit

#### Conceptual Difference
- **Gross Revenue (Top Line / GMV)**: The total undiscounted list price of all items added to orders. It indicates top-of-funnel customer transaction appetite.
- **Net Revenue (Recognized Invoiced Sales)**: The actual cash realized from completed orders after subtracting promotional coupons and discounts:
  $$\text{Net Revenue} = \text{Gross Revenue} - \text{Discounts}$$
- **Gross Profit**: The money remaining after subtracting direct product manufacturing/acquisition costs (Cost of Goods Sold / COGS):
  $$\text{Gross Profit} = \text{Net Revenue} - \text{COGS}$$
- **Gross Margin (%)**:
  $$\text{Gross Margin} = \left(\frac{\text{Gross Profit}}{\text{Net Revenue}}\right) \times 100$$

#### Project Example
- Gross Revenue: **$5,069,551.90**
- Promotional Discounts: **$235,760.27**
- Net Revenue: **$4,833,791.63**
- Total COGS: **$2,799,216.92**
- Gross Profit: **$2,034,574.71**
- Platform Gross Margin: **42.09%**

---

### Average Order Value (AOV)

#### Formula
$$\text{AOV} = \frac{\text{Net Revenue}}{\text{Total Completed Orders}}$$

#### Why it matters
AOV measures basket size efficiency. Increasing AOV by 10% through upselling and cross-selling increases top-line revenue without spending an additional dollar on customer acquisition.

#### Project Example
$$\text{AOV} = \frac{\$4,833,791.63}{14,978 \text{ completed orders}} = \$322.73$$

---

### Return Rate & Cancellation Rate (Operational Leakage)

#### Formulas
$$\text{Cancellation Rate} = \left(\frac{\text{Cancelled Orders}}{\text{Total Orders Placed}}\right) \times 100$$
$$\text{Return Rate} = \left(\frac{\text{Returned Orders}}{\text{Total Orders Placed}}\right) \times 100$$

#### Project Example
- Total Orders Placed: 18,000
- Cancelled Orders: 1,213 $\to$ **6.74%**
- Returned Orders: 1,809 $\to$ **10.05%**
- Total Financial Refund Drag: **$999,800.95**

---

## 2. Product & Funnel Analytics

### Clickstream Conversion Rate (Macro & Micro)

#### Macro (End-to-End) Conversion Rate
$$\text{End-to-End Conversion Rate} = \left(\frac{\text{Completed Purchases}}{\text{Total Website/App Sessions}}\right) \times 100$$

#### Micro (Step-to-Step) Conversion Rate
$$\text{Stage Conversion Rate}_{t \to t+1} = \left(\frac{\text{Users Reaching Stage}_{t+1}}{\text{Users at Stage}_t}\right) \times 100$$

#### Step Drop-Off Rate
$$\text{Drop-Off Rate}_{t \to t+1} = 100\% - \text{Stage Conversion Rate}_{t \to t+1}$$

#### Project Example
Across 30,000 sessions:
1. **Session Start**: 30,000
2. **View Item**: 21,399 $\to$ Step CR: **71.33%**, Drop-off: **28.67%**
3. **Add to Cart**: 9,479 $\to$ Step CR: **44.30%**, Drop-off: **55.70%** (Primary friction point)
4. **Begin Checkout**: 5,097 $\to$ Step CR: **53.77%**, Drop-off: **46.23%**
5. **Purchase Completed**: 3,097 $\to$ Step CR: **60.76%**, Drop-off: **39.24%**
- Overall End-to-End Conversion: **10.32%**

---

## 3. Customer Retention & Lifecycle Analytics

### Repeat Purchase Rate

#### Formula
$$\text{Repeat Purchase Rate} = \left(\frac{\text{Customers with } \ge 2 \text{ Completed Orders}}{\text{Total Ordering Customers}}\right) \times 100$$

#### Project Example
- Total Ordering Customers: 2,095
- Customers with 2+ orders: 1,604
- Repeat Purchase Rate: **76.55%**

---

### Cohort Retention vs. Churn Rate

#### Definition
- **Cohort**: A group of users who share a common characteristic and time frame—in our project, the month in which they completed their first order.
- **Retention Rate ($R_n$)**: Percentage of the original cohort members who return to make an order in Month $n$:
  $$R_n = \left(\frac{\text{Active Customers in Month } n}{\text{Cohort Size in Month } 0}\right) \times 100$$
- **Customer Churn Rate ($C_n$)**: Percentage of customers lost by Month $n$:
  $$C_n = 100\% - R_n$$

#### Project Example
For the January 2024 cohort (220 customers):
- Month 0: 100.0% (220 users)
- Month 1: 48.2% (106 users) $\to$ Month 1 churn was 51.8%
- Month 2: 48.2% (106 users)
- Month 3: 46.4% (102 users)
- Month 6: 42.7% (94 users)

---

### Customer Lifetime Value (LTV)

#### Empirical Cohort LTV Formula
$$\text{Cumulative LTV}_n = \frac{\sum_{t=0}^n \text{Net Revenue}_t}{\text{Cohort Base Size}}$$

#### Project Example
For January cohort:
- Month 0 LTV: $320.10
- Month 3 Cumulative LTV: $1,140.50
- Month 6 Cumulative LTV: $1,885.20

---

### RFM Segmentation (Recency, Frequency, Monetary)

#### How it works
1. **Recency ($R$)**: Days since customer's last order. (Lower is better $\to$ higher score).
2. **Frequency ($F$)**: Total number of orders placed. (Higher is better $\to$ higher score).
3. **Monetary ($M$)**: Total spend in dollars. (Higher is better $\to$ higher score).
4. Each customer receives a score from 1 to 5 using quintiles (`NTILE(5)` in SQL or `pd.qcut` in Python).
5. Customer segments are assigned based on score patterns:
   - **Champions** ($R \ge 4, F \ge 4, M \ge 4$): High spenders, bought recently, frequent repeaters.
   - **Loyal Customers** ($R \ge 3, F \ge 3, M \ge 3$): Consistent recurring buyers.
   - **At Risk** ($R \le 2, F \ge 4, M \ge 4$): Formerly great buyers who haven't returned recently.
   - **Hibernating** ($R \le 2, F \le 2$): Low recency, low frequency.
   - **Lost** ($R=1, F=1$): Churned one-time purchasers.

---

## 4. Marketing Unit Economics

### Customer Acquisition Cost (CAC)

#### Paid CAC vs. Blended CAC
- **Paid CAC**: Direct ad dollars spent divided strictly by customers acquired through that ad channel:
  $$\text{Paid CAC}_{channel} = \frac{\text{Channel Ad Spend}}{\text{Customers Acquired by Channel}}$$
- **Blended CAC**: Total marketing budget divided across ALL new customers acquired from all channels (including organic and direct):
  $$\text{Blended CAC} = \frac{\text{Total Marketing Spend}}{\text{Total New Customers Acquired}}$$

#### Project Example
- Paid Search Spend: $220,795.63 $\to$ 536 customers acquired $\to$ **Paid Search CAC = $411.93**
- Paid Social Spend: $166,276.47 $\to$ 425 customers acquired $\to$ **Paid Social CAC = $391.24**
- Total Marketing Spend: $472,292.81 $\to$ 2,095 total customers $\to$ **Blended CAC = $225.44**

---

### Return on Ad Spend (ROAS)

#### Formula
$$\text{ROAS} = \frac{\text{Attributed Revenue Generated}}{\text{Total Ad Spend}}$$

#### Distinction between ROAS and ROI
- **ROAS**: Gross revenue return per dollar of advertising. A ROAS of $4.0\text{x}$ means every \$1 spent on ads generates \$4 in top-line sales.
- **ROI**: Considers product costs (COGS) and operational overhead:
  $$\text{ROI} = \frac{\text{Gross Profit} - \text{Ad Spend}}{\text{Ad Spend}} \times 100\%$$

#### Project Example
- Paid Search: Revenue \$1,552,084.77 / Spend \$220,795.63 = **7.03x ROAS**
- Affiliate: Revenue \$202,044.20 / Spend \$55,328.80 = **3.65x ROAS**

---

## 5. Experimentation & Inferential Statistics

### Two-Sample Proportion Z-Test

#### Hypotheses
- $H_0: p_{\text{treatment}} - p_{\text{control}} = 0$ (Null Hypothesis: No difference in conversion rate)
- $H_1: p_{\text{treatment}} - p_{\text{control}} \ne 0$ (Alternative Hypothesis: Significant difference)

#### Formula
$$Z = \frac{\hat{p}_{\text{treatment}} - \hat{p}_{\text{control}}}{\sqrt{\hat{p}_{pool}(1 - \hat{p}_{pool})\left(\frac{1}{n_{\text{control}}} + \frac{1}{n_{\text{treatment}}}\right)}}$$
where $\hat{p}_{pool} = \frac{x_{\text{control}} + x_{\text{treatment}}}{n_{\text{control}} + n_{\text{treatment}}}$.

---

### P-Value & Statistical Significance ($\alpha = 0.05$)

#### Definition
The **p-value** is the probability of observing a difference at least as extreme as the one calculated in our sample, assuming that the null hypothesis is completely true.
- If $p < 0.05$, the probability of the result occurring by chance alone is less than 5%. We reject the null hypothesis and declare **statistical significance**.
- In our project experiment:
  $$Z = 2.0003, \quad p = 0.04547 < 0.05$$
  Because $0.04547 < 0.05$, the +1.32% absolute lift is statistically significant at the 95% confidence level.

---

### Confidence Intervals (95% CI)

#### Formula
$$\text{CI}_{95\%} = \Delta \pm 1.96 \times SE_{\text{unpooled}}$$
- If the entire 95% confidence interval lies strictly above 0 (e.g. $[+0.03\%, +2.63\%]$), zero is ruled out with 95% certainty.

---

### Statistical vs. Practical Significance

- **Statistical Significance**: Proves that the observed lift is real and not random noise.
- **Practical (Business) Significance**: Assesses whether the magnitude of the lift is large enough to justify engineering rollout, server maintenance, and operational overhead.
- In our project, an absolute lift of +1.32% translates to **+\$128,000+** in annual top-line revenue—comfortably exceeding engineering implementation hurdles.
