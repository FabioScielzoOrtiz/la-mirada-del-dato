"""
Descarga en bruto: población residente en España por nacionalidad y lugar de
nacimiento (INE), a nivel nacional y provincial.

Usado por: posts/i01-population-nationality

Tablas:
  56938  ECP. Población residente por fecha, sexo, edad, nacionalidad (agrupación
         de países) y lugar de nacimiento (agrupación de países). Nacional, 2002-2025
         (serie retropolada por el INE: homogénea en todo el periodo). Tabla principal.
  9691   Cifras de Población (CP, operación sustituida por la ECP). Población residente
         por fecha, sexo, provincia, nacionalidad (agrupación de países) y lugar de
         nacimiento (agrupación de países). 2002-2022.
  60129  ECP. Población residente en viviendas familiares por fecha, sexo, grupo de
         edad y nacionalidad (española/extranjera). Por provincias, desde 2021.
  60130  ECP. Población residente en viviendas familiares por fecha, sexo, grupo de
         edad y lugar de nacimiento (España/extranjero). Por provincias, desde 2021.

Notas:
  - 9691 (CP) y 60129/60130 (ECP) son operaciones distintas y se solapan en 2021-2022:
    sirve para medir el salto entre ambas en la serie provincial.
  - 60129/60130 solo cuentan la población en viviendas familiares (sin establecimientos
    colectivos), así que no suman exactamente la población residente total.

Formato de URL igual que en download_adrh.py (CSV con separador ';').
Guarda los ficheros tal cual en data/raw/ine_poblacion/<id>.csv. Reanudable: salta
los ficheros ya descargados.

Ejecutar desde la raíz del proyecto:
    python src/download/download_ine_poblacion.py
"""

import time
from pathlib import Path

import requests

OUT = Path("data/raw/ine_poblacion")
URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"   # mismo formato que download_adrh.py

TABLAS: dict[str, str] = {
    "56938": "ECP, nacional: fecha, sexo, edad, nacionalidad y lugar de nacimiento (grupos de países), 2002-2025",
    "9691":  "CP, provincial: fecha, sexo, nacionalidad y lugar de nacimiento (grupos de países), 2002-2022",
    "60129": "ECP, provincial (viviendas familiares): fecha, sexo, grupo de edad y nacionalidad, 2021-",
    "60130": "ECP, provincial (viviendas familiares): fecha, sexo, grupo de edad y lugar de nacimiento, 2021-",
}

OUT.mkdir(parents=True, exist_ok=True)
for id_, desc in TABLAS.items():
    destino = OUT / f"{id_}.csv"
    if destino.exists() and destino.stat().st_size > 0:
        print(f"ya existe {destino.name}")
        continue
    print(f"descargando {id_}: {desc}")
    r = requests.get(URL.format(id=id_), timeout=600)
    r.raise_for_status()
    if not r.content.strip() or r.content.lstrip()[:1] == b"<":
        raise SystemExit(f"Respuesta vacía o HTML para la tabla {id_}: revisa el id o la URL")
    destino.write_bytes(r.content)
    print(f"  -> {destino}  {len(r.content) / 1e6:.1f} MB")
    time.sleep(1)

print("Hecho.")
