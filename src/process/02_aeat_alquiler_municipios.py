"""
Paso 2 del procesamiento: alquiler por municipio de la AEAT
(Estadística de viviendas declaradas en el IRPF, ediciones 2023 y 2024).

Entradas (data/raw/aeat_irpf/<año>/): páginas HTML de las tablas
    "Rentabilidad y precios de alquiler ... municipios de más de 20.000 habitantes"
    (Tramo de Población: Total; Vivienda habitual: Sí / No) y, para 2024,
    "Comparativa ... con los nuevos contratos ... municipios de más de 20.000 habitantes".
Las tablas se localizan por su título en _index.csv.

Salida (data/processed/):
    aeat_alquiler_municipios.parquet
        Una fila por municipio, año y uso (habitual / no_habitual).

Decisiones:
- Solo filas municipales (las que llevan el código INE como sufijo "Nombre-04003");
  se descartan las de total, CCAA y provincia.
- Las columnas de nuevos contratos solo existen para 2024 y vivienda habitual;
  en el resto de filas quedan nulas.
- La AEAT publica varias copias idénticas de algunas tablas; se comprueba que
  coinciden y se usa una.

Ejecutar desde la raíz del proyecto:
    python src/process/02_aeat_alquiler_municipios.py
"""
import csv
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import polars as pl

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/processed")
AEAT = RAW / "aeat_irpf"

# Tablas a usar: (año, uso) -> patrón del título en _index.csv
TABLAS = {
    (2023, "habitual"): r"Rentabilidad y precios de alquiler para municipios de más de 20\.000 habitantes Tramo de Población: Total , Vivienda habitual: Si$",
    (2023, "no_habitual"): r"Rentabilidad y precios de alquiler para municipios de más de 20\.000 habitantes Tramo de Población: Total , Vivienda habitual: No$",
    (2024, "habitual"): r"Rentabilidad y precios de alquiler como vivienda habitual para municipios de más de 20\.000 habitantes Tramo de Población: Total , Vivienda habitual: Si$",
    (2024, "no_habitual"): r"Rentabilidad y precios de alquiler como vivienda habitual para municipios de más de 20\.000 habitantes Tramo de Población: Total , Vivienda habitual: No$",
    (2024, "comparativa"): r"Comparativa de rentabilidad y precios de alquiler como vivienda habitual con los nuevos contratos para municipios de más de 20\.000 habitantes Tramo de Población: Total$",
}

# Cabecera original (normalizada) -> nombre de columna
COLUMNAS = {
    "Número de viviendas con valor catastral": "n_viv_valor_catastral",
    "Número viviendas arrendadas": "n_viv_arrendadas",
    "Alquiler medio mensual": "alquiler_medio_mes",
    "Alquiler m2 mensual": "alquiler_m2_mes",
    "m2 medios": "m2_medios",
    "Días alquiler medios": "dias_alquiler_medios",
    "Valor referencia medio": "valor_referencia_medio",
    "Rentabilidad bruta %": "rentabilidad_bruta",
    "Número de viviendas a disposición": "n_viv_a_disposicion",
    # comparativa con nuevos contratos (2024)
    "Alquiler medio mensual (nuevos contratos)": "alquiler_medio_mes_nuevos",
    "m2 medios (nuevos contratos)": "m2_medios_nuevos",
    "Valor referencia medio (nuevos contratos)": "valor_referencia_medio_nuevos",
    "Rentabilidad bruta estimada %": "rentabilidad_bruta_estimada",
    "Rentabilidad bruta estimada % (nuevos contratos)": "rentabilidad_bruta_estimada_nuevos",
}


def norm(texto) -> str:
    return " ".join(str(texto).split())


def localizar(anio: int, patron: str) -> Path:
    """Devuelve el fichero cuya tabla tiene ese título; comprueba que las copias son idénticas."""
    filas = list(csv.reader(open(AEAT / str(anio) / "_index.csv", encoding="utf-8"), delimiter=";"))
    candidatos = [AEAT / str(anio) / f for f, titulo, _ in filas[1:]
                  if re.search(patron, norm(titulo.split(f"IRPF: {anio}: ", 1)[-1]))]
    if not candidatos:
        raise FileNotFoundError(f"No se encuentra la tabla {anio}: {patron}")
    tablas = [leer_tabla(c) for c in candidatos]
    assert all(t.equals(tablas[0]) for t in tablas), f"copias distintas de la tabla {anio}: {patron}"
    return candidatos[0]


def leer_tabla(ruta: Path) -> pd.DataFrame:
    html = ruta.read_bytes().decode("utf-8")
    tablas = pd.read_html(StringIO(html), decimal=",", thousands=".")
    tabla = max(tablas, key=lambda t: t.shape[0])
    # Cabeceras de dos niveles: se usa el nivel inferior
    tabla.columns = [norm(c[-1] if isinstance(c, tuple) else c) for c in tabla.columns]
    return tabla


def procesar(anio: int, uso: str, ruta: Path) -> pd.DataFrame:
    t = leer_tabla(ruta)
    loc = t.iloc[:, 0].astype(str).str.strip()
    m = loc.str.extract(r"^(?P<nombre_aeat>.*)-(?P<cod_mun>\d{5})$")
    t = pd.concat([m, t.iloc[:, 1:]], axis=1)[m["cod_mun"].notna()]
    desconocidas = [c for c in t.columns[2:] if c not in COLUMNAS]
    assert not desconocidas, f"columnas no previstas en {ruta.name}: {desconocidas}"
    t = t.rename(columns=COLUMNAS)
    for c in t.columns[2:]:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t["anio"], t["uso"] = anio, uso
    return t


# ---------------------------------------------------------------------------
partes = {clave: procesar(*clave, localizar(clave[0], patron)) for clave, patron in TABLAS.items()}

comp = partes.pop((2024, "comparativa"))
base = pd.concat(partes.values(), ignore_index=True)

# Control: el stock de la comparativa coincide con la tabla principal de 2024
hab24 = partes[(2024, "habitual")].set_index("cod_mun")
c = comp.set_index("cod_mun")
comunes = hab24.index.intersection(c.index)
for col in ["alquiler_medio_mes", "m2_medios", "valor_referencia_medio"]:
    dif = (hab24.loc[comunes, col] - c.loc[comunes, col]).abs().max()
    assert dif == 0, f"la comparativa no coincide con la tabla principal en {col} (dif. máx. {dif})"

nuevas = ["alquiler_medio_mes_nuevos", "m2_medios_nuevos", "valor_referencia_medio_nuevos",
          "rentabilidad_bruta_estimada", "rentabilidad_bruta_estimada_nuevos"]
comp = comp[["cod_mun"] + nuevas].assign(anio=2024, uso="habitual")
base = base.merge(comp, on=["cod_mun", "anio", "uso"], how="left")

orden = ["cod_mun", "nombre_aeat", "anio", "uso", "n_viv_valor_catastral", "n_viv_arrendadas",
         "alquiler_medio_mes", "alquiler_m2_mes", "m2_medios", "dias_alquiler_medios",
         "valor_referencia_medio", "rentabilidad_bruta", "n_viv_a_disposicion"] + nuevas
aeat = pl.from_pandas(base[orden]).with_columns(pl.col("anio").cast(pl.Int16)).sort("cod_mun", "anio", "uso")

# ---------------------------------------------------------------------------
# Comprobaciones
# ---------------------------------------------------------------------------
assert aeat.select(["cod_mun", "anio", "uso"]).is_unique().all(), "duplicados municipio-año-uso"
municipios = pl.read_parquet(OUT / "municipios.parquet")
fuera = aeat.join(municipios, on="cod_mun", how="anti")
assert fuera.height == 0, f"códigos que no existen en 2026: {fuera['cod_mun'].unique().to_list()}"
assert aeat.join(municipios.filter(pl.col("foral")), on="cod_mun", how="semi").height == 0, "aparecen municipios forales"

nulos = aeat.group_by("anio", "uso").agg(
    pl.len().alias("n_municipios"),
    *[pl.col(c).null_count().alias(f"nulos_{c}") for c in ["n_viv_arrendadas", "alquiler_medio_mes", "alquiler_m2_mes"]],
).sort("anio", "uso")
with pl.Config(tbl_cols=-1, tbl_width_chars=200):
    print(nulos)

aeat.write_parquet(OUT / "aeat_alquiler_municipios.parquet")
print(f"Guardado: {aeat.height} filas en {(OUT / 'aeat_alquiler_municipios.parquet').resolve()}")
