# data/

```
raw/<source>/<name>_<YYYY-MM-DD>.<ext>   descargas originales: no se editan nunca, la fecha es la de descarga
processed/<name>.parquet                  tablas limpias, las generan los scripts de src/processing/
```

Si un fichero se descarga a mano, se guarda igual: `raw/<source>/<name>_<fecha>.<ext>`.

## Catálogo

| Tabla procesada | Origen (raw) | Script | Post |
|:--|:--|:--|:--|
| `population_nationality` | `raw/ine/` (TODO: tabla) | `src/processing/population.py` | 001 |
| `population_birth_country` | `raw/ine/` (TODO: tabla) | `src/processing/population.py` | 001 |

## Fuentes

| Source | Organismo | Enlace | Notas |
|:--|:--|:--|:--|
| `ine` | Instituto Nacional de Estadística | https://www.ine.es | API JSON: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/<id>` |
