"""
Descarga en bruto de los resultados municipales del Censo de Población y
Viviendas 2011 (INE, tablas PC-Axis del sistema JAXI antiguo).

Tablas conocidas (viviendas, resultados municipales, path t20/e244/viviendas/p06):
  9mun00   Total viviendas familiares y viviendas principales por municipios (lista completa)
  10mun00  Viviendas por municipios (> 2.000 hab.) y tipo de vivienda (principal, secundaria, vacía)
  11mun00  Viviendas por municipios (> 50.000 hab. o capitales), tipo y año de construcción

Además se exploran los ficheros NNmun00.px (NN = 1..30) de los apartados de
viviendas y hogares, y se guardan los que existan (p. ej. tenencia, hogares por
tamaño). Para cada tabla se guarda el .px (incluye título y metadatos) y el CSV.
Ruta de salida: data/raw/censo2011/. Reanudable.

Ejecutar desde la raíz del proyecto:
    python src/download/download_censo2011.py
"""
import re
import time
from pathlib import Path

import requests

OUT = Path("data/raw/censo2011")
OUT.mkdir(parents=True, exist_ok=True)
APARTADOS = {
    "viviendas": "t20/e244/viviendas/p06/l0",
    "hogares": "t20/e244/hogares/p06/l0",
}
FORMATOS = {
    "px": "https://www.ine.es/jaxi/files/_px/es/px/{path}/{f}.px?nocab=1",
    "csv": "https://www.ine.es/jaxi/files/_px/es/csv_bdsc/{path}/{f}.csv_bdsc?nocab=1",
}
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"


def bajar(url):
    for intento in range(2):
        try:
            r = s.get(url, timeout=120)
            inicio = r.content[:600].lower()
            if r.status_code == 200 and r.content and b"<html" not in inicio and b"<!doctype" not in inicio:
                return r.content
            return None
        except requests.RequestException as e:
            print(f"   error de red: {e}")
            time.sleep(5)
    return None


indice = []
for apartado, path in APARTADOS.items():
    for n in range(1, 31):
        fichero = f"{n}mun00"
        base = OUT / f"{apartado}_{fichero}"
        px_path, csv_path = base.with_suffix(".px"), base.with_suffix(".csv")
        if px_path.exists() and px_path.stat().st_size > 0:
            contenido_px = px_path.read_bytes()
        else:
            contenido_px = bajar(FORMATOS["px"].format(path=path, f=fichero))
            time.sleep(0.5)
            if contenido_px is None:
                continue
            px_path.write_bytes(contenido_px)
        if not (csv_path.exists() and csv_path.stat().st_size > 0):
            contenido_csv = bajar(FORMATOS["csv"].format(path=path, f=fichero))
            if contenido_csv:
                csv_path.write_bytes(contenido_csv)
            time.sleep(0.5)
        texto = contenido_px.decode("latin-1", errors="replace")
        m = re.search(r'TITLE="(.*?)";', texto, re.S)
        titulo = " ".join(m.group(1).replace('"', "").split()) if m else ""
        print(f"{apartado}/{fichero}: {titulo}")
        indice.append((apartado, fichero, titulo))

with open(OUT / "_index.csv", "w", encoding="utf-8") as f:
    f.write("apartado;fichero;titulo\n")
    for fila in indice:
        f.write(";".join(fila) + "\n")
print(f"Hecho: {len(indice)} tablas en {OUT.resolve()}")
