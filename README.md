# La Mirada del Dato

Investigaciones breves sobre cuestiones sociales con gran debate público (vivienda, inmigración, empleo, servicios públicos), contrastadas con datos abiertos y estadística. Cada entrada pone frente a frente las tesis enfrentadas y dice hacia dónde apunta la evidencia. Hasta el 29-N, especial elecciones generales.

Web: <https://lamiradadeldato.com> · Preguntas, series y calendario: [ROADMAP.md](ROADMAP.md)

## Estructura

```
la-mirada-del-dato/
├── _quarto.yml              configuración del sitio
├── index.qmd · method.qmd · about.qmd
├── ROADMAP.md               series, preguntas, tesis, datos y calendario
├── requirements.txt         dependencias de Python
├── CNAME                    dominio propio (GitHub Pages)
├── .github/workflows/       publicación automática
│
├── posts/                   una carpeta por entrada: <id>-<slug>/index.qmd
│   ├── _metadata.yml        valores comunes (autor, licencia, bibliografía)
│   └── _template/           plantilla (no se publica)
├── notebooks/               trabajo exploratorio: <id>-<slug>.ipynb  ↔  posts/<id>-<slug>/
│
├── src/                     scripts ejecutables (no es un paquete instalable)
│   ├── download/            descarga en bruto → data/raw/            (download_<fuente>.py)
│   ├── process/             data/raw/ → data/processed/, numerados   (NN_<tabla>.py)
│   ├── analysis/            indicadores reutilizados en varias entradas
│   └── utils/               rutas y estilo de gráficos (para notebooks y posts)
├── data/                    NO se versiona (ver .gitignore)
│   ├── raw/                 descargas originales, nunca se editan · catálogo en data/raw/README.md
│   └── processed/           tablas limpias en Parquet · diccionario en data/processed/README.md
│
├── assets/                  estilos (base, light, dark), plantilla de la portada, CSL
├── images/                  logo
└── _freeze/                 resultados ejecutados de cada post (Quarto; sí se versiona)
```

### Identificadores de las entradas

`<serie><nn>-<slug-en-inglés>`, igual en `posts/` y `notebooks/`:

| Serie | Prefijo | Ejemplo |
|:--|:-:|:--|
| Vivienda | `v` | `v01-tourist-housing` |
| Inmigración | `i` | `i01-population-nationality` |
| Economía, empleo y salarios | `e` | `e01-growth-households` |
| Estado del bienestar y cuentas públicas | `s` | `s01-tax-burden` |

El número identifica la pregunta, no el orden de publicación (eso lo da la fecha).

## Puesta en marcha

Requisitos: Python ≥ 3.11 y [Quarto](https://quarto.org/docs/get-started/).

```bash
python -m venv .venv
.venv\Scripts\activate                      # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
$env:QUARTO_PYTHON = "$PWD\.venv\Scripts\python.exe"   # Windows PowerShell: que Quarto use el Python del venv
quarto preview
```

Todos los scripts se lanzan **desde la raíz del proyecto**:

```bash
python src/download/download_ine_poblacion.py
python src/process/01_poblacion_nacionalidad.py
```

## Flujo de una entrada

| Paso | Dónde | Qué |
|:--|:--|:--|
| 1. Pregunta y tesis | `ROADMAP.md` → `posts/<id>/index.qmd` | Pregunta concreta y tesis enfrentadas en una frase neutra. |
| 2. Partidos (si es tema electoral) | `posts/<id>/index.qmd` | Programa, votaciones, acción de gobierno y declaraciones, con fuentes primarias. |
| 3. Descarga | `src/download/download_<fuente>.py` | → `data/raw/<fuente>/`. Documentar en `data/raw/README.md`. |
| 4. Exploración | `notebooks/<id>.ipynb` | Mirar los datos crudos, probar, decidir. |
| 5. Procesado | `src/process/NN_<tabla>.py` | Pasar aquí la limpieza ya decidida, con comprobaciones. → `data/processed/`. Documentar en `data/processed/README.md`. |
| 6. Análisis | `notebooks/<id>.ipynb` | Cifras y gráficos finales sobre `data/processed/`. |
| 7. Publicación | `posts/<id>/index.qmd` | Solo el código final. Rellenar `respuesta`, `confianza`, `resumen`. Quitar `draft: true`. `quarto render` y *push*. |

Reglas:

- `data/raw/` no se toca a mano. Los posts solo leen `data/processed/`: nada de limpieza dentro del `.qmd`.
- Los scripts de procesado son genéricos (por fuente, no por entrada) y reutilizables: clave territorial común `cod_mun` (código INE de 5 dígitos, texto), medidas de precisión conservadas y motivo de cada dato faltante.
- Los posts con `draft: true` se ven en `quarto preview`, pero no se publican.

### Importar `src` desde notebooks y posts

La primera celda de cada notebook y post añade la raíz del proyecto al `sys.path`:

```python
import sys
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))
from src.utils.paths import RAW, PROCESSED
```

## Publicación

```bash
quarto render          # ejecuta los posts nuevos o modificados y actualiza _freeze/
git add . && git commit -m "..." && git push
```

GitHub Actions renderiza el sitio a partir de `_freeze/` (no necesita los datos, que no se suben) y lo publica en la rama `gh-pages`.

## Estado

| Entrada | Estado |
|:--|:--|
| i01 · Población e inmigración | **En curso.** Datos descargados (`data/raw/ine_poblacion/`); falta procesado, análisis y tabla de partidos |
| v01 · Pisos turísticos | Esqueleto: falta descarga, procesado y análisis |
| Resto | Placeholders con pregunta, tesis y datos candidatos (ver ROADMAP) |

## Licencia

Contenido CC BY 4.0 · Código MIT.
