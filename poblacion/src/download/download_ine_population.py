"""Descarga en bruto de la tabla 56938 del INE (ECP): población residente por fecha, sexo, edad,
nacionalidad y país de nacimiento, nacional, 2002 – 1-I-2025 (serie homogénea).

Usado por: poblacion/notebooks/p01-population-nationality-origin.ipynb

Guarda el CSV (separador ';') tal cual en:
    poblacion/data/raw/ine_poblacion/56938_<AAAA-MM-DD>.csv
con la fecha de descarga en el nombre; nunca se sobrescribe.

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/download/download_ine_population.py
"""

import sys
from datetime import date
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import download
from common.paths import topic_dir, data_dirs

TABLE = "56938"
URL = f"https://www.ine.es/jaxiT3/files/t/csv_bdsc/{TABLE}.csv"

topic = topic_dir(__file__)
raw, _ = data_dirs(topic)
target = raw / "ine_poblacion" / f"{TABLE}_{date.today().isoformat()}.csv"

if target.exists() and target.stat().st_size > 0:
    print(f"Ya descargado hoy: {target.relative_to(topic)}")
else:
    out = download(URL, topic, source="ine_poblacion", name=TABLE, ext="csv", timeout=600)
    with open(out, "rb") as f:
        head = f.read(200).lstrip()
    if not head or head[:1] == b"<":   # empty or an HTML error page instead of a CSV
        out.unlink()
        raise SystemExit(f"Respuesta vacía o HTML para la tabla {TABLE}: revisa el id o la URL ({URL}).")
    print("Hecho.")
