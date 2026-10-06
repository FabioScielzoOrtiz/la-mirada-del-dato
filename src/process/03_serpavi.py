"""
Paso 3 del procesamiento: Sistema Estatal de Referencia del Precio del
Alquiler de Vivienda (SERPAVI), Ministerio de Vivienda, 2011-2024.

Entrada (data/raw/serpavi/):
    2026-03_09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB_v2.xlsx
    Hojas: CCAA, Provincias, Municipios, Distritos, Secciones censales.
    Formato ancho: 20 variables x 14 años, con el año como sufijo (_11 ... _24).

Salidas (data/processed/), mismo esquema en los cinco niveles:
    serpavi_ccaa.parquet        clave: cod_ccaa
    serpavi_provincias.parquet  clave: cod_prov
    serpavi_municipios.parquet  clave: cod_mun
    serpavi_distritos.parquet   clave: cod_distrito (+ cod_mun)
    serpavi_secciones.parquet   clave: cod_seccion (+ cod_mun)
    Una fila por territorio, año y tipología (colectiva / unifamiliar).

Decisiones:
- Formato largo. Las tipologías no se combinan (las medianas no se suman).
- motivo_sin_dato (solo si falta la mediana del alquiler por m2):
    foral_no_incorporado  País Vasco/Navarra antes de entrar en SERPAVI
                          (Navarra 2021, Gipuzkoa 2022, Álava y Bizkaia 2024)
    pocos_testigos        el Ministerio no publica el dato (pocas observaciones)
- Geografía del Censo 2021: en_geografia_actual marca si el municipio existe en 2026.
- Filas con P25 > mediana o mediana > P75 (errores de la fuente): se conservan los
  valores publicados y se marcan en cuantiles_incoherentes con las variables afectadas.

Ejecutar desde la raíz del proyecto (tarda unos minutos: el Excel pesa ~70 MB):
    python src/process/03_serpavi.py
"""
import sys
from pathlib import Path

import pandas as pd
import polars as pl

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/processed")
FICHERO = RAW / "serpavi" / "2026-03_09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB_v2.xlsx"

# Hoja -> (nombre de salida, {columna original: columna nueva} para las claves)
HOJAS = {
    "CCAA": ("ccaa", {"CCAA": "cod_ccaa", "LITCCAA": "nombre_ccaa"}),
    "Provincias": ("provincias", {"CPRO": "cod_prov", "LITPRO": "nombre_prov"}),
    "Municipios": ("municipios", {"CPRO": "cod_prov", "CUMUN": "cod_mun", "NMUN": "nombre_mun"}),
    "Distritos": ("distritos", {"CPRO": "cod_prov", "CUMUN": "cod_mun", "CUDIS": "cod_distrito"}),
    "Secciones censales": ("secciones", {"CPRO": "cod_prov", "CUMUN": "cod_mun", "CUSEC": "cod_seccion"}),
}
LONGITUD = {"cod_ccaa": 2, "cod_prov": 2, "cod_mun": 5, "cod_distrito": 7, "cod_seccion": 10}

# Prefijo de la variable original -> nombre base
VARIABLES = {"ALQM2_LV": "alq_m2", "ALQTBID12": "alq_mes", "SLVM2": "superficie"}
ESTADISTICOS = {"25": "p25", "M": "mediana", "75": "p75"}
TIPOLOGIAS = {"VC": "colectiva", "VU": "unifamiliar"}

# Primer año con datos de los territorios forales
INCORPORACION_PROV = {"31": 2021, "20": 2022, "01": 2024, "48": 2024}
INCORPORACION_CCAA = {"15": 2021, "16": 2022}  # Navarra; País Vasco (Gipuzkoa desde 2022)

MEDIDAS = [f"{v}_{e}" for v in VARIABLES.values() for e in ESTADISTICOS.values()]


def a_largo(df: pd.DataFrame, claves: list[str]) -> pl.DataFrame:
    """Convierte las columnas VARIABLE_ESTAD_TIPO_AA en filas (año, tipología)."""
    registros = []
    for col in df.columns:
        if col in claves:
            continue
        partes = col.split("_")
        anio = 2000 + int(partes[-1])
        if col.startswith("BI_ALVHEPCO_T"):  # testigos: BI_ALVHEPCO_TVC_11
            tipo, medida = TIPOLOGIAS[partes[-2][1:]], "n_testigos"
        else:  # ALQM2_LV_M_VC_11, ALQTBID12_25_VU_11, SLVM2_75_VC_11
            tipo = TIPOLOGIAS[partes[-2]]
            est = ESTADISTICOS[partes[-3]]
            base = VARIABLES["_".join(partes[:-3])]
            medida = f"{base}_{est}"
        registros.append((col, anio, tipo, medida))
    mapa = pd.DataFrame(registros, columns=["col", "anio", "tipologia", "medida"])

    largo = df.melt(id_vars=claves, var_name="col", value_name="valor").merge(mapa, on="col")
    largo["valor"] = pd.to_numeric(largo["valor"], errors="coerce")
    # set_index + unstack conserva las filas sin ningún dato (p. ej. forales no incorporados)
    ancho = (largo.set_index(claves + ["anio", "tipologia", "medida"])["valor"]
             .unstack("medida").reset_index())
    ancho.columns.name = None
    for m in ["n_testigos"] + MEDIDAS:
        if m not in ancho:
            ancho[m] = pd.NA
    return pl.from_pandas(ancho[claves + ["anio", "tipologia", "n_testigos"] + MEDIDAS])


def motivo(tabla: pl.DataFrame, nivel: str) -> pl.DataFrame:
    if nivel == "ccaa":
        inicio = pl.col("cod_ccaa").replace_strict(INCORPORACION_CCAA, default=0)
    else:
        inicio = pl.col("cod_prov").replace_strict(INCORPORACION_PROV, default=0)
    return tabla.with_columns(
        pl.when(pl.col("alq_m2_mediana").is_not_null()).then(None)
        .when(pl.col("anio") < inicio).then(pl.lit("foral_no_incorporado"))
        .otherwise(pl.lit("pocos_testigos"))
        .alias("motivo_sin_dato")
    )


municipios_2026 = pl.read_parquet(OUT / "municipios.parquet")["cod_mun"].implode()
salidas = {}
for hoja, (nombre, claves) in HOJAS.items():
    print(f"Leyendo hoja '{hoja}'...")
    df = pd.read_excel(FICHERO, sheet_name=hoja, dtype={k: str for k in claves})
    df = df[[c for c in df.columns if c in claves or c[-3] == "_" and c[-2:].isdigit()]]
    df = df.rename(columns=claves)
    nuevas = list(claves.values())
    clave = {"ccaa": "cod_ccaa", "provincias": "cod_prov", "municipios": "cod_mun",
             "distritos": "cod_distrito", "secciones": "cod_seccion"}[nombre]
    # Se descartan filas sin código (filas vacías y notas al pie de la hoja)
    df = df[df[clave].astype(str).str.strip().str.fullmatch(r"\d+")]
    for k in nuevas:
        if k in LONGITUD:
            df[k] = df[k].astype(str).str.strip().str.zfill(LONGITUD[k])
    t = a_largo(df, nuevas)
    t = t.with_columns(
        pl.col("anio").cast(pl.Int16),
        pl.col("n_testigos").cast(pl.Int64),
    )
    t = motivo(t, nombre)
    if "cod_mun" in t.columns:
        t = t.with_columns(pl.col("cod_mun").is_in(municipios_2026).alias("en_geografia_actual"))
    t = t.sort(clave, "anio", "tipologia")

    # ---- Comprobaciones ----
    assert t.select([clave, "anio", "tipologia"]).is_unique().all(), f"{nombre}: duplicados"
    # P25 <= mediana <= P75: las filas que no lo cumplen se conservan tal como las
    # publica el Ministerio, pero se marcan en cuantiles_incoherentes (variables afectadas)
    t = t.with_columns(
        pl.concat_str(
            [pl.when((pl.col(f"{v}_p25") > pl.col(f"{v}_mediana")) | (pl.col(f"{v}_mediana") > pl.col(f"{v}_p75")))
             .then(pl.lit(v)) for v in VARIABLES.values()],
            separator=",", ignore_nulls=True,
        ).replace("", None).alias("cuantiles_incoherentes")
    )
    inc = t.filter(pl.col("cuantiles_incoherentes").is_not_null())
    if inc.height:
        print(f"  AVISO {nombre}: {inc.height} filas con P25 <= mediana <= P75 incumplido:")
        print(inc.group_by("cod_prov" if "cod_prov" in inc.columns else clave, "anio", "tipologia", "cuantiles_incoherentes")
              .len().sort("len", descending=True).head(10))
    salidas[nombre] = t
    t.write_parquet(OUT / f"serpavi_{nombre}.parquet")
    print(f"  {nombre}: {t.height} filas, {t[clave].n_unique()} territorios")

# ---- Resumen de cobertura municipal ----
mun = salidas["municipios"]
cobertura = (
    mun.group_by("anio", "tipologia")
    .agg(
        pl.col("alq_m2_mediana").is_not_null().sum().alias("con_dato"),
        (pl.col("motivo_sin_dato") == "foral_no_incorporado").sum().alias("foral_no_incorporado"),
        (pl.col("motivo_sin_dato") == "pocos_testigos").sum().alias("pocos_testigos"),
    )
    .sort("tipologia", "anio")
)
with pl.Config(tbl_rows=40):
    print(cobertura)
print("Municipios SERPAVI que no existen en 2026:",
      mun.filter(~pl.col("en_geografia_actual"))["cod_mun"].unique().sort().to_list())

# ---- Validación cruzada con la AEAT (alquiler habitual, 2023-2024) ----
ruta_aeat = OUT / "aeat_alquiler_municipios.parquet"
if ruta_aeat.exists():
    aeat = pl.read_parquet(ruta_aeat).filter(pl.col("uso") == "habitual")
    cruce = (mun.filter(pl.col("tipologia") == "colectiva")
             .join(aeat, on=["cod_mun", "anio"], how="inner")
             .drop_nulls(["alq_mes_mediana", "alquiler_medio_mes"]))
    for anio in (2023, 2024):
        c = cruce.filter(pl.col("anio") == anio)
        r = c.select(pl.corr("alq_mes_mediana", "alquiler_medio_mes")).item()
        rho = c.select(pl.corr("alq_mes_mediana", "alquiler_medio_mes", method="spearman")).item()
        ratio = c.select((pl.col("alq_mes_mediana") / pl.col("alquiler_medio_mes")).median()).item()
        print(f"Validación AEAT {anio}: n={c.height}, Pearson={r:.3f}, Spearman={rho:.3f}, "
              f"mediana SERPAVI / media AEAT = {ratio:.2f}")

print("Guardado en", OUT.resolve())
