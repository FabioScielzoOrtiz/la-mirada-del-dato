"""
Descarga en bruto de la Estadística de Valor Tasado de Vivienda (Ministerio de
Vivienda, Boletín Estadístico Online). Guarda los Excel tal cual en
data/raw/valor_tasado/. Reanudable.

Ejecutar desde la raíz del proyecto:
    python src/download/download_valor_tasado.py
"""
import time
from pathlib import Path

import requests

BASE = "https://apps.fomento.gob.es/BoletinOnline2/sedal/{}.XLS"
FICHEROS = {
    "35101000": "valor_tasado_libre",
    "35101500": "valor_tasado_libre_hasta_5_anos",
    "35102000": "valor_tasado_libre_mas_5_anos",
    "35102500": "valor_tasado_protegida",
    "35103000": "tasaciones",
    "35103500": "valor_tasado_libre_municipios_25k",
}
OUT = Path("data/raw/valor_tasado")
OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"

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
    time.sleep(1)

print("Hecho. Ficheros en", OUT.resolve())
