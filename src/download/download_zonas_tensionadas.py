"""
Descarga en bruto de las resoluciones trimestrales del BOE con la relación de
zonas de mercado residencial tensionado (art. 18 Ley 12/2023).

Para cada identificador BOE descarga:
  - el XML  (https://www.boe.es/diario_boe/xml.php?id=...)  -> se procesará
  - el PDF  (ruta tomada del propio XML, etiqueta <url_pdf>) -> copia oficial
en data/raw/zonas_tensionadas/. Reanudable.

Si en el buscador del BOE aparece alguna resolución que no está en la lista,
basta con añadir su identificador a IDS.

Ejecutar desde la raíz del proyecto:
    python src/download/download_zonas_tensionadas.py
"""
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

IDS = {
    "BOE-A-2024-5214": "2024T1",
    "BOE-A-2024-20576": "2024T3",
    "BOE-A-2025-1721": "2024T4",
    "BOE-A-2025-8636": "2025T1",
    "BOE-A-2025-15728": "2025T2",
    "BOE-A-2025-21901": "2025T3",
    "BOE-A-2026-2448": "2025T4",
    "BOE-A-2026-9175": "2026T1",
    "BOE-A-2026-16532": "2026T2",
}

OUT = Path("data/raw/zonas_tensionadas")
OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"


def get(url):
    for intento in range(3):
        try:
            r = s.get(url, timeout=120)
            if r.status_code == 200 and r.content:
                return r.content
        except requests.RequestException as e:
            print(f"   error de red: {e}")
        time.sleep(5 * (intento + 1))
    return None


for boe_id, trimestre in IDS.items():
    xml_path = OUT / f"{boe_id}.xml"
    pdf_path = OUT / f"{boe_id}.pdf"

    if not (xml_path.exists() and xml_path.stat().st_size > 0):
        print(f"{boe_id} ({trimestre}): XML")
        contenido = get(f"https://www.boe.es/diario_boe/xml.php?id={boe_id}")
        if contenido is None:
            print("   NO SE PUDO DESCARGAR EL XML")
            continue
        xml_path.write_bytes(contenido)
        time.sleep(1)

    # Comprobación: título y trimestre que declara el propio documento
    raiz = ET.parse(xml_path).getroot()
    titulo = (raiz.findtext(".//titulo") or "").strip()
    print(f"   {titulo[:160]}...")

    if not (pdf_path.exists() and pdf_path.stat().st_size > 0):
        url_pdf = (raiz.findtext(".//url_pdf") or "").strip()
        if url_pdf:
            if url_pdf.startswith("/"):
                url_pdf = "https://www.boe.es" + url_pdf
            contenido = get(url_pdf)
            if contenido and contenido[:4] == b"%PDF":
                pdf_path.write_bytes(contenido)
            else:
                print("   no se pudo descargar el PDF (no es imprescindible)")
        time.sleep(1)

print("Hecho. Ficheros en", OUT.resolve())
