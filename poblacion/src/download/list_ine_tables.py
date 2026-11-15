"""Catálogo de tablas del INE para localizar los ids de las tablas que necesita una entrada.

Consulta la API del INE (operaciones disponibles y sus tablas), filtra las operaciones de
población y las tablas por palabras clave, y guarda el resultado en:
    poblacion/data/raw/ine_catalogo/tablas_<AAAA-MM-DD>.csv

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/download/list_ine_tables.py
"""

import sys
from datetime import date
from pathlib import Path

import polars as pl
import requests

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.paths import topic_dir, data_dirs

API = "https://servicios.ine.es/wstempus/js/ES"
OPERATION_WORDS = ["movimiento natural", "indicadores demogr", "continua de poblaci", "migraciones",
                   "cifras de poblaci", "fenómenos demogr", "nacimientos", "defunciones", "padr"]
TABLE_WORDS = ["nacimiento", "defuncion", "defunción", "vegetativo", "natural", "migratori",
               "crecimiento", "saldo", "madre"]

ALL_TABLES_OF = set()   # operations whose tables are all listed, filled below for the vital statistics

ops = requests.get(f"{API}/OPERACIONES_DISPONIBLES", timeout=120).json()
ops = [o for o in ops if any(w in o["Nombre"].lower() for w in OPERATION_WORDS)]
print("Operaciones:", [(o["Id"], o["Nombre"]) for o in ops])
ALL_TABLES_OF = {o["Id"] for o in ops
                 if any(w in o["Nombre"].lower() for w in ["movimiento natural", "nacimientos", "defunciones", "cifras de poblaci"])}

rows = []
for o in ops:
    tables = requests.get(f"{API}/TABLAS_OPERACION/{o['Id']}", timeout=120).json()
    for t in tables:
        if o["Id"] in ALL_TABLES_OF or any(w in t["Nombre"].lower() for w in TABLE_WORDS):
            rows.append({"operacion_id": o["Id"], "operacion": o["Nombre"],
                         "tabla_id": t["Id"], "tabla": t["Nombre"],
                         "periodicidad": t.get("FK_Periodicidad"), "ultima_modificacion": t.get("Ultima_Modificacion")})

raw, _ = data_dirs(topic_dir(__file__))
out = raw / "ine_catalogo" / f"tablas_{date.today().isoformat()}.csv"
out.parent.mkdir(parents=True, exist_ok=True)
pl.DataFrame(rows).write_csv(out)
print(f"Guardado {out} ({len(rows)} tablas)")
