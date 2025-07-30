
# Project Title

A brief description of what this project does and who it's for

# DataEase

**DataEase** is a Python package designed to simplify data preprocessing and SQL database interaction for developers and analysts. It provides easy-to-use functions for cleaning DataFrames, converting between file formats (CSV/JSON), and managing MySQL data pipelines.

---

## 🚀 Features

### 🧼 DataFrame Cleaning
- `remove_nulls()` – Drop rows with any missing values
- `remove_duplicates()` – Drop duplicate rows
- `join_columns()` – Combine multiple columns into one
- `drop_constant_columns()` – Remove columns with constant values
- `auto_convert_types()` – Automatically infer and cast data types

### 🔄 File Conversion
- `df_to_csv()` and `csv_to_df()` – Convert between CSV and DataFrame
- `df_to_json()` and `json_to_df()` – Convert between JSON and DataFrame

### 💽 MySQL Utilities
- `connect_to_mysql()` – Connect to a MySQL server
- `create_table_if_not_exists()` – Auto-generate MySQL schema from a DataFrame
- `append_df_to_table()` – Append DataFrame data to a MySQL table

### 🔍 SQL Tools
- `run_query()` – Execute custom SQL queries
- `insert_row()` – Insert row dynamically from dictionary

### 🛠️ SQL Query Builder
Build secure SQL queries programmatically:
```python
from DataEase import SQLQueryBuilder

query = (
    SQLQueryBuilder()
    .select("orders", ["orders.id", "users.name"])
    .join("INNER", "users", "orders.user_id = users.id")
    .where({"users.status": "active"})
    .order_by("orders.created_at", ascending=False)
    .limit(5)
    .build()
)
print(query)
"# SELECT orders.id, users.name FROM orders INNER JOIN users ON orders.user_id = users.id WHERE users.status='active' ORDER BY orders.created_at DESC LIMIT 5;"

---
## 👥 Contributors

- **Praveen Anand** – Project Lead and Core Developer  
- **Rahul Anand** – Co-Author: MySQL integration and Testing  
- **Joel Ishika Reddy Kandukuri** – Co-Author: DataFrame utilities and enhancements  

---

## 🧑‍💻 Installation

```bash
pip install DataEase
