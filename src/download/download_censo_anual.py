"""
Descarga en bruto del Censo Anual de Población (INE), 2021 en adelante.

El INE publica el Censo Anual repartido en varias operaciones (población por
edad y nacionalidad; educación y actividad; ocupación; años de llegada y
residencia anterior; estado civil). Este script:
  1. Busca en la API del INE todas las operaciones cuyo nombre contiene
     "censo anual" y las muestra.
  2. Lista todas sus tablas y guarda un índice en
     data/raw/censo_anual/_index_tablas.csv (operación, id, nombre).
  3. Descarga cada tabla en CSV (separador ';'), tal cual, en
     data/raw/censo_anual/<id>.csv. Incluye las tablas por municipio,
     distrito y sección censal.

Reanudable y con validación (no guarda respuestas vacías ni páginas de error).
Ejecutar desde la raíz del proyecto:
    python src/download/download_censo_anual.py
"""
import csv
import time
from pathlib import Path

import requests

API = "https://servicios.ine.es/wstempus/js/ES"
CSV_URL = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"
OUT = Path("data/raw/censo_anual")
PATRON = "censo anual"
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


# 1. Operaciones del Censo Anual
import unicodedata


def norm(txt):
    txt = unicodedata.normalize("NFKD", txt or "")
    return "".join(c for c in txt if not unicodedata.combining(c)).lower()


todas = get_json(f"{API}/OPERACIONES_DISPONIBLES")
censos = [o for o in todas if "censo" in norm(o.get("Nombre"))]
print("Operaciones del INE con 'censo' en el nombre:")
for o in censos:
    print(f"  Id={o['Id']}  Codigo={o.get('Cod_IOE', o.get('Codigo', ''))}  {o['Nombre']}")

# Operaciones elegidas: las que mencionan 'anual'. Si no hay ninguna, se
# puede forzar a mano poniendo sus Id en OPS_MANUAL.
OPS_MANUAL = []
ops = [o for o in censos if o["Id"] in OPS_MANUAL] if OPS_MANUAL else \
      [o for o in censos if "anual" in norm(o.get("Nombre"))]
if not ops:
    raise SystemExit("\nNinguna contiene 'anual'. Copia la lista de arriba en el "
                     "chat y ajustamos OPS_MANUAL.")
print("\nSe descargarán las tablas de:")
for o in ops:
    print(f"  {o['Id']}  {o['Nombre']}")

# 2. Tablas de cada operación
tablas = []
for o in ops:
    for t in get_json(f"{API}/TABLAS_OPERACION/{o['Id']}"):
        tablas.append((o["Nombre"], t["Id"], t["Nombre"]))
print(f"Total de tablas: {len(tablas)}")

with open(OUT / "_index_tablas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["operacion", "id", "nombre", "url_csv"])
    for op, id_, nombre in tablas:
        w.writerow([op, id_, nombre, CSV_URL.format(id=id_)])

# 3. Descarga
fallidas = []
for i, (op, id_, nombre) in enumerate(tablas, 1):
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
