"""
Descarga en bruto del Atlas de Distribución de Renta de los Hogares (ADRH, INE).

Qué hace:
  1. Pide a la API del INE la lista de TODAS las tablas de la operación ADRH
     (tablas nacionales/CCAA/provincias y las 5 tablas por provincia con
     detalle municipal, de distrito y de sección censal).
  2. Guarda esa lista en data/raw/adrh/_index_tablas.csv (id, nombre, url).
  3. Descarga cada tabla en CSV (separador ';') tal cual la publica el INE,
     en data/raw/adrh/<id>.csv. No transforma nada.

Es reanudable: si se corta, al volver a ejecutarlo salta las tablas ya
descargadas. Ejecutar desde la raíz del proyecto:
    python src/download/download_adrh.py
"""
import csv
import time
from pathlib import Path

import requests

OPERACION = "353"          # código de la operación ADRH en la API del INE
API = "https://servicios.ine.es/wstempus/js/ES"
CSV_URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"
OUT = Path("data/raw/adrh")
PAUSA = 1.0                # segundos entre descargas, por cortesía con el INE

OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()


def get(url, **kw):
    for intento in range(4):
        try:
            r = s.get(url, timeout=120, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            espera = 5 * (intento + 1)
            print(f"   fallo ({e}); reintento en {espera}s")
            time.sleep(espera)
    raise RuntimeError(f"No se pudo descargar {url}")


# 1. Lista de tablas
tablas = get(f"{API}/TABLAS_OPERACION/{OPERACION}").json()
print(f"La operación tiene {len(tablas)} tablas")

with open(OUT / "_index_tablas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id", "nombre", "url_csv"])
    for t in tablas:
        w.writerow([t["Id"], t["Nombre"], CSV_URL.format(id=t["Id"])])

# 2. Descarga de cada tabla
for i, t in enumerate(tablas, 1):
    destino = OUT / f"{t['Id']}.csv"
    if destino.exists() and destino.stat().st_size > 0:
        continue
    print(f"[{i}/{len(tablas)}] {t['Id']}  {t['Nombre']}")
    r = get(CSV_URL.format(id=t["Id"]), stream=True)
    tmp = destino.with_suffix(".part")
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    tmp.rename(destino)
    time.sleep(PAUSA)

print("Hecho. Ficheros en", OUT.resolve())
