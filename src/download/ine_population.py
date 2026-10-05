"""Download: resident population of Spain by nationality and country of birth (INE).

Used by: posts/001-spain-population-nationality

Run from the project root:
    python -m src.download.ine_population

Output: data/raw/ine/<name>_<YYYY-MM-DD>.json  (one file per table, never overwritten)

Candidate INE sources (TODO: pick the tables in INEbase and fill TABLES below)
-----------------------------------------------------------------------------
1. Estadística Continua de Población (ECP), quarterly, 2021 onwards.
   Population by nationality (Spanish / foreign, groups of countries) and by country of birth.
2. Cifras de Población (CP), half-yearly series 1971–2021 (nationality and country of birth from 2002).
   Useful to extend the series backwards. Check that the definitions match the ECP.
3. Estadística del Padrón Continuo, 1 January each year since 1998. Municipal detail; not the official
   population figure, but the longest series by nationality and country of birth.

How to find a table id: open the table in INEbase, "Descargar" → "API JSON" (or look at the URL, t=XXXXX).
The JSON API returns every series of the table:
    https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/<table_id>?nult=<n_periods>
(without ?nult it returns the whole history; check the API docs: https://www.ine.es/dyngs/DAB/index.htm?cid=1099)

Alternative: download the CSV by hand from INEbase and save it as data/raw/ine/<name>_<YYYY-MM-DD>.csv.
"""

from src.utils.files import download

# TODO: fill with the INE table ids you choose. Name -> table id.
TABLES: dict[str, str] = {
    # "ecp_nationality": "XXXXX",
    # "ecp_birth_country": "XXXXX",
}

API = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{table_id}"


def main() -> None:
    if not TABLES:
        raise SystemExit("TODO: add INE table ids to TABLES in src/download/ine_population.py")
    for name, table_id in TABLES.items():
        download(API.format(table_id=table_id), source="ine", name=name, ext="json")


if __name__ == "__main__":
    main()
