"""
Descarga en bruto de la Estadística Experimental de Viviendas Turísticas (INE).

- Tablas 1-4 (series completas, todas las oleadas desde 2020):
    39364  viviendas, plazas y plazas/vivienda: nacional, CCAA y provincias
    39363  viviendas, plazas y plazas/vivienda: municipios
    39365  % de viviendas turísticas sobre viviendas censadas: nacional, CCAA, provincias
    39366  % de viviendas turísticas sobre viviendas censadas: municipios
- Tabla 5: un Excel por oleada con detalle por distrito y sección censal.

Guarda todo tal cual en data/raw/viviendas_turisticas/. Reanudable.
Ejecutar desde la raíz del proyecto:
    python src/download/download_viviendas_turisticas.py
"""
import time
from pathlib import Path

import requests

OUT = Path("data/raw/viviendas_turisticas")
TABLA = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/{id}.csv"
T5 = "https://www.ine.es/experimental/viv_turistica/exp_viv_turistica_tabla5_{p}.xlsx?nocab=1"

FICHEROS = {
    "t39364_viv_tur_ccaa_prov.csv": TABLA.format(id=39364),
    "t39363_viv_tur_municipios.csv": TABLA.format(id=39363),
    "t39365_pct_viv_tur_ccaa_prov.csv": TABLA.format(id=39365),
    "t39366_pct_viv_tur_municipios.csv": TABLA.format(id=39366),
}
OLEADAS = ["AGO2020", "FEB2021", "AGO2021", "FEB2022", "AGO2022", "FEB2023",
           "AGO2023", "FEB2024", "AGO2024", "NOV2024", "MAY2025", "NOV2025",
           "MAY2026"]
for p in OLEADAS:
    FICHEROS[f"tabla5_secciones/tabla5_{p}.xlsx"] = T5.format(p=p)

s = requests.Session()


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


for nombre, url in FICHEROS.items():
    destino = OUT / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        print("ya existe:", nombre)
        continue
    print("descargando:", nombre)
    if not descarga(url, destino):
        print("   NO SE PUDO DESCARGAR:", url)
    time.sleep(1)

print("Hecho. Ficheros en", OUT.resolve())
