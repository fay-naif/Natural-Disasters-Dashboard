"""
Load the CSV in data/Natural_Disasters_Clean_AR.zip into a SQLite database (python/output/disasters.db)
and run every query in sql/analysis.sql.

    python python/load_to_sqlite.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "Natural_Disasters_Clean_AR.zip"
SQL = ROOT / "sql" / "analysis.sql"
DB = ROOT / "python" / "output" / "disasters.db"


def main():
    df = pd.read_csv(DATA, compression="zip", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as con:
        df.to_sql("disasters", con, if_exists="replace", index=False)
        queries = [q.strip() for q in SQL.read_text(encoding="utf-8").split(";") if q.strip()]
        for q in queries:
            title = next((l for l in q.splitlines() if l.startswith("-- ") and l[3:4].isdigit()), "")
            print(title)
            body = "\n".join(l for l in q.splitlines() if not l.startswith("--"))
            print(pd.read_sql_query(body, con).to_string(index=False))
            print()


if __name__ == "__main__":
    main()
