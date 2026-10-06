"""
Paso 4 del procesamiento: viviendas turísticas por municipio (INE, estadística
experimental de viviendas turísticas, 13 oleadas: ago-2020 a may-2026).

Usado por: posts/v01-tourist-housing

Entradas (data/raw/viviendas_turisticas/):
    t39363_viv_tur_municipios.csv    viviendas turísticas, plazas y plazas por vivienda
    t39366_pct_viv_tur_municipios.csv  % de viviendas turísticas sobre viviendas censadas
    (más adelante, para el detalle por barrios: tabla5_secciones/tabla5_<OLEADA>.xlsx)

Salida (data/processed/):
    viviendas_turisticas_municipios.parquet
        Una fila por municipio y oleada. Columnas previstas:
        cod_mun        texto (5)   código INE, de "28079 Madrid" -> "28079"
        periodo        texto       "2026M05" (o fecha: 2026-05-01)
        viv_turisticas entero      viviendas turísticas
        plazas         entero
        plazas_por_viv real
        pct_viv_tur    real        % sobre viviendas censadas
        motivo_sin_dato texto      p. ej. "secreto_estadistico" cuando la fuente da ".."

Formato de los CSV (comprobado):
    - UTF-8 con BOM, separador ";", fin de línea CRLF.
    - Números con punto de miles y coma decimal ("10.836", "0,71").
    - ".." = dato no publicado (municipios con muy pocas viviendas turísticas).
    - Las filas mezclan niveles: Total Nacional, CCAA, provincia y municipio.
      Las municipales son las que tienen la 4.ª columna ("Municipios") rellena.
    - t39363 viene en formato largo con la variable en la columna "Viviendas y plazas":
      hay que pivotar (Viviendas turísticas / Plazas / Plazas por vivienda turística).

Decisiones a tomar (en el notebook antes de escribir este script):
    - ¿Qué hacer con ".."? (nulo con motivo, no cero)
    - Salto de serie en ago y nov de 2024: el INE revisó para incluir las VUT de Andalucía.
    - Las oleadas cambian de mes (feb/ago hasta 2024, may/nov desde nov-2024).

Comprobaciones a incluir al final:
    - Sin duplicados municipio-oleada.
    - Todos los cod_mun existen en data/processed/municipios.parquet (o se listan los que no).
    - La suma municipal de viviendas turísticas coincide (o casi) con el total nacional de cada oleada.

Ejecutar desde la raíz del proyecto:
    python src/process/04_viviendas_turisticas.py
"""

import sys
from pathlib import Path

import polars as pl

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/processed")
VT = RAW / "viviendas_turisticas"

# TODO 1: leer t39363 y quedarse con las filas municipales
# TODO 2: separar cod_mun del nombre, convertir números, pivotar la variable
# TODO 3: leer t39366 y unir el porcentaje
# TODO 4: comprobaciones
# TODO 5: guardar OUT / "viviendas_turisticas_municipios.parquet"

raise SystemExit("TODO: implementar src/process/04_viviendas_turisticas.py")
