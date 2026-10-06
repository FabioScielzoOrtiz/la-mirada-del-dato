"""
Descarga en bruto del Censo Anual de Población (INE), 2021 en adelante.

La lista de operaciones de la API del INE no muestra el Censo Anual por su
nombre, así que se localiza la operación a partir de una tabla conocida del
Censo Anual (tabla "semilla"): se piden sus series a la API, se lee la
operación a la que pertenecen y se listan todas las tablas de esa operación.

Funciona en dos pasos para poder revisar antes de descargar:
  1) DESCARGAR = False -> solo crea data/raw/censo_anual/_index_tablas.csv
  2) DESCARGAR = True   -> descarga las tablas del índice (o las filtradas)

Ejecutar desde la raíz del proyecto:
    python src/download/download_censo_anual_v2.py
"""
import csv
import time
from pathlib import Path

import requests

DESCARGAR = True
# Tablas conocidas del Censo Anual (población por sexo, edad y nacionalidad,
# 2021-2025). Se pueden añadir ids de otras secciones del Censo Anual.
SEMILLAS = [68529]
# Si tras revisar el índice solo queremos algunas tablas, poner aquí sus ids.
SOLO_IDS = [66620, 66621, 66622, 66623, 66627, 66628, 66629, 66846, 67078, 67079, 67080, 68065, 69991, 69992, 69993, 69994, 69995, 69996, 69997, 69998, 69999, 70000, 70001, 70002, 70003, 70371, 70372, 70373, 70374, 70375, 70381, 70382, 70383, 73027, 76306, 76312, 76810]

API = "https://servicios.ine.es/wstempus/js/ES"
CSV_URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"
OUT = Path("data/raw/censo_anual")
PAUSA = 1.0

OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()


def get_json(url):
    for intento in range(4):
        try:
            r = s.get(url, timeout=120)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            print(f"   fallo ({e}); reintento")
            time.sleep(5 * (intento + 1))
    raise RuntimeError(f"No se pudo leer {url}")


def descarga(url, destino):
    for intento in range(3):
        try:
            r = s.get(url, timeout=300, stream=True)
            if r.status_code == 200:
                tmp = destino.with_name(destino.name + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                with open(tmp, "rb") as f:
                    inicio = f.read(512).lower()
                if tmp.stat().st_size > 0 and b"<html" not in inicio and b"<!doctype" not in inicio:
                    tmp.replace(destino)
                    return True
                tmp.unlink()
        except requests.RequestException as e:
            print(f"   error de red: {e}")
        time.sleep(5 * (intento + 1))
    return False


# 1. Operación(es) a partir de las tablas semilla
ops = set()
for t in SEMILLAS:
    series = get_json(f"{API}/SERIES_TABLA/{t}?page=1")
    op = series[0].get("FK_Operacion") if series else None
    print(f"Tabla semilla {t}: operación {op}")
    if op is not None:
        ops.add(op)
if not ops:
    raise SystemExit("No se pudo identificar la operación. Pega esta salida en el chat.")

for op in ops:
    info = get_json(f"{API}/OPERACION/{op}")
    print(f"  Operación {op}: {info.get('Nombre')}  (código {info.get('Codigo', '')})")

# 2. Índice de tablas
tablas = []
for op in ops:
    for t in get_json(f"{API}/TABLAS_OPERACION/{op}"):
        tablas.append((op, t["Id"], t["Nombre"], t.get("Ultima_Modificacion", "")))
print(f"Total de tablas en la(s) operación(es): {len(tablas)}")

with open(OUT / "_index_tablas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["operacion", "id", "nombre", "ultima_modificacion", "url_csv"])
    for op, id_, nombre, mod in tablas:
        w.writerow([op, id_, nombre, mod, CSV_URL.format(id=id_)])
print("Índice guardado en", (OUT / "_index_tablas.csv").resolve())

if not DESCARGAR:
    raise SystemExit("Paso 1 terminado (DESCARGAR = False). Revisamos el índice antes de descargar.")

# 3. Descarga
if SOLO_IDS:
    tablas = [t for t in tablas if t[1] in SOLO_IDS]
fallidas = []
for i, (op, id_, nombre, _) in enumerate(tablas, 1):
    destino = OUT / f"{id_}.csv"
    if destino.exists() and destino.stat().st_size > 0:
        continue
    print(f"[{i}/{len(tablas)}] {id_}  {nombre}")
    if not descarga(CSV_URL.format(id=id_), destino):
        print("   NO SE PUDO DESCARGAR")
        fallidas.append(id_)
    time.sleep(PAUSA)

print("Hecho. Ficheros en", OUT.resolve())
if fallidas:
    print("Tablas sin descargar:", fallidas)
