# Data Quality & Integrity Audit Report
**Execution Timestamp**: 2026-11-08 16:31:52 UTC
**Audit Result**: 🟢 PASSED (100%)

## Summary Metrics
- **Total Checks Evaluated**: 33
- **Tests Passed**: 33
- **Tests Failed**: 0

## Detailed Test Results
| Table | Test Name | Status | Severity | Details |
|---|---|---|---|---|
| `customers` | PK Uniqueness (customer_id) | ✅ PASS | ERROR | Zero duplicates found in 2500 rows. |
| `products` | PK Uniqueness (product_id) | ✅ PASS | ERROR | Zero duplicates found in 120 rows. |
| `sessions` | PK Uniqueness (session_id) | ✅ PASS | ERROR | Zero duplicates found in 30000 rows. |
| `orders` | PK Uniqueness (order_id) | ✅ PASS | ERROR | Zero duplicates found in 18000 rows. |
| `order_items` | PK Uniqueness (order_item_id) | ✅ PASS | ERROR | Zero duplicates found in 30142 rows. |
| `ab_experiment` | PK Uniqueness (experiment_user_id) | ✅ PASS | ERROR | Zero duplicates found in 12000 rows. |
| `marketing_spend` | Composite Key Uniqueness (date+channel) | ✅ PASS | ERROR | Zero duplicate entries. |
| `customers` | Null Check (customer_id) | ✅ PASS | ERROR | Column `customer_id` has 0 null values. |
| `customers` | Null Check (signup_date) | ✅ PASS | ERROR | Column `signup_date` has 0 null values. |
| `customers` | Null Check (acquisition_channel) | ✅ PASS | ERROR | Column `acquisition_channel` has 0 null values. |
| `products` | Null Check (product_id) | ✅ PASS | ERROR | Column `product_id` has 0 null values. |
| `products` | Null Check (cost_price) | ✅ PASS | ERROR | Column `cost_price` has 0 null values. |
| `products` | Null Check (retail_price) | ✅ PASS | ERROR | Column `retail_price` has 0 null values. |
| `products` | Null Check (category) | ✅ PASS | ERROR | Column `category` has 0 null values. |
| `orders` | Null Check (order_id) | ✅ PASS | ERROR | Column `order_id` has 0 null values. |
| `orders` | Null Check (customer_id) | ✅ PASS | ERROR | Column `customer_id` has 0 null values. |
| `orders` | Null Check (order_date) | ✅ PASS | ERROR | Column `order_date` has 0 null values. |
| `orders` | Null Check (net_amount) | ✅ PASS | ERROR | Column `net_amount` has 0 null values. |
| `orders` | Null Check (order_status) | ✅ PASS | ERROR | Column `order_status` has 0 null values. |
| `order_items` | Null Check (order_item_id) | ✅ PASS | ERROR | Column `order_item_id` has 0 null values. |
| `order_items` | Null Check (order_id) | ✅ PASS | ERROR | Column `order_id` has 0 null values. |
| `order_items` | Null Check (product_id) | ✅ PASS | ERROR | Column `product_id` has 0 null values. |
| `order_items` | Null Check (quantity) | ✅ PASS | ERROR | Column `quantity` has 0 null values. |
| `order_items` | Null Check (unit_price) | ✅ PASS | ERROR | Column `unit_price` has 0 null values. |
| `marketing_spend` | Null Check (spend_date) | ✅ PASS | ERROR | Column `spend_date` has 0 null values. |
| `marketing_spend` | Null Check (channel) | ✅ PASS | ERROR | Column `channel` has 0 null values. |
| `marketing_spend` | Null Check (spend_amount) | ✅ PASS | ERROR | Column `spend_amount` has 0 null values. |
| `orders` | FK Integrity (customer_id) | ✅ PASS | ERROR | All orders reference valid customer IDs. |
| `order_items` | FK Integrity (order_id) | ✅ PASS | ERROR | All items reference valid order IDs. |
| `order_items` | FK Integrity (product_id) | ✅ PASS | ERROR | All line items reference valid product SKUs. |
| `orders` | Non-Negative Revenue | ✅ PASS | ERROR | All order net amounts are non-negative. |
| `orders` | Net Revenue Math Consistency | ✅ PASS | ERROR | Net revenue matches Gross - Discount perfectly. |
| `orders` | Chronological Integrity | ✅ PASS | ERROR | Zero time-travel orders (all order dates >= signup). |

## Validation Scope
1. **Uniqueness**: Primary keys validated across all dimension and fact entities.
2. **Completeness**: Critical non-nullable foreign keys and metrics inspected for null values.
3. **Referential Integrity**: Cross-table orphan checks (orders -> customers, line items -> orders/products).
4. **Financial Consistency**: Non-negative amounts, discount subtotal equations, margin bounds.
5. **Chronological Validity**: Order dates verified strictly on or after customer registration dates.
