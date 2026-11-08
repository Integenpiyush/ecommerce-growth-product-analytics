# Strategic Business Case Studies & Executive Decision Framework

This report presents six empirical, data-driven business case studies conducted on the e-commerce platform's analytical warehouse. Every metric, trend, and recommendation is grounded in real computations from the platform's data engine.

---

## Case Study 1: Mid-Year Revenue Decline & Leakage Investigation

### 1. Business Problem
In Q2 (specifically April–May), executive leadership observed a 6.2% deceleration in net revenue growth compared to Q1. The C-Suite raised immediate questions: *Is traffic dropping, is basket size shrinking, or is revenue leaking through cancellations and product returns?*

### 2. Metric Definitions
- **Gross Revenue**: Sum of product list prices $\times$ units ordered before discounts.
- **Net Revenue**: $\text{Gross Revenue} - \text{Discount Amount}$ for Completed orders.
- **Leakage Rate**: $(\text{Cancelled Orders} + \text{Returned Orders}) / \text{Total Orders Placed}$.
- **Net Refund Impact**: Cash refunded due to cancellations and post-delivery returns.

### 3. Analytical Approach
1. Decomposed Net Revenue into its core formula components: $\text{Revenue} = \text{Sessions} \times \text{Conversion Rate} \times \text{AOV} \times (1 - \text{Leakage Rate})$.
2. Analyzed monthly trends across gross revenue, completed revenue, cancellation volume, and return volume.
3. Evaluated delivery delays and return reason codes.

### 4. Empirical Findings
- Total platform revenue generated in 2024 reached **$4,833,791.63** across 14,978 completed orders.
- However, total operational leakage reached **16.79%** of all orders placed:
  - **Cancelled Orders**: 1,213 orders (6.74% cancellation rate), totaling $389,450 in lost volume.
  - **Returned Orders**: 1,809 orders (10.05% return rate), generating **$610,350.95** in refunded merchandise value.
  - Total refund and leakage cash drag totaled **$999,800.95**.
- In Apparel and Footwear, return rates spiked to **14.8%**, with **"Wrong Size / Fit"** and **"Defective / Damaged"** accounting for 58% of all recorded return reasons.
- Cancelled orders were heavily concentrated in orders with estimated delivery times exceeding 5 business days.

### 5. Business Interpretation
The revenue deceleration was not a demand-generation failure (traffic was healthy and AOV remained constant at ~$322), but rather an **operational fulfillment and sizing friction failure**. Customers experienced post-purchase regret or delayed deliveries, resulting in pre-dispatch cancellations and post-delivery returns.

### 6. Actionable Recommendations
1. **Implement Fit Guidance & Virtual Sizing AI**: Embed dynamic sizing recommendations on Apparel PDPs to reduce sizing mismatches.
2. **Optimize Expedited Fulfillment**: Introduce regional warehouse fulfillment routing to cut delivery transit times below 3 days.
3. **Automated Order Tracking SMS**: Provide live shipping milestone notifications to quell buyer anxiety and stem pre-delivery cancellations.

### 7. Expected Impact
- Cutting the return rate from 10.05% to 7.5% preserves **$152,000+** in net retained merchandise value annually.
- Reducing cancellations by 25% recovers **$97,000+** in gross sales.

### 8. Limitations
Returns data tracks customer-reported reasons, which may suffer from survey bias (e.g. selecting "Damaged" to qualify for free return postage).

---

## Case Study 2: Mobile Product Funnel Drop-Off & Checkout Friction

### 1. Business Problem
While Mobile traffic accounts for **65.8%** of all platform browsing sessions (19,742 of 30,000 sessions), Mobile generates only **53.2%** of completed transactions. Product Management sought to isolate exact friction stages where mobile users abandon baskets.

### 2. Metric Definitions
- **Stage Drop-Off Rate**: $(Users_{Stage\_N} - Users_{Stage\_N+1}) / Users_{Stage\_N}$.
- **Step-to-Step Conversion Rate**: $Users_{Stage\_N+1} / Users_{Stage\_N}$.
- **End-to-End Conversion Rate**: $\text{Purchases} / \text{Total Sessions}$.

### 3. Analytical Approach
Segmented clickstream events across device form factors (Desktop, Mobile, Tablet) through the 5 funnel stages:
$\text{Session} \to \text{View Item} \to \text{Add to Cart} \to \text{Begin Checkout} \to \text{Purchase}$.

### 4. Empirical Findings
| Funnel Milestone | Desktop | Mobile | Tablet | Gap (Desktop vs Mobile) |
|---|---|---|---|---|
| **Sessions** | 8,162 | 19,742 | 2,096 | Mobile = 65.8% share |
| **View Item Rate** | 80.2% | 68.1% | 66.5% | -12.1% on Mobile |
| **Cart Rate (from Views)** | 48.6% | 41.8% | 40.2% | -6.8% on Mobile |
| **Checkout Rate (from Carts)** | 59.4% | 50.8% | 48.5% | -8.6% on Mobile |
| **Purchase Rate (from Checkouts)** | 66.8% | 57.4% | 55.2% | -9.4% on Mobile |
| **End-to-End Conversion** | **15.42%** | **8.29%** | **7.06%** | **Desktop converts 1.86x higher** |

### 5. Business Interpretation
Mobile conversion suffers compounding attrition across every stage. The primary drop-off occurs at **View Item $\to$ Add to Cart** (58.2% drop-off on mobile), where slow product image loading and buried "Add to Cart" buttons below the fold on mobile viewports impede mobile shoppers. The secondary drop-off at **Checkout** reflects burdensome multi-step form fields on touchscreens.

### 6. Actionable Recommendations
1. **Sticky "Buy Now / Add to Cart" Footer**: Implement a persistent mobile bottom navigation bar with one-tap cart additions.
2. **Mobile Autofill & Express Wallets**: Integrate Apple Pay, Google Pay, and UPI 1-click checkout to remove 12 manual text input fields.
3. **Core Web Vitals PDP Optimization**: Compress product hero imagery via WebP/AVIF formats to reduce Largest Contentful Paint (LCP) under 1.8s.

### 7. Expected Impact
Elevating Mobile end-to-end conversion from 8.29% to 10.5% on 19,742 sessions would unlock **+436 additional monthly purchases**, delivering approximately **$140,000+** in incremental monthly revenue.

### 8. Limitations
Does not capture cross-device journeys where users discover items on Mobile during commutes and finalize purchases later on Desktop.

---

## Case Study 3: Customer Retention Attrition & Cohort Decay

### 1. Business Problem
Acquiring new customers via paid channels is becoming increasingly expensive due to privacy tracking changes. Growth leadership needs to know: *Are acquired customers repeat-purchasing, and does customer retention decay after month 1?*

### 2. Metric Definitions
- **Month-N Retention Rate**: $\text{Active Buyers in Month N} / \text{Initial Cohort Base Size} \times 100\%$.
- **Repeat Purchase Rate**: $\text{Customers with } \ge 2 \text{ orders} / \text{All Purchasing Customers}$.
- **Customer Lifetime Value (LTV)**: Cumulative net revenue generated per acquired customer over time.

### 3. Analytical Approach
1. Built a dynamic monthly cohort retention matrix tracking 12 acquisition cohorts over 12 operational months.
2. Computed cumulative LTV curves and segmented customer recency/frequency metrics.

### 4. Empirical Findings
- Platform repeat customer rate is **76.55%** (1,604 out of 2,095 ordering customers made 2+ purchases).
- Cohort Retention Dynamics:
  - **Month 0 (Acquisition)**: 100% baseline.
  - **Month 1**: Drops steeply to **48.2%** for the Jan cohort (45.2% for Feb, 41.8% for Mar).
  - **Month 2–6**: Stabilizes in the **40%–50%** band.
- Cumulative 6-Month LTV:
  - Month 0 LTV: ~$320
  - Month 3 Cumulative LTV: ~$1,120
  - Month 6 Cumulative LTV: ~$1,890
- High revenue concentration: The **Champions** segment (404 customers, 19.3% of users) accounts for **67.75%** of all net revenue ($3.27M).

### 5. Business Interpretation
Customer retention exhibits the classic "cliff and plateau" curve. While a 50%+ drop from Month 0 to Month 1 is typical in retail e-commerce, the high retention stability (40%+) thereafter and strong repeat purchase rate (76.5%) demonstrate exceptional product-market fit among retained buyers. However, revenue is disproportionately dependent on top-tier Champions, creating key-person risk if top accounts churn.

### 6. Actionable Recommendations
1. **30-Day Post-Purchase Trigger Program**: Implement an automated CRM email workflow triggered at Day 14 and Day 21 post-delivery offering replenishment reminders and complementary product discounts.
2. **VIP Tier Loyalty Program**: Introduce an invitation-only rewards tier for Champions with early product access and dedicated customer support.
3. **Win-back Campaign for "At Risk" Segment**: Deploy targeted SMS/push re-engagement for high-value customers inactive for 60+ days.

### 7. Expected Impact
A 5% improvement in Month 1 retention across 250 monthly new customers retains 12 additional buyers per cohort, adding **$22,000+** in cumulative 90-day LTV per cohort.

### 8. Limitations
Retention is based on repeat orders within a 1-year observation window; does not account for multi-year replenishment cycles (e.g. durable appliances).

---

## Case Study 4: Marketing Budget Capital Allocation (ROAS vs. CAC)

### 1. Business Problem
The CMO manages an annual performance marketing budget of ~$470,000 distributed across Paid Search, Paid Social, Affiliate, and Organic channels. The Board demands a reallocation plan to maximize net contribution profit.

### 2. Metric Definitions
- **Customer Acquisition Cost (CAC)**: $\text{Total Channel Ad Spend} / \text{First-Time Acquired Customers}$.
- **Return on Ad Spend (ROAS)**: $\text{Attributed Net Revenue} / \text{Channel Ad Spend}$.
- **Net Contribution Profit**: $\text{Attributed Gross Profit} - \text{Total Ad Spend}$.

### 3. Analytical Approach
Aggregated daily ad spend, clicks, impressions, and attributed orders across each channel to build an efficiency scorecard.

### 4. Empirical Findings
| Acquisition Channel | Total Ad Spend | Acquired Customers | Total Revenue | CAC ($) | ROAS | Net Contribution Profit ($) |
|---|---|---|---|---|---|---|
| **Paid Search (Google Ads)** | $220,795.63 | 536 | $1,552,084.77 | $411.93 | **7.03x** | **+$430,597.95** |
| **Organic Search (SEO)** | $11,802.15 | 536 | $1,054,952.54 | $22.02 | **89.39x** | **+$436,379.97** |
| **Paid Social (Meta Ads)** | $166,276.47 | 425 | $805,178.68 | $391.24 | **4.84x** | **+$170,133.19** |
| **Email Marketing** | $18,089.76 | 213 | $524,677.29 | $84.93 | **29.00x** | **+$204,505.36** |
| **Affiliate Marketing** | $55,328.80 | 114 | $202,044.20 | $485.34 | **3.65x** | **+$29,680.19** |
| **Direct / Referral** | $0.00 | 271 | $694,854.15 | $0.00 | N/A | **+$290,985.24** |

### 5. Business Interpretation
- **Paid Search** is our primary scaling engine, delivering $1.55M in sales at an exceptional 7.03x ROAS and +$430.6K in net profit.
- **Affiliate Marketing** is sub-scale and underperforming, with an inflated CAC of $485.34 and ROAS of 3.65x, barely covering margin requirements.
- **Email & Organic Search** deliver outstanding efficiency (ROAS 29.0x and 89.4x), proving that owned channels generate superior margin.

### 6. Actionable Recommendations
1. **Reallocate $30,000 from Affiliate to Paid Search**: Boost budget for high-intent generic search terms where marginal ROAS exceeds 5.5x.
2. **Expand Email Acquisition Workflows**: Reinvest $10,000 into lead-magnet acquisition popups and newsletter co-marketing to grow owned email lists.
3. **Renegotiate Affiliate Commissions**: Shift affiliate payout model from top-line commission to a fixed bounty tied strictly to new-to-brand customers.

### 7. Expected Impact
Shifting $30K from 3.65x ROAS (Affiliate) to 7.0x ROAS (Paid Search) generates an estimated **+$100,500** in incremental gross merchandise value.

### 8. Limitations
Attribution utilizes first-touch channel attribution; last-touch or data-driven multi-touch attribution (MTA) may credit Paid Social for upper-funnel discovery that concludes in Paid Search.

---

## Case Study 5: Category Merchandise Unit Economics & Margin Optimization

### 1. Business Problem
Electronics generates high top-line volume, but warehouse and executive teams expressed concern that low product margins may leave little bottom-line profit after payment processing, shipping, and discount costs.

### 2. Metric Definitions
- **Gross Margin (%)**: $(\text{Item Revenue} - \text{Item COGS}) / \text{Item Revenue} \times 100\%$.
- **Revenue Contribution (%)**: $\text{Category Revenue} / \text{Total Catalog Revenue} \times 100\%$.
- **Profit Contribution (%)**: $\text{Category Profit} / \text{Total Catalog Profit} \times 100\%$.

### 3. Empirical Findings
| Category | Total Orders | Units Sold | Total Revenue | Gross Profit | Gross Margin (%) | Margin Benchmark |
|---|---|---|---|---|---|---|
| **Electronics** | 3,923 | 5,880 | $1,556,983.33 | $491,157.94 | **31.55%** | 31.0% |
| **Home & Living** | 3,939 | 5,984 | $1,114,841.52 | $517,049.93 | **46.38%** | 46.0% |
| **Sports & Outdoors**| 3,892 | 5,910 | $1,008,187.56 | $420,833.40 | **41.74%** | 41.5% |
| **Apparel** | 3,928 | 5,953 | $880,958.82 | $512,189.62 | **58.14%** | 57.5% |
| **Beauty & Personal**| 3,892 | 5,939 | $508,580.67 | $341,943.90 | **67.23%** | 67.5% |

### 4. Business Interpretation
- **Electronics** accounts for 30.7% of total revenue ($1.56M), but only 21.5% of total gross profit due to compressed margins (31.55%).
- In contrast, **Home & Living** ($517K profit) and **Apparel** ($512K profit) generate more absolute profit dollars than Electronics, despite having substantially lower revenue footprints.
- **Beauty & Personal Care** delivers stellar 67.23% margins, but is constrained by low unit average selling prices ($85 vs $265 in Electronics).

### 5. Actionable Recommendations
1. **Bundle High-Margin Beauty & Apparel Accessories with Electronics**: Program cart cross-sells on Electronics PDPs (e.g. protective cases, cleaning kits) to blend basket margins up by 4–6%.
2. **Tiered Free Shipping Threshold**: Increase free shipping threshold from $75 to $99 for Electronics orders to offset heavy shipping freight expenses.
3. **Elevate Apparel & Home Merchandising**: Feature Home & Living in hero homepage real estate to steer volume toward high-margin merchandise.

### 6. Expected Impact
A 200 bps increase in overall gross margin percentage via category bundle cross-selling yields **+$96,600** in direct gross profit on $4.83M revenue.

### 7. Limitations
Assumes constant supplier cost prices; does not model bulk purchase order supplier rebate tiers.

---

## Case Study 6: Checkout Optimization A/B Experiment Rollout Decision

### 1. Business Problem
Product and Growth teams initiated a 30-day randomized controlled trial (`checkout_one_step_v2`) testing a streamlined one-page checkout flow against the existing multi-step flow. The product lead requested an empirical statistical evaluation: *Should we roll this out to 100% of traffic, iterate, or abort?*

### 2. Hypotheses & Statistical Framework
- **Primary Metric**: Binary Conversion Rate (Completed Checkout / Assigned Visitors).
- **Secondary Guardrail Metric**: Average Revenue Per User (ARPU).
- **Null Hypothesis ($H_0$)**: $p_{\text{treatment}} - p_{\text{control}} = 0$
- **Alternative Hypothesis ($H_1$)**: $p_{\text{treatment}} - p_{\text{control}} > 0$
- **Significance Level ($\alpha$)**: $0.05$ (Two-sided test)
- **Target Power ($1 - \beta$)**: $0.80$

### 3. Empirical Experimental Results
- **Sample Size**: 12,000 unique assigned visitors (Control: $N=6,043$, Treatment: $N=5,957$).
- **Control Performance**: 910 conversions, **15.06%** Conversion Rate.
- **Treatment Performance**: 976 conversions, **16.38%** Conversion Rate.
- **Observed Lift**:
  - Absolute Lift: **+1.32%** percentage points ($+0.0132$)
  - Relative Lift: **+8.83%**
- **Statistical Significance**:
  - Pooled Standard Error: $SE = 0.00665$
  - Test Statistic: $Z = 2.0003$
  - **p-value**: **$0.04547$** ($p < 0.05$)
  - **95% Confidence Interval**: $[+0.03\%, +2.63\%]$ (relative: $[+0.21\%, +17.48\%]$).
- **Guardrail Metric (ARPU)**:
  - Control ARPU: $12.66, Treatment ARPU: $13.70 (Lift: +$1.04, Welch's $t = 1.602$, $p = 0.109$).

### 4. Heterogeneity & Subgroup Breakdown
Subgroup analysis revealed that the lift was overwhelmingly driven by **Mobile devices**:
- **Mobile Relative Lift**: **+18.4%** ($p = 0.012$, statistically significant).
- **Desktop Relative Lift**: **+5.6%** ($p = 0.38$, not statistically significant).

### 5. Final Rollout Decision & Recommendation
**DECISION: FULL ROLLOUT TO 100% OF USERS (RECOMMENDED)**

#### Justification:
1. **Statistically Significant**: The primary conversion rate metric achieved statistical significance ($p = 0.0455 < 0.05$) with a confidence interval strictly excluding zero.
2. **Guardrail Metric Preserved**: ARPU did not degrade; in fact, it trended positively (+$1.04 per visitor).
3. **Clear Mechanism of Action**: The lift is concentrated where intended—on mobile devices where multi-step forms caused the greatest drop-off.

### 6. Expected Annual Impact
Applying the +1.32% absolute conversion rate lift across 30,000 annual sessions yields **+396 additional completed orders**, generating approximately **+$128,000** in incremental top-line annual revenue.

### 7. Limitations & Post-Launch Monitoring
- **Novelty Effect**: Repeat visitors might convert faster initially due to UI freshness; monitor 60-day post-launch conversion stability.
- **Return Rate Watch**: Confirm that 1-click ease does not elevate impulse buying and subsequent return rates over the subsequent quarter.
