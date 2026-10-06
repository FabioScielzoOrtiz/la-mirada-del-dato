"""
Descarga en bruto del Censo de Población y Viviendas 2021 (INE).

Guarda cada fichero tal cual lo publica el INE en data/raw/censo2021/.
Reanudable: salta lo ya descargado (y vuelve a intentar los ficheros vacíos).
Ejecutar desde la raíz del proyecto:
    python src/download/download_censo2021.py

Nota: las tablas municipales del Censo 2021 son tablas "tpx" del sistema
JAXI antiguo del INE, no del JAXI-T3 (por eso la primera versión de este
script dejó ficheros vacíos). Para cada tabla se prueban varios formatos de
URL y se guarda el primero que devuelve contenido válido.
"""
import time
from pathlib import Path

import requests

OUT = Path("data/raw/censo2021")


def tpx(id_):
    """URLs candidatas para una tabla tpx, por orden de preferencia."""
    return [
        (f"https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/{id_}.csv", ".csv"),
        (f"https://www.ine.es/jaxi/files/tpx/es/csv_bd/{id_}.csv", ".tsv"),
        (f"https://www.ine.es/jaxi/files/tpx/es/xlsx/{id_}.xlsx", ".xlsx"),
        (f"https://www.ine.es/jaxi/files/tpx/es/px/{id_}.px", ".px"),
    ]


def directo(url):
    return [(url, Path(url).suffix)]


FICHEROS = {
    # --- Indicadores por sección censal (TODAS las secciones de España) ---
    "C2021_Indicadores": directo("https://www.ine.es/censos2021/C2021_Indicadores.csv"),
    "C2021_indicadores_diccionario": directo("https://www.ine.es/censos2021/indicadores_seccen_c2021.xlsx"),

    # --- Tablas municipales: todos los municipios ---
    "t59525_viviendas_por_tipo": tpx(59525),
    "t59531_viviendas_intensidad_uso": tpx(59531),
    "t59543_hogares_por_tamano": tpx(59543),

    # --- Tablas municipales: solo capitales y municipios > 50.000 hab. ---
    "t59526_viviendas_tipo_50k": tpx(59526),
    "t59527_viviendas_ano_construccion_50k": tpx(59527),
    "t59528_viviendas_superficie_50k": tpx(59528),
    "t59529_viviendas_regimen_tenencia_50k": tpx(59529),
    "t59530_viviendas_tamano_hogar_superficie_50k": tpx(59530),
    "t59544_hogares_tamano_tipo_50k": tpx(59544),
    "t59545_hogares_tamano_estructura_50k": tpx(59545),

    # --- Microdatos (muestra del 10%) ---
    "microdatos/CensoViviendas_2021": directo("https://www.ine.es/ftp/microdatos/censopv/cen21/CensoViviendas_2021.zip"),
    "microdatos/CensoPersonas_2021": directo("https://www.ine.es/ftp/microdatos/censopv/cen21/CensoPersonas_2021.zip"),
}

s = requests.Session()


def ya_descargado(nombre):
    base = OUT / nombre
    for p in base.parent.glob(base.name + ".*"):
        if p.suffix != ".part" and p.stat().st_size > 0:
            return p
    return None


def descarga(url, destino):
    """Descarga url en destino. Devuelve True si el contenido es válido."""
    try:
        r = s.get(url, timeout=300, stream=True)
        if r.status_code != 200:
            return False
        tmp = destino.with_name(destino.name + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        # contenido válido: no vacío y no una página HTML de error
        with open(tmp, "rb") as f:
            inicio = f.read(512).lower()
        if tmp.stat().st_size == 0 or b"<html" in inicio or b"<!doctype" in inicio:
            tmp.unlink()
            return False
        tmp.replace(destino)
        return True
    except requests.RequestException as e:
        print(f"   error de red: {e}")
        return False


for nombre, candidatas in FICHEROS.items():
    hecho = ya_descargado(nombre)
    if hecho:
        print("ya existe:", hecho.name)
        continue
    print("descargando:", nombre)
    ok = False
    for url, ext in candidatas:
        destino = OUT / (nombre + ext)
        destino.parent.mkdir(parents=True, exist_ok=True)
        for intento in range(2):
            if descarga(url, destino):
                print("   OK ->", destino.name, f"({destino.stat().st_size/1e6:.1f} MB)")
                ok = True
                break
            time.sleep(3)
        if ok:
            break
        print("   sin contenido en", url)
    if not ok:
        print("   NO SE PUDO DESCARGAR", nombre)
    time.sleep(1)

# Limpieza: ficheros vacíos que dejó la versión anterior del script
for p in OUT.glob("*.csv"):
    if p.stat().st_size == 0:
        p.unlink()
        print("borrado fichero vacío:", p.name)

print("Hecho. Ficheros en", OUT.resolve())
