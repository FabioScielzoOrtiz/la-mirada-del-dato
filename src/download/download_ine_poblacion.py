"""
Descarga en bruto: población residente en España por nacionalidad y país de
nacimiento (INE).

Usado por: posts/i01-population-nationality

Fuentes candidatas (TODO: elegir las tablas en INEbase y rellenar TABLAS):
  1. Estadística Continua de Población (ECP), trimestral, desde 2021.
     Población por nacionalidad (española / extranjera, grupos de países) y por país de nacimiento.
  2. Cifras de Población (CP), semestral 1971–2021 (nacionalidad y país de nacimiento desde 2002).
     Sirve para alargar la serie hacia atrás. Comprobar que las definiciones coinciden con la ECP.
  3. Estadística del Padrón Continuo, a 1 de enero desde 1998. Detalle municipal; no es la cifra
     oficial de población, pero es la serie más larga por nacionalidad y país de nacimiento.

Cómo encontrar el id de una tabla: abrirla en INEbase y mirar la URL (t=XXXXX).
Se descarga el CSV (separador ';') igual que en download_adrh.py:
    https://www.ine.es/jaxiT3/files/t/csv_bdsc/<id>.csv

Guarda los ficheros tal cual en data/raw/ine_poblacion/<id>.csv. Reanudable.
Ejecutar desde la raíz del proyecto:
    python src/download/download_ine_poblacion.py
"""

import time
from pathlib import Path

import requests

OUT = Path("data/raw/ine_poblacion")
URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"   # mismo formato que download_adrh.py

# TODO: id de tabla -> descripción
TABLAS: dict[str, str] = {
    # "XXXXX": "ECP, población por nacionalidad",
    # "XXXXX": "ECP, población por país de nacimiento",
}

if not TABLAS:
    raise SystemExit("TODO: añadir los ids de las tablas del INE en TABLAS")

OUT.mkdir(parents=True, exist_ok=True)
for id_, desc in TABLAS.items():
    destino = OUT / f"{id_}.csv"
    if destino.exists() and destino.stat().st_size > 0:
        print(f"ya existe {destino.name}")
        continue
    r = requests.get(URL.format(id=id_), timeout=300)
    r.raise_for_status()
    destino.write_bytes(r.content)
    print(f"{destino.name}  {len(r.content) / 1e6:.1f} MB  ({desc})")
    time.sleep(1)
