"""Procesamiento de las tablas de la EPA para la entrada p01 (sección del ciclo económico).

Usado por: poblacion/notebooks/p01-natural-vs-migratory-growth.ipynb

Lee las tablas elegidas por src/download/download_epa_tables.py (el id de cada una está en
data/raw/ine_catalogo/epa_seleccion_<fecha>.csv), se queda con el total nacional, ambos sexos
y todas las edades, y calcula medias anuales de los cuatro trimestres (solo años completos).
Guarda en poblacion/data/processed/:

    p01_epa.parquet   anio, nacionalidad (total / española / doble / extranjera), ocupados
                      (miles, media anual), tasa_paro (%, media anual de las tasas trimestrales;
                      sin dato para «doble»: la tabla de paro no separa la doble nacionalidad)

Ejecutar desde cualquier carpeta del proyecto (después de la descarga):
    python poblacion/src/process/process_p01_epa.py
"""

import sys
from pathlib import Path

import polars as pl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import latest_raw, write_processed
from common.paths import topic_dir

TOPIC = topic_dir(__file__)

# Nivel «total» de cada dimensión que no interesa desagregar (se elige el primero que exista)
TOTAL_LEVELS = ["Total", "Ambos sexos", "Total Nacional", "Total nacional", "16 y más años",
                "De 16 y más años", "Valor absoluto"]
# En la tabla de ocupados, «Española» excluye la doble nacionalidad, que va aparte; en la de
# tasas de paro no hay categoría de doble nacionalidad.
NATIONALITY = {"total": "total", "española": "española", "doble nacionalidad": "doble",
               "extranjera": "extranjera", "extranjera: total": "extranjera"}


def read(table: str) -> pl.DataFrame:
    """CSV del INE: separador ';', miles con '.', decimales con ','; vacío = sin dato."""
    df = pl.read_csv(latest_raw(TOPIC, "ine", table), separator=";", infer_schema_length=0)
    return df.with_columns(
        pl.col("Total").str.replace_all(r"\.", "").str.replace(",", ".")
        .replace("", None).cast(pl.Float64).alias("valor")
    ).drop("Total")


def national_quarterly(table: str, value_name: str) -> pl.DataFrame:
    """Serie trimestral por nacionalidad: fija en su nivel total el resto de dimensiones."""
    df = read(table)
    nat_col = next(c for c in df.columns if c.lower().startswith("nacionalidad"))
    for col in [c for c in df.columns if c not in (nat_col, "Periodo", "valor")]:
        values = df[col].unique().to_list()
        level = next((v for v in TOTAL_LEVELS if v in values), None)
        if level is None:
            raise ValueError(f"Tabla {table}, columna «{col}»: no encuentro el nivel total entre {values}")
        print(f"  {table} · {col} = {level}")
        df = df.filter(pl.col(col) == level)
    df = (df.with_columns(nacionalidad=pl.col(nat_col).str.to_lowercase().replace_strict(NATIONALITY, default=None))
            .filter(pl.col("nacionalidad").is_not_null()))
    assert {"total", "española", "extranjera"} <= set(df["nacionalidad"]), (table, df[nat_col].unique().to_list())
    df = df.with_columns(anio=pl.col("Periodo").str.slice(0, 4).cast(pl.Int32),
                         trimestre=pl.col("Periodo").str.extract(r"T(\d)$").cast(pl.Int8))
    assert df["trimestre"].null_count() == 0, f"Periodos no trimestrales en {table}: {df['Periodo'].head().to_list()}"
    assert df.select(pl.len().over("anio", "trimestre", "nacionalidad")).max().item() == 1, f"Filas duplicadas en {table}"
    return df.select("anio", "trimestre", "nacionalidad", pl.col("valor").alias(value_name))


sel = pl.read_csv(latest_raw(TOPIC, "ine_catalogo", "epa_seleccion"), schema_overrides={"tabla_id": pl.String})
ids = dict(zip(sel["clave"], sel["tabla_id"]))
print("Tablas:", ids)

q = national_quarterly(ids["epa_ocupados_nacionalidad"], "ocupados").join(
    national_quarterly(ids["epa_paro_nacionalidad"], "tasa_paro"),
    on=["anio", "trimestre", "nacionalidad"], how="full", coalesce=True)

# Comprobación: ocupados total = española + doble nacionalidad + extranjera
w = q.pivot(on="nacionalidad", index=["anio", "trimestre"], values="ocupados")
gap = (w["total"] - w["española"] - w["doble"] - w["extranjera"]).abs().max()
print(f"Ocupados: máxima diferencia total − (española + doble + extranjera) = {gap:.1f} miles")
assert gap < 1, "Los grupos de nacionalidad no suman el total"

epa = (q.group_by("anio", "nacionalidad")
        .agg(pl.len().alias("n_trimestres"), pl.col("ocupados").mean(), pl.col("tasa_paro").mean())
        .filter(pl.col("n_trimestres") == 4)
        .drop("n_trimestres")
        .sort("anio", "nacionalidad"))
print(epa.filter(pl.col("nacionalidad") == "total").select("anio", "ocupados", "tasa_paro"))
write_processed(epa, TOPIC, "p01_epa")
