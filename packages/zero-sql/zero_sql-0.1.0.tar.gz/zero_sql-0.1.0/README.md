# Zero SQL

🚀 Perform database operations in Python **without writing SQL**, **without pandas**, and **without ORM**.

## Installation

```bash
pip install zero-sql
```

## Usage

```python
from zero_sql import ZeroSQL

db = ZeroSQL("test.db")
db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "email": "TEXT"})

db.add("users", {"name": "Selvi", "email": "selvi@gmail.com"})
print(db.get("users", columns=["name"], where={"id": 1}))
```
