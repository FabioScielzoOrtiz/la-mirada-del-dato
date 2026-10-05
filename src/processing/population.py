"""Processing: raw INE population tables -> tidy tables in data/processed/.

Used by: posts/001-spain-population-nationality

Run from the project root (after the download step):
    python -m src.processing.population

Target output (TODO: adjust once you have seen the raw data in the notebook)
---------------------------------------------------------------------------
data/processed/population_nationality.parquet
    date         Date     reference date (1 Jan / 1 Jul / quarter)
    group        str      "Española" | "Extranjera" (nationality)  -- or finer groups (UE, resto de Europa, África...)
    population   int

data/processed/population_birth_country.parquet
    date         Date
    group        str      "España" | "Extranjero" (country of birth) -- or by continent / country
    population   int

Keep this script boring: read raw -> rename columns -> fix types -> filter totals -> save.
Exploration and checks go in notebooks/001-spain-population-nationality.ipynb; when a step is
settled there, move it here.
"""

import polars as pl

from src.utils.files import latest_raw, write_processed


def read_ine_json(path) -> pl.DataFrame:
    """INE DATOS_TABLA JSON -> long table (series name, period, value).

    TODO: check the structure of the downloaded file. Each element is a series with
    'Nombre' (series label) and 'Data' (list of {'Fecha', 'Anyo', 'Valor', ...}).
    """
    raise NotImplementedError


def main() -> None:
    # TODO
    # raw = read_ine_json(latest_raw("ine", "ecp_nationality"))
    # tidy = (raw ... )
    # write_processed(tidy, "population_nationality")
    raise SystemExit("TODO: implement src/processing/population.py")


if __name__ == "__main__":
    main()
