# La Mirada del Dato

Blog de verificación de datos: afirmaciones del debate público, contrastadas con datos abiertos y estadística. Entradas cortas, sin adjetivos, con el código y los datos a la vista.

Web: <https://fabioscielzoortiz.github.io/la-mirada-del-dato> · Afirmaciones pendientes: [ROADMAP.md](ROADMAP.md)

## Estructura

```
la-mirada-del-dato/
├── _quarto.yml            configuración del sitio
├── index.qmd              portada (tabla de preguntas)
├── method.qmd             método y escala de respuestas
├── about.qmd              sobre el blog
├── references.bib         bibliografía común
├── requirements.txt       dependencias de Python
├── ROADMAP.md             afirmaciones a contrastar
│
├── posts/                 una carpeta por entrada: NNN-short-slug/index.qmd
│   ├── _metadata.yml      valores comunes (autor, licencia, bibliografía)
│   └── _template/         plantilla (no se publica)
├── notebooks/             trabajo exploratorio: NNN-short-slug.ipynb ↔ posts/NNN-short-slug/
│
├── src/                   código reutilizable, se ejecuta como scripts (no es un paquete instalable)
│   ├── download/          descarga datos → data/raw/
│   ├── processing/        data/raw/ → data/processed/
│   ├── analysis/          indicadores usados en varias entradas
│   └── utils/             rutas, lectura/escritura, estilo de gráficos
├── data/
│   ├── raw/               descargas originales, nunca se editan (fecha en el nombre)
│   └── processed/         tablas limpias en Parquet
│
├── assets/                estilos (base, light, dark) y CSL de citas
├── images/                logo
└── _freeze/               resultados ejecutados de cada post (lo genera Quarto; se sube al repo)
```

## Puesta en marcha

Requisitos: Python ≥ 3.11 y [Quarto](https://quarto.org/docs/get-started/).

```bash
python -m venv .venv
.venv\Scripts\activate               # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m ipykernel install --user --name la-mirada-del-dato   # opcional: kernel con nombre para Jupyter/VS Code

quarto preview                       # con el venv activado, para que Quarto use su Python
```

Todos los comandos se lanzan **desde la raíz del proyecto**.

## Flujo de una entrada

Cada entrada tiene un identificador `NNN-short-slug` que se repite en el notebook y en la carpeta del post.

| Paso | Dónde | Qué |
|:--|:--|:--|
| 1. Pregunta | `ROADMAP.md` | Elegir la afirmación y escribir la pregunta contrastable. |
| 2. Descarga | `src/download/<fuente>_<tema>.py` | `python -m src.download.<módulo>` → `data/raw/<fuente>/<nombre>_<fecha>.<ext>`. O descarga manual con el mismo nombre. |
| 3. Exploración | `notebooks/NNN-short-slug.ipynb` | Mirar los datos crudos, probar, ensuciar. |
| 4. Procesado | `src/processing/<tema>.py` | Pasar aquí los pasos de limpieza ya decididos. `python -m src.processing.<módulo>` → `data/processed/<nombre>.parquet`. |
| 5. Análisis | `notebooks/NNN-short-slug.ipynb` | Cifras y gráficos finales sobre `data/processed/`. |
| 6. Publicación | `posts/NNN-short-slug/index.qmd` | Copiar solo el código final. Rellenar `respuesta`, `confianza`, `resumen`. Quitar `draft: true`. |

Reglas:

- `data/raw/` no se toca a mano: si hay una versión nueva, se descarga con otra fecha.
- Los posts solo leen `data/processed/`. Nada de limpieza dentro del `.qmd`.
- Los scripts de `src/` son independientes y se pueden volver a lanzar en cualquier momento.
- `src/analysis/` solo recoge lo que ya se ha usado en más de una entrada.
- Los posts con `draft: true` se ven en `quarto preview`, pero no se publican ni salen en la portada.

### Importar `src` desde notebooks y posts

`src` no se instala. La primera celda de cada notebook y post añade la raíz del proyecto al `sys.path`:

```python
import sys
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "_quarto.yml").exists())
sys.path.insert(0, str(ROOT))
```

## Publicación

```bash
quarto render          # ejecuta los posts nuevos o modificados y actualiza _freeze/
git add . && git commit -m "..." && git push
```

GitHub Actions (`.github/workflows/publish.yml`) renderiza el sitio usando `_freeze/` (no necesita volver a ejecutar el código ni los datos) y lo publica en la rama `gh-pages`.

## Estado

| Post | Estado |
|:--|:--|
| 001 · Población por nacionalidad y país de nacimiento | Esqueleto: falta descarga, procesado y análisis |
| 002–006 | Placeholders (ver ROADMAP) |

## Licencia

Contenido CC BY 4.0 · Código MIT.
