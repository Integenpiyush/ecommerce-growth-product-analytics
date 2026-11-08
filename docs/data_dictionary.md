# Data Dictionary

This document details every table, field, datatype, description, and sample value within the E-commerce Growth & Product Analytics Platform.

---

## 1. `dim_customers`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `customer_id` | VARCHAR(32) | PRIMARY KEY | Unique customer identifier | `CUST-0001` |
| `signup_date` | DATE | NOT NULL | Date customer registered an account | `2024-02-14` |
| `acquisition_channel` | VARCHAR(50) | NOT NULL | Marketing channel credited with user acquisition | `Organic Search` |
| `device_preference` | VARCHAR(30) | NOT NULL | Customer's primary access device (`Mobile`, `Desktop`, `Tablet`) | `Mobile` |
| `city_tier` | VARCHAR(20) | NOT NULL | Demographic city tier (`Tier 1`, `Tier 2`, `Tier 3`) | `Tier 1` |
| `gender` | VARCHAR(20) | NOT NULL | Reported or inferred gender | `Female` |
| `age` | INT | CHECK (18-120) | Age in completed years | `32` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account operational status | `true` |

---

## 2. `dim_products`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `product_id` | VARCHAR(32) | PRIMARY KEY | Unique product SKU | `PROD-001` |
| `product_name` | VARCHAR(150) | NOT NULL | Full product merchandise name | `Smartphones Model A1` |
| `category` | VARCHAR(50) | NOT NULL | Primary department category | `Electronics` |
| `subcategory` | VARCHAR(50) | NOT NULL | Secondary product category | `Smartphones` |
| `cost_price` | NUMERIC(10,2) | >= 0 | Unit cost to manufacture or acquire (COGS) | `185.50` |
| `retail_price` | NUMERIC(10,2) | >= 0 | List price / MSRP before discount | `279.99` |
| `target_margin_pct` | NUMERIC(5,2) | NOT NULL | Expected gross margin percentage | `33.75` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Product currently in stock and sellable | `true` |

---

## 3. `dim_dates`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `date_key` | DATE | PRIMARY KEY | Calendar date | `2024-11-29` |
| `year` | INT | NOT NULL | 4-digit calendar year | `2024` |
| `quarter` | INT | 1 - 4 | Calendar quarter | `4` |
| `month` | INT | 1 - 12 | Month of year | `11` |
| `month_name` | VARCHAR(20) | NOT NULL | Full month name | `November` |
| `week_of_year` | INT | 1 - 53 | ISO week number | `48` |
| `day_of_month` | INT | 1 - 31 | Calendar day | `29` |
| `day_of_week` | INT | 1 - 7 | Day of week (1=Mon, 7=Sun) | `5` |
| `day_name` | VARCHAR(20) | NOT NULL | Day name | `Friday` |
| `is_weekend` | BOOLEAN | NOT NULL | True if Saturday or Sunday | `false` |
| `is_holiday_season` | BOOLEAN | NOT NULL | True for Q4 peak holiday season (Nov/Dec) | `true` |

---

## 4. `fact_orders`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `order_id` | VARCHAR(32) | PRIMARY KEY | Unique order transaction ID | `ORD-00001` |
| `customer_id` | VARCHAR(32) | FK -> `dim_customers` | Customer placing the transaction | `CUST-0412` |
| `session_id` | VARCHAR(32) | NULLABLE | Associated browsing session | `SESS-014521` |
| `order_date` | DATE | FK -> `dim_dates` | Date order was placed | `2024-05-18` |
| `order_status` | VARCHAR(20) | CHECK enum | Status (`Completed`, `Cancelled`, `Returned`) | `Completed` |
| `payment_method` | VARCHAR(40) | NOT NULL | Payment provider/instrument | `Credit Card` |
| `gross_amount` | NUMERIC(10,2) | >= 0 | Undiscounted product subtotal | `159.98` |
| `discount_amount` | NUMERIC(10,2) | >= 0 | Promotional discount subtracted | `20.00` |
| `net_amount` | NUMERIC(10,2) | >= 0 | Net invoice total (`gross_amount - discount`) | `139.98` |
| `shipping_amount` | NUMERIC(10,2) | >= 0 | Shipping surcharge charged to customer | `0.00` |
| `tax_amount` | NUMERIC(10,2) | >= 0 | Sales tax collected | `10.50` |
| `total_cogs` | NUMERIC(10,2) | >= 0 | Sum of item unit costs | `68.20` |
| `gross_profit` | NUMERIC(10,2) | NOT NULL | Net profit (`net_amount - total_cogs`) | `71.78` |
| `profit_margin_pct`| NUMERIC(6,2) | NULLABLE | Gross margin percentage (`profit / net_amount`) | `51.28` |
| `refund_amount` | NUMERIC(10,2) | >= 0 | Amount refunded back to customer | `0.00` |
| `delivery_days` | INT | NULLABLE | Days from placement to delivery | `3` |
| `return_reason` | VARCHAR(100) | NULLABLE | Customer return reason note | `Buyer Remorse` |

---

## 5. `fact_order_items`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `order_item_id` | VARCHAR(32) | PRIMARY KEY | Unique order line item key | `ITEM-000001` |
| `order_id` | VARCHAR(32) | FK -> `fact_orders` | Parent order reference | `ORD-00001` |
| `product_id` | VARCHAR(32) | FK -> `dim_products` | Product purchased | `PROD-014` |
| `quantity` | INT | > 0 | Units purchased | `2` |
| `unit_price` | NUMERIC(10,2) | >= 0 | Unit retail price at time of sale | `79.99` |
| `unit_cost` | NUMERIC(10,2) | >= 0 | Unit COGS at time of sale | `34.10` |
| `total_price` | NUMERIC(10,2) | >= 0 | Extended item price (`quantity * unit_price`) | `159.98` |
| `total_cost` | NUMERIC(10,2) | >= 0 | Extended item COGS (`quantity * unit_cost`) | `68.20` |
| `item_profit` | NUMERIC(10,2) | NOT NULL | Line profit (`total_price - total_cost`) | `91.78` |

---

## 6. `fact_sessions`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `session_id` | VARCHAR(32) | PRIMARY KEY | Unique web/app session ID | `SESS-000001` |
| `customer_id` | VARCHAR(32) | NULLABLE FK | Registered user ID if logged in | `CUST-1044` |
| `session_date` | DATE | FK -> `dim_dates` | Session initiation date | `2024-03-12` |
| `traffic_channel` | VARCHAR(50) | NOT NULL | Channel driving the visit | `Paid Search` |
| `device` | VARCHAR(30) | NOT NULL | Device type (`Mobile`, `Desktop`, `Tablet`) | `Desktop` |
| `pages_viewed` | INT | >= 1 | Number of distinct pageviews | `8` |
| `session_duration_seconds` | INT | >= 0 | Session length in seconds | `345` |
| `has_view_item` | INT | 0 or 1 | Viewed product detail page | `1` |
| `has_add_to_cart` | INT | 0 or 1 | Added product to cart | `1` |
| `has_begin_checkout` | INT | 0 or 1 | Initiated checkout process | `1` |
| `has_purchase` | INT | 0 or 1 | Completed transaction | `1` |
| `order_id` | VARCHAR(32) | NULLABLE | Associated order ID if purchase occurred | `ORD-03211` |

---

## 7. `fact_marketing_spend`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `spend_id` | SERIAL / INT | PRIMARY KEY | Auto-increment identifier | `102` |
| `spend_date` | DATE | FK -> `dim_dates` | Calendar date of spend | `2024-04-10` |
| `channel` | VARCHAR(50) | NOT NULL | Ad network / acquisition channel | `Paid Search` |
| `spend_amount` | NUMERIC(10,2) | >= 0 | Capital expended in USD | `542.50` |
| `impressions` | INT | >= 0 | Ad impressions served | `6840` |
| `clicks` | INT | >= 0 | Link clicks registered | `246` |
| `cpc` | NUMERIC(8,3) | >= 0 | Cost per click (`spend / clicks`) | `2.205` |
| `ctr_pct` | NUMERIC(6,2) | >= 0 | Click-through rate (`clicks / impressions * 100`) | `3.60` |

---

## 8. `fact_ab_experiment`
| Field Name | Type | Constraints | Description | Example |
|---|---|---|---|---|
| `experiment_user_id` | VARCHAR(32) | PRIMARY KEY | Distinct randomized visitor ID | `EXP-USER-00001` |
| `experiment_name` | VARCHAR(100) | NOT NULL | Name of test initiative | `checkout_one_step_v2`|
| `variant` | VARCHAR(20) | CHECK enum | Assigned variant (`control`, `treatment`) | `treatment` |
| `device` | VARCHAR(30) | NOT NULL | Access device | `Mobile` |
| `assigned_date` | DATE | FK -> `dim_dates` | Date user was first enrolled | `2024-06-05` |
| `converted` | INT | 0 or 1 | 1 if completed checkout, 0 otherwise | `1` |
| `revenue` | NUMERIC(10,2) | >= 0 | Transaction revenue if converted | `84.50` |
| `session_duration_seconds` | INT | >= 0 | Time spent in checkout flow in seconds | `210` |
