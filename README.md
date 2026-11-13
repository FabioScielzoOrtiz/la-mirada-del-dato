# La Mirada del Dato

Estadística aplicada a problemas sociales, explicada paso a paso. Web: [lamiradadeldato.com](https://lamiradadeldato.com).

Es una extensión aplicada de mi docencia: cada técnica que usa una entrada está explicada en mis materiales de estadística y la entrada los cita.

## Estructura

```
index.qmd temas.qmd method.qmd about.qmd   páginas del sitio
_variables.yml           registro de materiales docentes que citan las entradas
common/                  código compartido (rutas, estilo de gráficos, descarga de ficheros)
_template/               plantillas (no se publican): article.ipynb y topic/
<tema>/                  cada tema es un mini-proyecto (poblacion/, gasto-publico/, vivienda/, seguridad/, historia/)
  index.qmd              página del tema: lista sus entradas
  notebooks/             un notebook por entrada: el archivo maestro (la web muestra solo una parte)
  src/{download,process}/  código propio del tema   ┐ se crean al empezar
  data/{raw,processed}/    datos (no versionados)   ┘ la primera entrada del tema
  research_questions/    preguntas de investigación del tema (opcional)
```

## Flujo de trabajo

**Nuevo tema:** copia `_template/topic/` como `<tema>/`, edita su `index.qmd` y añádelo a `temas.qmd`. Las entradas previstas se anuncian con notebooks mínimos (pregunta y «Próximamente»); la página del tema las lista por nombre de fichero, en el orden de la serie.

**Nueva entrada:**
1. Copia `_template/article.ipynb` a `<tema>/notebooks/<id>-<slug>.ipynb` (ids: `p` población, `g` gasto público, `v` vivienda, `seg` seguridad, `h` historia).
2. Descarga y procesa con scripts en `<tema>/src/`; el notebook lee de `<tema>/data/processed/`.
3. Cita cada técnica con `{{< var materiales.<id> >}}`. Si no está en `_variables.yml`, primero se añade a los materiales docentes y después al registro.
4. Ejecuta el notebook entero y guárdalo **con las salidas**: Quarto publica las salidas guardadas, no lo re-ejecuta.
   Lo que no es para el lector se oculta en el propio notebook: `#| include: false` en celdas de código y una «zona de trabajo» entre `::: {.content-hidden}` y `:::` (instrucciones en la plantilla). Oculto no es privado: el repositorio es público.
5. Quita `draft: true` y la etiqueta «Próximamente» de la cabecera (primera celda *raw*), y haz commit.

**Publicar un material docente:** cambia su línea en `_variables.yml` por un enlace; todas las entradas que lo citan se actualizan.

## Entorno

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
quarto preview
```
