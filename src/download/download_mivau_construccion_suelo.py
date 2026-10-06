"""
Descarga en bruto de tablas del Boletín Estadístico Online del Ministerio de
Vivienda sobre oferta de vivienda y suelo:
  - 32: Vivienda libre (iniciadas y terminadas)       -> data/raw/vivienda_libre/
  - 33: Estimación del parque de viviendas            -> data/raw/parque_viviendas/
  - 36: Precios de suelo urbano                       -> data/raw/suelo_urbano/
  - 31: Vivienda y rehabilitación protegidas          -> data/raw/vivienda_protegida/
Reanudable. Ejecutar desde la raíz del proyecto:
    python src/download/download_mivau_construccion_suelo.py
"""
import time
from pathlib import Path

import requests

BASE = "https://apps.fomento.gob.es/BoletinOnline2/sedal/{}.XLS"
RAW = Path("data/raw")

CONOCIDOS = {
    "vivienda_libre": {
        "32100500": "iniciadas_mensual",
        "32101000": "terminadas_mensual",
        "32200500": "iniciadas_anual",
        "32201000": "terminadas_anual",
    },
    "parque_viviendas": {
        "33100500": "total_viviendas_ccaa_prov",
        "33102000": "principales_no_principales_ccaa_prov",
    },
    "suelo_urbano": {
        "36100500": "n_transacciones_total",
        "36101000": "n_transacciones_persona_fisica",
        "36101500": "n_transacciones_persona_juridica",
        "36102000": "n_transacciones_mun_menos_1000",
        "36102500": "n_transacciones_mun_1000_5000",
        "36103000": "n_transacciones_mun_5000_10000",
        "36103500": "n_transacciones_mun_10000_50000",
        "36104000": "n_transacciones_mun_mas_50000",
        "36200500": "valor_total",
        "36201000": "valor_persona_fisica",
        "36201500": "valor_persona_juridica",
        "36300500": "superficie_total",
        "36301000": "superficie_persona_fisica",
        "36301500": "superficie_persona_juridica",
        "36400500": "precio_m2_ccaa_prov",
        "36401000": "precio_m2_mun_menos_1000",
        "36401500": "precio_m2_mun_1000_5000",
        "36402000": "precio_m2_mun_5000_10000",
        "36402500": "precio_m2_mun_10000_50000",
        "36403000": "precio_m2_mun_mas_50000",
    },
    "vivienda_protegida": {
        # Series mensuales
        "31201000": "m_solicitudes_calif_provisional_estatal",
        "31201500": "m_calif_provisionales_estatal",
        "31202000": "m_calif_provisionales_estatal_autonomico",
        "31202510": "m_calif_provisionales_regimen_general_concertado",
        "31202520": "m_calif_provisionales_regimen_especial",
        "31202530": "m_calif_provisionales_otros_tipos",
        "31203010": "m_calif_provisionales_promotor_privado",
        "31203020": "m_calif_provisionales_promotor_publico",
        "31203510": "m_calif_provisionales_propiedad",
        "31203520": "m_calif_provisionales_alquiler_sin_opcion",
        "31203530": "m_calif_provisionales_alquiler_con_opcion",
        "31203540": "m_calif_provisionales_otros_regimenes",
        "31204000": "m_solicitudes_calif_definitiva_estatal",
        "31204500": "m_calif_definitivas_estatal",
        "31205000": "m_calif_definitivas_estatal_autonomico",
        "31205510": "m_calif_definitivas_regimen_general_concertado",
        "31205520": "m_calif_definitivas_regimen_especial",
        "31205530": "m_calif_definitivas_otros_tipos",
        "31206010": "m_calif_definitivas_promotor_privado",
        "31206020": "m_calif_definitivas_promotor_publico",
        "31206510": "m_calif_definitivas_propiedad",
        "31206520": "m_calif_definitivas_alquiler_sin_opcion",
        "31206530": "m_calif_definitivas_alquiler_con_opcion",
        "31206540": "m_calif_definitivas_otros_regimenes",
        # Series anuales
        "31301000": "a_solicitudes_calif_provisional_estatal",
        "31302000": "a_calif_provisionales_estatal",
        "31303000": "a_calif_provisionales_estatal_autonomico",
        "31304000": "a_solicitudes_calif_definitiva_estatal",
        "31305000": "a_calif_definitivas_estatal",
        "31306000": "a_calif_definitivas_estatal_autonomico",
        "31307000": "a_calif_provisionales_planes_promotor",
        "31308000": "a_calif_provisionales_regimen_uso",
        # Rehabilitación protegida
        "31501000": "rehab_m_solicitudes_estatal",
        "31502000": "rehab_m_aprob_provisionales_estatal",
        "31503000": "rehab_m_aprob_definitivas_estatal",
        "31504000": "rehab_m_solicitudes_estatal_autonomico",
        "31505000": "rehab_m_aprob_provisionales_estatal_autonomico",
        "31506000": "rehab_m_aprob_definitivas_estatal_autonomico",
        "31601000": "rehab_a_solicitudes_estatal",
        "31602000": "rehab_a_aprob_provisionales_estatal",
        "31603000": "rehab_a_aprob_definitivas_estatal",
        "31604000": "rehab_a_solicitudes_estatal_autonomico",
        "31605000": "rehab_a_aprob_provisionales_estatal_autonomico",
        "31606000": "rehab_a_aprob_definitivas_estatal_autonomico",
    },
}

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (investigacion academica UC3M)"


def bajar(codigo):
    """Devuelve el contenido del XLS o None si no existe."""
    for intento in range(3):
        try:
            r = s.get(BASE.format(codigo), timeout=120)
            if r.status_code != 200:
                print(f"   HTTP {r.status_code}")
                return None
            # Excel válido: firma OLE2 (.xls, D0 CF 11 E0) o ZIP (.xlsx, PK)
            if r.status_code == 200 and r.content[:4] in (b"\xd0\xcf\x11\xe0", b"PK\x03\x04"):
                return r.content
            if r.status_code == 200:
                print(f"   respuesta no Excel ({len(r.content)} bytes): {r.content[:80]!r}")
                return None
        except requests.RequestException as e:
            print(f"   error de red: {e}")
        time.sleep(5 * (intento + 1))
    return None


for carpeta, tablas in CONOCIDOS.items():
    out = RAW / carpeta
    out.mkdir(parents=True, exist_ok=True)
    for codigo, nombre in tablas.items():
        destino = out / f"{codigo}_{nombre}.xls"
        if destino.exists() and destino.stat().st_size > 0:
            continue
        print("descargando:", carpeta, destino.name)
        contenido = bajar(codigo)
        if contenido:
            destino.write_bytes(contenido)
        else:
            print("   NO SE PUDO DESCARGAR", codigo)
        time.sleep(1)

print("Hecho.")
