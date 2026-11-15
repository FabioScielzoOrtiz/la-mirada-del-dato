"""Descarga en bruto de tablas del INE (formato CSV, separador ';') para la entrada p01.

Usado por: poblacion/notebooks/p01-natural-vs-migratory-growth.ipynb

Cada tabla se guarda tal cual en:
    poblacion/data/raw/ine/<id>_<AAAA-MM-DD>.csv
con la fecha de descarga en el nombre; nunca se sobrescribe. Si el INE responde 503, el
script reintenta varias veces antes de fallar; las tablas ya descargadas hoy se saltan.

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/download/download_ine_tables.py
"""

import sys
from datetime import date
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import download
from common.paths import topic_dir, data_dirs

# id: qué contiene (según el catálogo del INE). Candidatas: se descartan tras revisarlas.
TABLES = {
    # Estadística Continua de Población: stocks trimestrales, 2002 – último trimestre
    "79273": "Población residente por fecha, sexo, nacionalidad y país de nacimiento (España/extranjero)",
    # Estadística de Migraciones: saldo con el extranjero (2008–2021 y, con la nueva estadística, 2021–)
    "24310": "Saldo migratorio con el extranjero por año, país de nacimiento y nacionalidad (2008–2021)",
    "69760": "Saldos por año, sexo, país de nacimiento y tipo de saldo (2021–)",
    # MNP: nacimientos y defunciones (series desde 1975) y fenómenos demográficos
    "6525": "Nacimientos por lugar de residencia de la madre (serie desde 1975)",
    "6562": "Defunciones por lugar de residencia (serie desde 1975)",
    "6566": "Fenómenos demográficos por tipo de fenómeno (nacimientos, defunciones, crecimiento vegetativo), 1992–",
    # MNP: nacimientos según la madre, defunciones según el fallecido
    "58929": "Nacimientos por nacionalidad de la madre, nacional y CCAA, 2009–",
    "58930": "Nacimientos por país de nacimiento de la madre, nacional y CCAA, 2009–",
    "58701": "Defunciones a nivel nacional por nacionalidad",
    "70648": "Defunciones a nivel nacional por país de nacimiento",
    # Estimaciones experimentales del INE para el último año sin MNP definitivo (2025–)
    "46682": "Estimación mensual de nacimientos (EMN): mensuales y acumulados, nacional, CCAA y provincias",
    "62277": "Estimación de defunciones (EDeS): mensuales y acumuladas, nacional y CCAA, 2009–",
    # Indicadores Demográficos Básicos: tasas por mil (contraste)
    "1416": "Saldo vegetativo por mil habitantes",
    "5224": "Crecimiento de la población por cada mil habitantes",
    "2776": "Porcentaje de nacidos por nacionalidad de la madre según orden del nacimiento",
}

topic = topic_dir(__file__)
raw, _ = data_dirs(topic)
failed = []
for table, what in TABLES.items():
    target = raw / "ine" / f"{table}_{date.today().isoformat()}.csv"
    if target.exists() and target.stat().st_size > 0:
        print(f"{table}: ya descargada hoy")
        continue
    url = f"https://www.ine.es/jaxiT3/files/t/csv_bdsc/{table}.csv"
    try:
        out = download(url, topic, source="ine", name=table, ext="csv", timeout=600)
    except Exception as e:  # keep going with the other tables
        print(f"{table}: ERROR {e}")
        failed.append(table)
        continue
    head = out.read_bytes()[:200].lstrip()
    if not head or head[:1] == b"<":
        out.unlink()
        print(f"{table}: respuesta vacía o HTML, descartada")
        failed.append(table)
print("Hecho." if not failed else f"Fallaron: {failed}. Vuelve a ejecutar más tarde.")
