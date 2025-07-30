# `tablesQLite` + `recordsQL` Integration Example

This project demonstrates how to use **`tablesQLite`** for defining table schemas and **`recordsQL`** for generating flexible, expressive SQL queries — including **`INSERT`, `UPDATE`, `SELECT`**, and more — with a focus on type-safe, validated column operations.

> 💡 `tablesQLite` focuses on table-level (DDL) logic.  
> 💡 `recordsQL` handles record-level (DML) operations like insertions, updates, selects, etc.  
> ✅ This separation encourages clear modular design.

---

## 📦 Installation

```bash
pip install tablesqlite recordsql expressql
```

---

## 📋 Features

* Define tables with rich column constraints (types, nulls, defaults, foreign keys, uniqueness, checks).
* Generate full `CREATE TABLE` SQL strings.
* Parse a SQL schema back into a `SQLTableInfo` object.
* Insert and manipulate rows using `recordsQL`-based query builders.
* Optional integration: dynamically patch record query methods into your `SQLTableInfo`.

---

## 🧪 Quick Example

### Step 1: Define a table

```python
from tablesqlite import SQLColumnInfo, SQLTableInfo
from expressQL import parse_condition, cols, col

col_names = ("id", "name", "age", "email", "balance", "is_active", "created_at", "updated_at", "cc_number")
datatypes = ("INTEGER", "TEXT", "INTEGER", "TEXT", "REAL", "BOOLEAN", "DATETIME", "DATETIME", "INTEGER")
not_nulls = (True, False, True, False, False, True, True, True, True)
default_values = (None, None, None, None, 0.0, False, "CURRENT_TIMESTAMP", "CURRENT_TIMESTAMP", None)
primary_keys = (True, False, False, False, False, False, False, False, False)
uniques = (True, False, False, True, False, False, False, False, True)
foreign_keys = (None, None, None, None, None, None, None, None, {"table": "credit_cards", "column": "cc_number"})

id, balance, age = cols("id", "balance", "age")
checks = (
    parse_condition("id > 0"), None, parse_condition("age >= 18"), None,
    parse_condition("balance >= 0"), None, None, None, None)

columns = [
    SQLColumnInfo(name, dtype, not_null=nn, default_value=defv,
                  primary_key=pk, unique=uq, foreign_key=fk, check=chk)
    for name, dtype, nn, defv, pk, uq, fk, chk in zip(
        col_names, datatypes, not_nulls, default_values,
        primary_keys, uniques, foreign_keys, checks)
]

table_info = SQLTableInfo(
    name="users",
    columns=columns,
    foreign_keys=[
        {"columns": ["cc_number"], "ref_table": "credit_cards", "ref_columns": ["cc_number"]}
    ]
)

query, _ = table_info.create_query()
print(query)
"""
>>> query1= CREATE TABLE "users" ("id" INTEGER UNIQUE PRIMARY KEY CHECK (id > 0),
 "name" TEXT, "age" INTEGER NOT NULL CHECK (age >= 18),
 "email" TEXT UNIQUE, "balance" REAL DEFAULT 0.0 CHECK (balance >= 0),
 "is_active" BOOLEAN NOT NULL DEFAULT False,
 "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "cc_number" INTEGER UNIQUE NOT NULL, FOREIGN KEY ("cc_number") REFERENCES credit_cards("cc_number"));
"""
```

---

### Step 2: Validate Table Equality

```python
table_info_ = SQLTableInfo.from_sql_schema(query)
assert query == table_info_.create_query()[0]
assert table_info.to_dict() == table_info_.to_dict()
```

---

### Step 3: Enable Record Queries

```python
from recordsQL.integrations.tablesqlite import add_query_methods
add_query_methods()  # Dynamically injects insert/update/select/delete into SQLTableInfo
```

---

### Step 4: Create an Insert Query

```python
from expressQL import cols
from datetime import datetime, timedelta

data = {
    "id": 1,
    "name": "John Doe",
    "age": 30,
    "email": "johndoe@gmail.com"
}
timestamp = (datetime.now() - timedelta(days=5)).isoformat()
extra = [("balance", 100.0), ("is_active", True), ("created_at", timestamp), ("updated_at", timestamp)]

insert_q = table_info.insert_query(data, *extra, returning=cols("id", "name", "age", "email"))
print("Insert Query:", *insert_query.placeholder_pair())
"""
Insert Query: INSERT INTO "users" (id, name, age, email, balance, is_active, created_at, updated_at)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?)  RETURNING id, name, age, email 
 [1, 'John Doe', 30, 'johndoe@gmail.com', 100.0, 1, '2025-05-23T22:18:14.115497', '2025-05-23T22:18:14.115497']
"""
```

---

### ⚠️ Column Validation Examples

```python
try:
    i_query = table_info.insert_query({"non_column": 0}, returning = cols("id", "name", "age", "email"), if_column_exists=True)
except ValueError as e:
    print(f"Caught expected ValueError: {e}")
    print("Caught expected ValueError for non-existing column in insert query.")
try:
    i_query = table_info.insert_query({"non_column": 0},
     returning = cols("id", "name", "age", "email"), if_column_exists=True,
    resolve_by="ignore")
except ValueError as e:
    print(f"Caught expected ValueError: {e}")
    print("Caught expected error for no valid columns in insert query.")
"""
Caught expected ValueError: If 'if_column_exists' is True, all provided columns must exist in the table.
Caught expected ValueError for non-existing column in insert query.
Caught expected ValueError: No valid columns provided for insertion.
Caught expected error for no valid columns in insert query.
"""
```

---

### ✅ Ignoring Invalid Columns Gracefully

```python
i_query = table_info.insert_query({"non_column": 0, "name": "Jane Doe"}, 
    returning = cols("id", "name", "age", "email"), if_column_exists=True,
    resolve_by="ignore")
print("Insert Query with ignored non-existing column:")
print(*i_query.placeholder_pair())
"""
INSERT INTO "users" (name) VALUES (?)  RETURNING id, name, age, email 
['Jane Doe']
"""
```

---

## 🧩 Design Philosophy

* `tablesQLite` = Table definitions, constraints, schema parsing (DDL).
* `recordsQL` = Insert, select, update, delete, joins, withs, expressions (DML).
* You can extend `SQLTableInfo` with dynamic query builders via `add_query_methods()` from `recordsQL`.

---

## 🔧 Advanced

Want to create your own patch or only expose selected methods?

```python
from recordsQL.integrations.tablesqlite import insert_query_for
query = insert_query_for(table_info, name="Test", age=25)
```

---

## 📚 Dependencies

* [`expressQL`](https://pypi.org/project/expressQL): SQL expression builder.
* [`recordsQL`](https://pypi.org/project/recordsQL): Record-level query generation.
* [`tablesQLite`](https://pypi.org/project/tablesQLite): Table schema abstraction (you’re here!).

---

## 📜 License

MIT License

---
