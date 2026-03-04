#!/usr/bin/env python3
"""
export_db.py — Exporte elnet.db vers des fichiers SQL compressés
Segmente le dump en chunks gzip pour git LFS ou transfert manuel.
Utilisation : python export_db.py
"""
import sqlite3
import gzip
import os

DB_PATH  = os.environ.get("DATABASE_URL", "sqlite:///./elnet.db") \
              .replace("sqlite:///", "").replace("./", "")
SQL_PATH = "database.sql"
GZ_PATH  = "database.sql.gz"

print(f"📦 Export de {DB_PATH} → {SQL_PATH} + {GZ_PATH} ...")

conn = sqlite3.connect(DB_PATH)

# Export SQL brut
with open(SQL_PATH, "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write(line + "\n")

# Export compressé (pour git LFS ou transfert scp)
with open(SQL_PATH, "rb") as f_in, gzip.open(GZ_PATH, "wb") as f_out:
    f_out.write(f_in.read())

conn.close()

sql_size = os.path.getsize(SQL_PATH) / (1024 * 1024)
gz_size  = os.path.getsize(GZ_PATH)  / (1024 * 1024)

print(f"✅ Export terminé :")
print(f"   database.sql    → {sql_size:.1f} MB  (brut)")
print(f"   database.sql.gz → {gz_size:.1f}  MB  (compressé)")
print()
print("📌 Pour versionner avec git LFS :")
print("   git lfs install")
print("   git lfs track 'database.sql.gz'")
print("   git add .gitattributes database.sql.gz && git commit -m 'chore: export BDD'")
print()
print("📌 Ou copier directement sur le VPS :")
print("   scp database.sql.gz user@vps:/app/elnet/")
