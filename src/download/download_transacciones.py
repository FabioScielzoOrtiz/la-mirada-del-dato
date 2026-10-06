"""
Descarga en bruto de la Estadística de Transacciones Inmobiliarias
(compraventa de viviendas) del Ministerio de Vivienda, Boletín Estadístico
Online. Origen de los datos: Consejo General del Notariado.

Guarda los Excel tal cual en data/raw/transacciones/. Reanudable.
Ejecutar desde la raíz del proyecto:
    python src/download/download_transacciones.py
"""
import time
from pathlib import Path

import requests

BASE = "https://apps.fomento.gob.es/BoletinOnline2/sedal/{}.XLS"
FICHEROS = {
    # --- Número de transacciones: CCAA y provincias ---
    "34010110": "n_total",
    "34010120": "n_libre",
    "34010130": "n_libre_nueva",
    "34010140": "n_libre_segunda_mano",
    "34010150": "n_protegida",
    "34010160": "n_protegida_nueva",
    "34010170": "n_protegida_segunda_mano",
    "34010180": "n_nueva",
    "34010190": "n_segunda_mano",
    "340101a0": "n_libre_tipologia_edificio",
    "340101b0": "n_libre_nueva_tipologia_edificio",
    "340101c0": "n_libre_segunda_mano_tipologia_edificio",
    "340101d0": "n_residencia_comprador",
    "340101e0": "n_residentes_ccaa_comprador_ubicacion",
    "340101f0": "n_residentes_prov_comprador_ubicacion",
    "340101g0": "n_extranjeros_ccaa_comprador_ubicacion",
    "340101h0": "n_extranjeros_prov_comprador_ubicacion",
    "340101i0": "n_extranjeros_calificacion_todas",
    "340101j0": "n_extranjeros_calificacion_nueva",
    "340101k0": "n_extranjeros_calificacion_segunda_mano",
    "340101l0": "n_libre_valor_superficie",
    # --- Número de transacciones: municipios ---
    "34010210": "mun_n_total",
    "34010220": "mun_n_libre",
    "34010230": "mun_n_protegida",
    "34010240": "mun_n_nueva",
    "34010250": "mun_n_segunda_mano",
    # --- Valor de las transacciones: CCAA y provincias ---
    "34020110": "valor_libre",
    "34020120": "valor_libre_nueva",
    "34020130": "valor_libre_segunda_mano",
    "34020140": "valor_libre_extranjeros",
    "34020150": "valor_medio_libre",
    "34020160": "valor_medio_libre_nueva",
    "34020170": "valor_medio_libre_segunda_mano",
    "34020180": "valor_medio_libre_extranjeros",
}
OUT = Path("data/raw/transacciones")
OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"

fallidos = []
for codigo, nombre in FICHEROS.items():
    destino = OUT / f"{codigo}_{nombre}.xls"
    if destino.exists() and destino.stat().st_size > 0:
        print("ya existe:", destino.name)
        continue
    print("descargando:", destino.name)
    for intento in range(3):
        try:
            r = s.get(BASE.format(codigo), timeout=120)
            inicio = r.content[:512].lower()
            if r.status_code == 200 and r.content and b"<html" not in inicio:
                destino.write_bytes(r.content)
                break
        except requests.RequestException as e:
            print(f"   error de red: {e}")
        time.sleep(5 * (intento + 1))
    else:
        print("   NO SE PUDO DESCARGAR", codigo)
        fallidos.append(codigo)
    time.sleep(1)

print("Hecho. Ficheros en", OUT.resolve())
if fallidos:
    print("Sin descargar:", fallidos)
