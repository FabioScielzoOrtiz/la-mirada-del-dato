"""Procesamiento de las tablas del INE para la entrada p01 (¿Crece España solo gracias a la inmigración?).

Usado por: poblacion/notebooks/p01-natural-vs-migratory-growth.ipynb

Lee los CSV más recientes de poblacion/data/raw/ine/ (descargados con
src/download/download_ine_tables.py), los limpia, comprueba su coherencia y guarda en
poblacion/data/processed/:

    p01_stocks.parquet       población a 1 de enero por nacionalidad y país de nacimiento, 2002–2026 (ECP, 79273)
    p01_components.parquet   componentes del crecimiento por año: nacimientos, defunciones, saldo natural,
                             saldo migratorio con el extranjero y crecimiento observado, 1975–2025
    p01_births_mother.parquet  nacimientos según nacionalidad y país de nacimiento de la madre, 2002–2024
    p01_deaths_group.parquet   defunciones según nacionalidad y país de nacimiento, 2009–2024
    p01_rates.parquet        tasas por mil del INE (crecimiento y saldo vegetativo), 1975–2024
    p01_checks.parquet       comprobaciones de coherencia (las que muestra la entrada)

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/process/process_p01.py
"""

import sys
from pathlib import Path

import polars as pl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import latest_raw, write_processed
from common.paths import topic_dir

TOPIC = topic_dir(__file__)
MESES = {"enero": 1, "abril": 4, "julio": 7, "octubre": 10}


def read(table: str) -> pl.DataFrame:
    """CSV del INE: separador ';', miles con '.', decimales con ','; vacío = sin dato."""
    df = pl.read_csv(latest_raw(TOPIC, "ine", table), separator=";", infer_schema_length=0)
    return df.with_columns(
        pl.col("Total").str.replace_all(r"\.", "").str.replace(",", ".")
        .replace("", None).cast(pl.Float64).alias("valor")
    ).drop("Total")


def year_of(col: str) -> pl.Expr:
    return pl.col(col).str.slice(0, 4).cast(pl.Int32)


# ── 1. Stocks: población a 1 de enero (ECP, 79273) ────────────────────────────────────────────
ecp = read("79273").filter(pl.col("Sexo") == "Total").with_columns(
    anio=pl.col("Periodo").str.extract(r"(\d{4})$").cast(pl.Int32),
    mes=pl.col("Periodo").str.extract(r"de (\w+) de").replace_strict(MESES, return_dtype=pl.Int8),
)
stocks = (
    ecp.filter(pl.col("mes") == 1)
    .select("anio", nacionalidad="Nacionalidad", nacimiento="País de nacimiento", poblacion="valor")
    .sort("anio", "nacionalidad", "nacimiento")
)
# Comprobación: los cruces suman los totales (el INE redondea: tolerancia de unas pocas personas)
wide = stocks.pivot(on=["nacionalidad", "nacimiento"], index="anio", values="poblacion")
check_stocks = wide.select(
    "anio",
    dif_nacionalidad=pl.col('{"Total","Total"}') - pl.col('{"Española","Total"}') - pl.col('{"Extranjera","Total"}'),
    dif_nacimiento=pl.col('{"Total","Total"}') - pl.col('{"Total","España"}') - pl.col('{"Total","Extranjero"}'),
)
assert check_stocks.select(pl.col("dif_nacionalidad", "dif_nacimiento").abs().max()).max_horizontal().item() <= 10

# ── 2. Componentes del crecimiento ────────────────────────────────────────────────────────────
def monthly_to_annual(df: pl.DataFrame, filters: list[pl.Expr]) -> pl.DataFrame:
    return (df.filter(*filters).with_columns(anio=year_of("Periodo"))
            .group_by("anio").agg(valor=pl.col("valor").sum(), meses=pl.len()).sort("anio"))

births_mnp = monthly_to_annual(read("6525"), [pl.col("Comunidades y Ciudades Autónomas") == "Total"])
deaths_mnp = monthly_to_annual(read("6562"), [pl.col("Comunidades y Ciudades Autónomas") == "Total"])
assert births_mnp["meses"].min() == 12 and deaths_mnp["meses"].min() == 12

# Estimaciones experimentales (EMN y EDeS), para 2025 y para contrastarlas con el MNP
births_emn = monthly_to_annual(read("46682"), [pl.col("Comunidades y Ciudades Autónomas").is_null(),
                                               pl.col("Provincias").is_null(), pl.col("Tipo de dato") == "Dato base"])
deaths_edes = monthly_to_annual(read("62277"), [pl.col("Total Nacional") == "Total Nacional",
                                                pl.col("Comunidades y Ciudades Autónomas").is_null(),
                                                pl.col("Tipo de dato") == "Dato base"])
last_mnp = births_mnp["anio"].max()
est_year = last_mnp + 1
assert births_emn.filter(pl.col("anio") == est_year)["meses"].item() == 12
assert deaths_edes.filter(pl.col("anio") == est_year)["meses"].item() == 12

natural = (
    births_mnp.select("anio", nacimientos="valor")
    .join(deaths_mnp.select("anio", defunciones="valor"), on="anio")
    .with_columns(fuente_natural=pl.lit("MNP definitivo"))
    .vstack(pl.DataFrame({
        "anio": [est_year],
        "nacimientos": births_emn.filter(pl.col("anio") == est_year)["valor"],
        "defunciones": deaths_edes.filter(pl.col("anio") == est_year)["valor"],
        "fuente_natural": ["Estimación experimental (EMN, EDeS)"],
    }, schema_overrides={"anio": pl.Int32}))
    .with_columns(saldo_natural=pl.col("nacimientos") - pl.col("defunciones"))
)

# Saldo migratorio con el extranjero: estadística antigua (2008–2020) y nueva (2021–)
mig_old = (read("24310").filter(pl.col("País de nacimiento") == "Total", pl.col("Nacionalidad") == "Total")
           .select(anio=year_of("Periodo"), saldo_migratorio="valor"))
mig_new = (read("69760").filter(pl.col("País de nacimiento") == "Total", pl.col("Sexo") == "Ambos sexos",
                                pl.col("Tipo de saldo") == "Saldo exterior")
           .select(anio=year_of("Periodo"), saldo_migratorio="valor"))
first_new = mig_new["anio"].min()
migration = pl.concat([
    mig_old.filter(pl.col("anio") < first_new).with_columns(fuente_migratorio=pl.lit("Estadística de Migraciones (hasta 2020)")),
    mig_new.with_columns(fuente_migratorio=pl.lit("Estadística de Migraciones y Cambios de Residencia (desde 2021)")),
])

# Crecimiento observado: población del 1-I de t+1 menos la del 1-I de t (se atribuye al año t)
total = stocks.filter(pl.col("nacionalidad") == "Total", pl.col("nacimiento") == "Total").select("anio", "poblacion")
growth = total.with_columns(crecimiento=pl.col("poblacion").shift(-1) - pl.col("poblacion")).drop_nulls("crecimiento")

components = (
    natural.join(migration, on="anio", how="left")
    .join(growth.rename({"poblacion": "poblacion_1_enero"}), on="anio", how="left")
    .with_columns(
        residuo=pl.col("crecimiento") - pl.col("saldo_natural") - pl.col("saldo_migratorio"),
        saldo_migratorio_implicito=pl.col("crecimiento") - pl.col("saldo_natural"),
    )
    .sort("anio")
)

# ── 3. Nacimientos según la madre y defunciones según el fallecido ────────────────────────────
nat_m = (read("58929").filter(pl.col("Nacional y Comunidades Autónomas") == "Total Nacional",
                              pl.col("Nacionalidad de la madre").is_in(["Total", "Española", "Extranjera"]))
         .select(anio=year_of("Periodo"), grupo="Nacionalidad de la madre", valor="valor")
         .pivot(on="grupo", index="anio", values="valor"))
born_m = (read("58930").filter(pl.col("Nacional y Comunidades autónomas") == "Total Nacional",
                               pl.col("Lugar de nacimiento de la madre").is_in(["Total", "España", "Extranjera"]))
          .select(anio=year_of("Periodo"), grupo="Lugar de nacimiento de la madre", valor="valor")
          .pivot(on="grupo", index="anio", values="valor"))
share_idb = (read("2776").filter(pl.col("Orden de nacimiento") == "Todos", pl.col("Nacionalidad") == "Extranjera")
             .select(anio=year_of("Periodo"), pct_madre_extranjera_idb="valor"))
births_mother = (
    births_mnp.select("anio", nacimientos="valor").filter(pl.col("anio") >= 2002)
    .join(nat_m.select("anio", madre_nacionalidad_extranjera="Extranjera", madre_nacionalidad_total="Total"), on="anio", how="left")
    .join(born_m.select("anio", madre_nacida_extranjero="Extranjera", madre_nacimiento_total="Total"), on="anio", how="left")
    .join(share_idb, on="anio", how="left")
    .with_columns(
        # 2002–2008: sin la tabla por nacionalidad, se aplica el porcentaje del INE (IDB 2776)
        madre_nacionalidad_extranjera=pl.coalesce(
            "madre_nacionalidad_extranjera",
            (pl.col("nacimientos") * pl.col("pct_madre_extranjera_idb") / 100).round(0)),
    )
    .sort("anio")
)

dn = (read("58701").filter(pl.col("Nacionalidad").is_in(["Total", "Española", "Extranjera", "No consta"]))
      .select(anio=year_of("Periodo"), grupo="Nacionalidad", valor="valor").pivot(on="grupo", index="anio", values="valor"))
db = (read("70648").filter(pl.col("País de nacimiento").is_in(["Total", "España", "Extranjera", "No consta"]))
      .select(anio=year_of("Periodo"), grupo="País de nacimiento", valor="valor").pivot(on="grupo", index="anio", values="valor"))
deaths_group = (
    dn.select("anio", defunciones="Total", def_nacionalidad_espanola="Española", def_nacionalidad_extranjera="Extranjera",
              def_nacionalidad_no_consta="No consta")
    .join(db.select("anio", def_nacidos_espana="España", def_nacidos_extranjero="Extranjera",
                    def_nacimiento_no_consta="No consta"), on="anio")
    .sort("anio")
)

# ── 4. Tasas por mil del INE (contexto largo) ─────────────────────────────────────────────────
rates = (
    read("5224").filter(pl.col("Totales Territoriales") == "Total Nacional").select(anio=year_of("Periodo"), crecimiento_por_mil="valor")
    .join(read("1416").filter(pl.col("Totales Territoriales") == "Total Nacional")
          .select(anio=year_of("Periodo"), saldo_vegetativo_por_mil="valor"), on="anio")
    .with_columns(saldo_migratorio_implicito_por_mil=pl.col("crecimiento_por_mil") - pl.col("saldo_vegetativo_por_mil"))
    .sort("anio")
)

# ── 5. Comprobaciones que se muestran en la entrada ───────────────────────────────────────────
fen = read("6566").filter(pl.col("Operación") == "MNP Estadística de Nacimientos",
                          pl.col("Conceptos Demográficos") == "Crecimiento vegetativo")
fen = fen.select(anio=year_of("Periodo"), crecimiento_vegetativo_ine="valor")
mig_2021 = pl.DataFrame({"anio": [first_new],
                         "saldo_migratorio_antigua": mig_old.filter(pl.col("anio") == first_new)["saldo_migratorio"],
                         "saldo_migratorio_nueva": mig_new.filter(pl.col("anio") == first_new)["saldo_migratorio"]})
checks = (
    natural.select("anio", "saldo_natural")
    .join(fen, on="anio", how="left")
    .join(births_emn.select("anio", nacimientos_emn="valor"), on="anio", how="left")
    .join(deaths_edes.select("anio", defunciones_edes="valor"), on="anio", how="left")
    .join(births_mnp.select("anio", nacimientos_mnp="valor"), on="anio", how="left")
    .join(deaths_mnp.select("anio", defunciones_mnp="valor"), on="anio", how="left")
    .join(check_stocks, on="anio", how="left")
    .join(mig_2021, on="anio", how="left")
    .sort("anio")
)
# El saldo natural calculado debe coincidir con el publicado por el INE
diff = checks.drop_nulls("crecimiento_vegetativo_ine").select((pl.col("saldo_natural") - pl.col("crecimiento_vegetativo_ine")).abs().max()).item()
assert diff <= 5, f"El saldo natural calculado difiere del publicado por el INE en {diff}"

for name, df in [("p01_stocks", stocks), ("p01_components", components), ("p01_births_mother", births_mother),
                 ("p01_deaths_group", deaths_group), ("p01_rates", rates), ("p01_checks", checks)]:
    write_processed(df, TOPIC, name)
print("Hecho.")
