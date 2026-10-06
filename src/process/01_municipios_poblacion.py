"""
Paso 1 del procesamiento: tabla de municipios y serie de población (Padrón).

Entradas (data/raw/):
    diccionario26.xlsx          Relación de municipios y códigos INE a 1-ene-2026
    pobmun/pobmunAA.xls(x)      Cifras oficiales de población, 1996, 1998-2025

Salidas (data/processed/):
    municipios.parquet   Una fila por municipio vigente en 2026:
                         cod_mun, nombre_mun, cod_prov, nombre_prov,
                         cod_ccaa, nombre_ccaa, foral
    poblacion.parquet    Formato largo, cada año con sus propios municipios:
                         cod_mun, anio, pob_total, pob_hombres, pob_mujeres,
                         en_geografia_actual

Decisiones:
- Clave municipal: código INE de 5 dígitos (CPRO + CMUN) como texto.
- El Padrón NO se armoniza a la geografía de 2026: cada año conserva los
  municipios que existían entonces; en_geografia_actual marca si el código
  sigue existiendo en 2026 (False = municipio desaparecido por fusión).
- En 1998 el código de municipio incluye el dígito de control (4 cifras):
  se toman las 3 primeras.

Ejecutar desde la raíz del proyecto:
    python src/process/01_municipios_poblacion.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
import polars as pl

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

# Códigos y nombres de comunidades autónomas (INE, CODAUTO)
CCAA = {
    "01": "Andalucía", "02": "Aragón", "03": "Asturias, Principado de",
    "04": "Balears, Illes", "05": "Canarias", "06": "Cantabria",
    "07": "Castilla y León", "08": "Castilla-La Mancha", "09": "Cataluña",
    "10": "Comunitat Valenciana", "11": "Extremadura", "12": "Galicia",
    "13": "Madrid, Comunidad de", "14": "Murcia, Región de",
    "15": "Navarra, Comunidad Foral de", "16": "País Vasco",
    "17": "Rioja, La", "18": "Ceuta", "19": "Melilla",
}
PROV_FORALES = {"01", "20", "48", "31"}  # Álava, Gipuzkoa, Bizkaia, Navarra


def leer_excel(ruta: Path) -> pd.DataFrame:
    """Lee la primera hoja como texto y devuelve la tabla desde la fila de cabecera."""
    crudo = pd.read_excel(ruta, sheet_name=0, header=None, dtype=str)
    primera = crudo.iloc[:, 0].astype(str).str.strip().str.upper()
    fila = primera[primera.isin(["CPRO", "CÓDIGO PROVINCIA", "CODAUTO"])].index[0]
    tabla = crudo.iloc[fila + 1:].reset_index(drop=True)
    tabla.columns = [str(c).strip() for c in crudo.iloc[fila]]
    return tabla


# ---------------------------------------------------------------------------
# 1. Padrón: todos los años
# ---------------------------------------------------------------------------
partes = []
for ruta in sorted((RAW / "pobmun").glob("pobmun*.xls*")):
    aa = int(re.search(r"pobmun(\d{2})", ruta.name).group(1))
    anio = 1900 + aa if aa >= 90 else 2000 + aa
    t = leer_excel(ruta)
    # 7 columnas: CPRO, PROVINCIA, CMUN, NOMBRE, total, hombres, mujeres
    # 6 columnas (1996, 1998, 1999): CPRO, CMUN, NOMBRE, total, hombres, mujeres
    if t.shape[1] >= 7:
        t = t.iloc[:, [0, 1, 2, 3, 4, 5, 6]]
        t.columns = ["cpro", "nombre_prov", "cmun", "nombre_mun", "pob_total", "pob_hombres", "pob_mujeres"]
    else:
        t = t.iloc[:, [0, 1, 2, 3, 4, 5]]
        t.columns = ["cpro", "cmun", "nombre_mun", "pob_total", "pob_hombres", "pob_mujeres"]
        t["nombre_prov"] = None
    t = t[t["cpro"].astype(str).str.strip().str.fullmatch(r"\d{1,2}")]
    t["cpro"] = t["cpro"].str.strip().str.zfill(2)
    t["cmun"] = t["cmun"].astype(str).str.strip().str[:3].str.zfill(3)
    t["anio"] = anio
    partes.append(t)

pob = (
    pl.from_pandas(pd.concat(partes, ignore_index=True))
    .with_columns(
        (pl.col("cpro") + pl.col("cmun")).alias("cod_mun"),
        pl.col("nombre_mun").str.strip_chars(),
        pl.col("nombre_prov").str.strip_chars(),
        *[pl.col(c).str.strip_chars().str.replace_all(r"[.\s]", "").cast(pl.Int64)
          for c in ["pob_total", "pob_hombres", "pob_mujeres"]],
        pl.col("anio").cast(pl.Int16),
    )
)

# ---------------------------------------------------------------------------
# 2. Municipios vigentes en 2026
# ---------------------------------------------------------------------------
dic = pl.from_pandas(leer_excel(RAW / "diccionario26.xlsx")).select(
    pl.col("CODAUTO").str.strip_chars().str.zfill(2).alias("cod_ccaa"),
    pl.col("CPRO").str.strip_chars().str.zfill(2).alias("cod_prov"),
    pl.col("CMUN").str.strip_chars().str.zfill(3).alias("cmun"),
    pl.col("NOMBRE").str.strip_chars().alias("nombre_mun"),
)
# Nombre de provincia: el del Padrón más reciente que lo trae
nombres_prov = (
    pob.filter(pl.col("nombre_prov").is_not_null())
    .sort("anio", descending=True)
    .group_by("cpro").agg(pl.col("nombre_prov").first())
    .rename({"cpro": "cod_prov"})
)
municipios = (
    dic.with_columns((pl.col("cod_prov") + pl.col("cmun")).alias("cod_mun"))
    .join(nombres_prov, on="cod_prov", how="left")
    .with_columns(
        pl.col("cod_ccaa").replace_strict(CCAA, default=None).alias("nombre_ccaa"),
        pl.col("cod_prov").is_in(PROV_FORALES).alias("foral"),
    )
    .select("cod_mun", "nombre_mun", "cod_prov", "nombre_prov", "cod_ccaa", "nombre_ccaa", "foral")
    .sort("cod_mun")
)

poblacion = (
    pob.with_columns(pl.col("cod_mun").is_in(municipios["cod_mun"].implode()).alias("en_geografia_actual"))
    .select("cod_mun", "anio", "pob_total", "pob_hombres", "pob_mujeres", "en_geografia_actual")
    .sort("cod_mun", "anio")
)

# ---------------------------------------------------------------------------
# 3. Comprobaciones
# ---------------------------------------------------------------------------
assert municipios["cod_mun"].is_unique().all(), "códigos de municipio duplicados"
assert municipios["nombre_prov"].null_count() == 0, "provincias sin nombre"
assert municipios["nombre_ccaa"].null_count() == 0, "CCAA sin nombre"
assert poblacion.select(["cod_mun", "anio"]).is_unique().all(), "duplicados municipio-año"
assert poblacion["pob_total"].null_count() == 0, "población total nula"
descuadre = poblacion.filter(pl.col("pob_hombres") + pl.col("pob_mujeres") != pl.col("pob_total"))
assert descuadre.height == 0, f"hombres + mujeres != total en {descuadre.height} filas"

resumen = (
    poblacion.group_by("anio")
    .agg(
        pl.len().alias("n_municipios"),
        pl.col("pob_total").sum().alias("poblacion_espana"),
        (~pl.col("en_geografia_actual")).sum().alias("n_no_vigentes_2026"),
    )
    .sort("anio")
    .with_columns(pl.col("anio").cast(pl.Utf8))
)
with pl.Config(tbl_rows=40, thousands_separator="."):
    print(resumen)
print(f"Municipios vigentes 2026: {municipios.height}  (forales: {municipios['foral'].sum()})")

municipios.write_parquet(OUT / "municipios.parquet")
poblacion.write_parquet(OUT / "poblacion.parquet")
print("Guardado en", OUT.resolve())
