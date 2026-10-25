"""Procesamiento de la tabla 56938 del INE (ECP): población residente por fecha, sexo, edad,
nacionalidad y país de nacimiento.

Usado por: poblacion/notebooks/p01-population-nationality-origin.ipynb

Lee el CSV más reciente de poblacion/data/raw/ine_poblacion/, lo limpia, valida y guarda:
    poblacion/data/processed/poblacion_nacionalidad_origen.parquet
El parquet solo se escribe si pasan todas las comprobaciones de calidad.

Ejecutar desde cualquier carpeta del proyecto:
    python poblacion/src/process/process_ine_population.py
"""

import sys
from pathlib import Path

import polars as pl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))

from common.files import latest_raw, write_processed
from common.paths import topic_dir

TABLE = "56938"
OUTPUT_NAME = "poblacion_nacionalidad_origen"
VALOR = "total"      # columna con la población
TOL = 5              # diferencia máxima admitida en las comprobaciones de suma (redondeo del INE; observado: 2)

COL_NAMES_MAP = {
    "edad simple": "edad",
    "país de nacimiento": "pais_nacimiento",
}

MESES = {"enero": "01", "abril": "04", "julio": "07", "octubre": "10"}   # los únicos que aparecen en esta tabla

MAP_NAC = {
    "Total": "Total", "Española": "Española", "Extranjera": "Extranjera", "Apátridas": "Apátridas",
    # Europa: UE28 hasta 2020 y UE27 desde 2020 (dos clasificaciones que no coinciden en ninguna fecha)
    "País de la UE28 sin España": "Europa", "País de Europa menos UE28": "Europa",
    "País de la UE27_2020 sin España": "Europa", "País de Europa menos UE27_2020": "Europa",
    "De Africa": "África", "De América del Norte": "América del Norte",
    "De Centro América y Caribe": "América Central y Caribe", "De Sudamérica": "Sudamérica",
    "De Asia": "Asia", "De Oceanía": "Oceanía",
}

MAP_PAIS = {
    "Total": "Total", "España": "España", "Extranjero": "Extranjero",
    # Europa: UE28 hasta 2020 y UE27 desde 2020
    "UE28 sin España": "Europa", "Europa menos UE28": "Europa",
    "UE27_2020 sin España": "Europa", "Europa menos UE27_2020": "Europa",
    "África": "África", "América del Norte": "América del Norte",
    "Centro América y Caribe": "América Central y Caribe",   # mismo nombre que en nacionalidad
    "Sudamérica": "Sudamérica", "Asia": "Asia", "Oceanía": "Oceanía",
}

REGIONES_NAC = ["África", "América Central y Caribe", "América del Norte", "Apátridas",
                "Asia", "Europa", "Oceanía", "Sudamérica"]
REGIONES_PAIS = ["África", "América Central y Caribe", "América del Norte",
                 "Asia", "Europa", "Oceanía", "Sudamérica"]


def procesar(df: pl.DataFrame) -> pl.DataFrame:
    # Renombrar columnas
    df = df.rename({col: col.lower() for col in df.columns}).rename(COL_NAMES_MAP)

    # periodo: str a date, y nos quedamos solo con el 1 de enero (antes de nada: reduce ~75 % las filas)
    df = df.with_columns(
        periodo=pl.col("periodo").str.replace_many(MESES).str.to_date("%d de %m de %Y")
    ).filter(pl.col("periodo").dt.month() == 1)

    # edad: de string a numérica (conserva el texto, que se usa para filtrar "Todas las edades")
    df = df.with_columns(edad_num=pl.col("edad").str.extract(r"^(\d+)").cast(pl.Int64))

    # total: str a numérica ("1.234" -> 1234; ".." -> null)
    df = df.with_columns(
        total=pl.col("total").str.replace_all(".", "", literal=True).cast(pl.Int64, strict=False)
    )
    # Los nulos se miran ANTES de agrupar: la suma de un grupo todo-null da 0 en Polars y los ocultaría
    print(f"Nulos en '{VALOR}' (de '..') antes de agrupar: {df[VALOR].null_count()}")

    # nacionalidad y pais_nacimiento: agrupación y formateo
    df = df.with_columns(
        nacionalidad=pl.col("nacionalidad").replace_strict(MAP_NAC),
        pais_nacimiento=pl.col("pais_nacimiento").replace_strict(MAP_PAIS),
    )

    # Un único group_by para unir las filas de Europa (UE28 / UE27)
    claves = [c for c in df.columns if c != VALOR]
    return df.group_by(claves).agg(pl.col(VALOR).sum()).sort(claves)


def check_suma(d: pl.DataFrame, col: str, partes: list[str], total: str) -> pl.DataFrame:
    """Diferencia por periodo entre la suma de `partes` y la categoría `total`."""
    return (d.pivot(on=col, index="periodo", values=VALOR)
        .with_columns(dif=pl.sum_horizontal(partes) - pl.col(total))
        .select("periodo", "dif").sort("periodo"))


def validar(df: pl.DataFrame) -> None:
    base = df.filter(pl.col("sexo") == "Total", pl.col("edad") == "Todas las edades")
    base_nac = base.filter(pl.col("pais_nacimiento") == "Total")      # series por nacionalidad
    base_pais = base.filter(pl.col("nacionalidad") == "Total")        # series por país de nacimiento

    # una fila por periodo y categoría
    assert base_nac.group_by("periodo", "nacionalidad").len()["len"].unique().to_list() == [1]
    assert base_pais.group_by("periodo", "pais_nacimiento").len()["len"].unique().to_list() == [1]

    # 24 periodos (1 de enero de 2002 a 2025)
    n_periodos = base["periodo"].n_unique()
    print(f"Periodos: {n_periodos}")
    assert n_periodos == 24, "Faltan periodos (se esperaban 24: 1-I-2002 a 1-I-2025)"

    checks = {
        "Española + Extranjera = Total": (base_nac, "nacionalidad", ["Española", "Extranjera"], "Total"),
        "Regiones de nacionalidad (con Apátridas) = Extranjera": (base_nac, "nacionalidad", REGIONES_NAC, "Extranjera"),
        "España + Extranjero = Total": (base_pais, "pais_nacimiento", ["España", "Extranjero"], "Total"),
        "Regiones de nacimiento = Extranjero": (base_pais, "pais_nacimiento", REGIONES_PAIS, "Extranjero"),
    }
    for nombre, (d, col, partes, total) in checks.items():
        dif_max = check_suma(d, col, partes, total)["dif"].abs().max()
        print(f"{nombre}: diferencia máx. = {dif_max}")
        assert dif_max <= TOL, f"Falla la comprobación '{nombre}' (diferencia máx. {dif_max} > {TOL})"

    # Variación anual del total: sin umbral, para juzgar a ojo (sobre todo 2020–2021)
    print("\nVariación anual del total:")
    with pl.Config(tbl_rows=30):
        print(base_nac.filter(pl.col("nacionalidad") == "Total").sort("periodo")
              .select("periodo", VALOR,
                      var_abs=pl.col(VALOR).diff(),
                      var_pct=(100 * pl.col(VALOR).pct_change()).round(2)))


def main() -> None:
    topic = topic_dir(__file__)
    raw_path = latest_raw(topic, source="ine_poblacion", name=TABLE)
    print(f"Leyendo {raw_path.relative_to(topic)}")

    df = procesar(pl.read_csv(raw_path, separator=";"))
    validar(df)
    write_processed(df, topic, OUTPUT_NAME)


if __name__ == "__main__":
    main()