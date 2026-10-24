# La Mirada del Dato

Análisis breves con datos públicos sobre los grandes debates de España. Web: [lamiradadeldato.com](https://lamiradadeldato.com).

## Estructura

```
index.qmd temas.qmd method.qmd about.qmd   páginas del sitio
common/                  código compartido (rutas, estilo de gráficos, descarga de ficheros)
_template/               plantillas (no se publican): article.ipynb y topic/
<tema>/                  cada tema es un mini-proyecto (poblacion/, vivienda/…)
  index.qmd              página del tema: lista sus análisis
  notebooks/             cada análisis ES su notebook (se publica tal cual)
  src/{download,process}/  código propio del tema
  data/{raw,processed}/    datos del tema (no versionados)
  research_questions/    preguntas y plan de análisis fijados antes de analizar (opcional)
```

## Flujo de trabajo

**Nuevo tema:** copia `_template/topic/` como `<tema>/`, edita su `index.qmd` y añádelo a `temas.qmd`.

**Nuevo análisis:**
1. Copia `_template/article.ipynb` a `<tema>/notebooks/<id>-<slug>.ipynb` (ids: `i` población, `v` vivienda…).
2. Escribe las preguntas y el plan de análisis **antes** de analizar.
3. Descarga y procesa con scripts en `<tema>/src/`; el notebook lee de `<tema>/data/processed/`.
4. Ejecuta el notebook entero y guárdalo **con las salidas**: Quarto publica un notebook con las salidas que lleva guardadas, no lo re-ejecuta.
5. Quita `draft: true` y la etiqueta «Próximamente» de la cabecera (primera celda *raw*), y haz commit.

## Entorno

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
quarto preview
```
