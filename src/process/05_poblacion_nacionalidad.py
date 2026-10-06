"""
Paso 5 del procesamiento: población residente por nacionalidad y país de
nacimiento (INE), serie nacional.

Usado por: posts/i01-population-nationality

Entradas (data/raw/ine_poblacion/): tablas descargadas con
    src/download/download_ine_poblacion.py

Salidas previstas (data/processed/) — TODO: ajustar tras ver los datos en el notebook:
    poblacion_nacionalidad.parquet
        fecha        fecha de referencia (1 de enero / 1 de julio / trimestre)
        grupo        "Española" | "Extranjera" (o grupos de países: UE, resto de Europa, África...)
        poblacion    entero
    poblacion_pais_nacimiento.parquet
        fecha
        grupo        "España" | "Extranjero" (o por continente / país)
        poblacion    entero

Mantener el script sencillo: leer raw -> renombrar -> tipos -> filtrar totales -> comprobar -> guardar.
La exploración va en notebooks/i01-population-nationality.ipynb.

Ejecutar desde la raíz del proyecto:
    python src/process/05_poblacion_nacionalidad.py
"""

import sys
from pathlib import Path

import polars as pl

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/processed")

# TODO 1: leer las tablas de RAW / "ine_poblacion"
# TODO 2: ordenar a formato largo (fecha, grupo, poblacion)
# TODO 3: comprobaciones: española + extranjera = total; nacidos en España + fuera = total
# TODO 4: guardar en OUT

raise SystemExit("TODO: implementar src/process/05_poblacion_nacionalidad.py")
