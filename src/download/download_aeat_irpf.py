"""
Descarga en bruto de las tablas de la Estadística de viviendas declaradas en
el IRPF (AEAT), ediciones 2023 y 2024.

Para cada tabla "semilla" se descarga su página HTML y también las variantes
enlazadas desde sus selectores (p. ej. vivienda habitual Sí/No, tramos de
población), un solo nivel de profundidad. Guarda en
data/raw/aeat_irpf/<año>/ y un índice _index.csv con url, título y fichero.
Guarda los bytes originales de cada página. Reanudable. Ejecutar desde la raíz del proyecto:
    python src/download/download_aeat_irpf.py
"""
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

BASE = ("https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/"
        "La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfvivienda/{y}/")

SEMILLAS = {
    2023: [
        "jrubik19cd43289fdbce9fbcbd2391abc7741113e371d8",   # valor catastral y uso, CCAA/prov
        "jrubikfd568028ab18e1fafc3590ffd1be3049dcba32dc",   # rentabilidad y precios, CCAA/prov
        "jrubik398550fc8595f66d9764a92a177519b0c947b77",    # rentabilidad y precios, municipios >20k
        "jrubikf7a8a5a0b7d1a38d33b94d3d7b460bf326cb77994",  # detalle por código postal
        "jrubikf3b34e86c57c1ee126f3c51c25abfb644a3e7e3a6",  # clasificación según uso (declarante)
        "jrubik6450d01f89579c6d20992c8e3de5164f886cad95",   # viviendas con arrendamiento (declarante)
        "jrubikf581dce8f25e851a4efe5d99575e22dcdb326986f",  # viviendas con renta imputada
        "jrubik7ca9181b384f26e269e511929236d6b056688809",   # CCAA residencia declarante vs ubicación
        "jrubikf4f835991733d596d12bfcd2722b1d7d54e61847f",  # cuenta de resultados arrendamiento
        "jrubik2a56eb0e6388762225261766346b63b7d973e0ab",   # resumen actividad arrendamiento
    ],
    2024: [
        "jrubik61a05e3830ecee0fbb552daa3b8d60a57826ffd9",   # valor catastral y uso, CCAA/prov
        "jrubikf53b07ce4916495be456684ec99760a9e5f321e9c",  # rentabilidad y precios, CCAA/prov
        "jrubikf42fc49ff49ff008eb78484361f9a64ef49975636",  # comparativa nuevos contratos, CCAA/prov
        "jrubikf51e805519b77c14638914bf8be47b12345122c36",  # rentabilidad y precios, municipios >20k
        "jrubik16a4b116943de994823993a0e8a448e24ac90bcd",   # comparativa nuevos contratos, municipios
        "jrubik57516e9b05dec25fa980640fd51a74f5c6543f9a",   # detalle por código postal
        "jrubik582b4eeccd4e39730277d218cc788357e33967da",   # comparativa nuevos contratos, código postal
        "jrubik363e5de8f59ea768b6235c20cc2f1c98f2d62663",   # clasificación según uso (declarante)
        "jrubikffbbfc140eeb3061470b400b2fe7de51c1523ce1",   # viviendas con arrendamiento (declarante)
        "jrubik1f5bf339c5c4b77c3f443fa65bb4a075b8f9dba1",   # viviendas con renta imputada
        "jrubik687aa69520a2afcfc63ba4ad06d454907ad4b2a4",   # CCAA residencia declarante vs ubicación
        "jrubikf6dab530d3943a3876eb332fcaebe8535f33f367",   # cuenta de resultados arrendamiento
        "jrubik68a3bc536e315a8831ee6d19cdc039c1781914e0",   # resumen actividad arrendamiento
    ],
}

OUT = Path("data/raw/aeat_irpf")
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"
ENLACE = re.compile(r'href="(jrubik[0-9a-f]+\.html)"')
TITULO = re.compile(r"<title>(.*?)</title>", re.S | re.I)


def get(url):
    """Devuelve los bytes originales de la página (sin recodificar)."""
    for intento in range(3):
        try:
            r = s.get(url, timeout=120)
            if r.status_code == 200 and r.content:
                return r.content
        except requests.RequestException as e:
            print(f"   error de red: {e}")
        time.sleep(5 * (intento + 1))
    return None


for anio, semillas in SEMILLAS.items():
    carpeta = OUT / str(anio)
    carpeta.mkdir(parents=True, exist_ok=True)
    base = BASE.format(y=anio)
    indice = []
    vistos = set()
    cola = [(sem + ".html", 0) for sem in semillas]
    while cola:
        nombre, nivel = cola.pop(0)
        if nombre in vistos:
            continue
        vistos.add(nombre)
        destino = carpeta / nombre
        crudo = destino.read_bytes() if destino.exists() else b""
        # La primera versión del script guardó el texto mal recodificado
        # ("EstadÃ­stica"): esos ficheros se vuelven a descargar.
        if not crudo or "EstadÃ".encode("utf-8") in crudo:
            print(f"[{anio}] {nombre}")
            crudo = get(urljoin(base, nombre))
            if crudo is None:
                print("   NO SE PUDO DESCARGAR")
                continue
            destino.write_bytes(crudo)
            time.sleep(1)
        html = crudo.decode("utf-8", errors="replace")
        m = TITULO.search(html)
        titulo = " ".join(m.group(1).split()) if m else ""
        indice.append((nombre, titulo, urljoin(base, nombre)))
        if nivel == 0:  # variantes enlazadas desde los selectores de la tabla semilla
            for enlace in ENLACE.findall(html):
                if enlace not in vistos:
                    cola.append((enlace, 1))
    with open(carpeta / "_index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["fichero", "titulo", "url"])
        w.writerows(indice)
    print(f"[{anio}] {len(indice)} páginas")

print("Hecho. Ficheros en", OUT.resolve())
