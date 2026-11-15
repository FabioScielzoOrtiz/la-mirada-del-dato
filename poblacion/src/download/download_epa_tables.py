"""Descarga en bruto de las tablas de la EPA (Encuesta de Población Activa, INE) para la entrada p01.

Usado por: poblacion/notebooks/p01-natural-vs-migratory-growth.ipynb (sección «¿Sigue la
inmigración al ciclo económico?»)

Los ids de las tablas de la EPA cambian con las revisiones de la encuesta, así que el script no
los fija: consulta el catálogo de la operación en la API del INE y elige las tablas por su nombre.
Guarda:
    poblacion/data/raw/ine_catalogo/tablas_epa_<AAAA-MM-DD>.csv   catálogo completo de la EPA
    poblacion/data/raw/ine_catalogo/epa_seleccion_<AAAA-MM-DD>.csv  qué id corresponde a cada clave
    poblacion/data/raw/ine/<id>_<AAAA-MM-DD>.csv                 cada tabla elegida, tal cual
y escribe en pantalla qué id corresponde a cada tabla. Si un nombre no da exactamente una tabla,
no descarga esa y muestra las candidatas: copia la salida para revisarla.

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/download/download_epa_tables.py
"""

import re
import sys
from datetime import date
from pathlib import Path

import polars as pl
import requests

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import download
from common.paths import topic_dir, data_dirs

API = "https://servicios.ine.es/wstempus/js/ES"

# clave: (patrón del nombre de la tabla, en minúsculas; qué se usa de ella). Solo tablas trimestrales:
# el INE publica algunas tablas dos veces, una trimestral (periodicidad 3) y otra anual (12).
QUARTERLY = 3
WANTED = {
    "epa_ocupados_nacionalidad": (
        r"^ocupados por nacionalidad, sexo y grupo de edad",
        "Ocupados (miles) por nacionalidad, trimestral, total nacional",
    ),
    "epa_paro_nacionalidad": (
        r"^tasas de paro por nacionalidad, sexo y comunidad autónoma",
        "Tasa de paro (%) por nacionalidad, trimestral (se usa la fila «Total Nacional»)",
    ),
}

topic = topic_dir(__file__)
raw, _ = data_dirs(topic)

# 1. Operación EPA y su catálogo de tablas
ops = requests.get(f"{API}/OPERACIONES_DISPONIBLES", timeout=120).json()
epa = [o for o in ops if o.get("Codigo") == "EPA" or "encuesta de población activa" in o["Nombre"].lower()]
print("Operación:", [(o["Id"], o.get("Codigo"), o["Nombre"]) for o in epa])
if len(epa) != 1:
    sys.exit("No se ha identificado una única operación EPA: copia la línea anterior.")
tables = requests.get(f"{API}/TABLAS_OPERACION/{epa[0]['Id']}", timeout=120).json()
cat = pl.DataFrame([{"tabla_id": str(t["Id"]), "tabla": t["Nombre"],
                     "periodicidad": t.get("FK_Periodicidad"),
                     "ultima_modificacion": t.get("Ultima_Modificacion")} for t in tables])
out = raw / "ine_catalogo" / f"tablas_epa_{date.today().isoformat()}.csv"
out.parent.mkdir(parents=True, exist_ok=True)
cat.write_csv(out)
print(f"Catálogo EPA: {cat.height} tablas -> {out.relative_to(topic)}")

# 2. Elegir y descargar (la selección se guarda para el procesado)
failed, chosen = [], []
for key, (pattern, what) in WANTED.items():
    hits = cat.filter(pl.col("tabla").str.to_lowercase().str.contains(pattern),
                      pl.col("periodicidad") == QUARTERLY)
    if hits.height != 1:
        near = cat.filter(pl.col("tabla").str.to_lowercase().str.contains(pattern.split(",")[0].lstrip("^")))
        print(f"\n{key}: {hits.height} tablas encajan con «{pattern}». Candidatas:")
        for r in near.iter_rows(named=True):
            print(f"   {r['tabla_id']}: {r['tabla']} (periodicidad {r['periodicidad']})")
        failed.append(key)
        continue
    table = hits["tabla_id"][0]
    chosen.append({"clave": key, "tabla_id": table, "tabla": hits["tabla"][0]})
    print(f"\n{key} -> tabla {table}: {hits['tabla'][0]}")
    target = raw / "ine" / f"{table}_{date.today().isoformat()}.csv"
    if target.exists() and target.stat().st_size > 0:
        print("   ya descargada hoy")
        continue
    try:
        f = download(f"https://www.ine.es/jaxiT3/files/t/csv_bdsc/{table}.csv", topic,
                     source="ine", name=table, ext="csv", timeout=600)
    except Exception as e:
        print(f"   ERROR {e}")
        failed.append(key)
        continue
    if f.read_bytes()[:200].lstrip()[:1] in (b"", b"<"):
        f.unlink()
        print("   respuesta vacía o HTML, descartada")
        failed.append(key)

if chosen:
    sel = raw / "ine_catalogo" / f"epa_seleccion_{date.today().isoformat()}.csv"
    pl.DataFrame(chosen).write_csv(sel)
    print(f"Selección guardada en {sel.relative_to(topic)}")
print("\nHecho." if not failed else f"\nPendientes: {failed}. Copia la salida completa.")
