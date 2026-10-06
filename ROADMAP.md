# Roadmap

*Última actualización: 6 de octubre de 2026*

**La Mirada del Dato** reúne investigaciones breves sobre cuestiones sociales con gran debate público. No son artículos académicos: cada entrada contrasta con datos abiertos y evidencia las tesis enfrentadas sobre una pregunta concreta, dice hacia dónde apunta la evidencia y con qué incertidumbre, y se publica en pocas semanas. Si una serie da para más, puede acabar en un artículo académico, pero eso no es el objetivo.

## Principios

1. **Tesis enfrentadas.** Cada pregunta se formula como un contraste entre tesis rivales (habitualmente, las de distintos partidos o colectivos), escritas en una frase neutra. El objetivo no es tomar partido, sino arbitrar: qué tesis encaja mejor con los datos, dónde y con qué incertidumbre.
2. **Simetría.** Cada tesis se mide con la misma calidad de datos. Si una carece de datos comparables, se dice como limitación en vez de darla por refutada.
3. **Sin inferencia causal salvo que el diseño lo permita.** Con datos agregados se miden asociaciones, magnitudes y su heterogeneidad. Lenguaje preciso («asociado a», «compatible con»), con especial cuidado en inmigración, donde una correlación ecológica puede malinterpretarse en cualquier dirección.
4. **La respuesta puede depender del territorio.** Cuando aplica, se muestra la heterogeneidad (por tamaño de municipio, comunidad o tipo de mercado de vivienda): una tesis puede ser cierta en la costa turística y falsa en una ciudad mediana.
5. **Posición de los partidos, cuando procede.** En las cuestiones de debate electoral, la entrada recoge qué proponen y qué han hecho PP, PSOE, Vox y Sumar/Frente Amplio, con fuentes primarias (programa, votaciones, acción de gobierno, declaraciones).
6. **De menos a más.** Primero lo descriptivo y con los datos ya disponibles; los análisis complejos, cuando la base de datos esté madura.

## Series y entradas

**Identificadores:** `<serie><nn>-<slug>`, el mismo en `posts/` y en `notebooks/` (por ejemplo, `posts/v01-tourist-housing/` y `notebooks/v01-tourist-housing.ipynb`).
**Datos:** ✔ ya en `data/raw/` · ⬇ falta descargar.
**Dificultad:** ★ descriptivo con datos directos · ★★ cruzar fuentes o cuidar definiciones · ★★★ problemas de medición serios, muchas fuentes o tentación causal.
**29-N:** cuestión central de la campaña de las generales del 29 de noviembre de 2026 (categoría «Elecciones 29-N» y sección de partidos).

### v · Vivienda

Serie principal. Recoge las preguntas del proyecto de investigación sobre vivienda (RQ0–RQ5). Los datos se descargan y procesan pregunta a pregunta.

| ID | Pregunta | Tesis A | Tesis B | Datos | Dif. | 29-N |
|:--|:--|:--|:--|:--|:-:|:-:|
| v01 | ¿Qué peso tienen los pisos turísticos: son marginales o están concentrados? | Son marginales (en torno al 1–1,5 % del parque) y no explican el problema | Concentrados en ciertas zonas, allí sí pesan y presionan | ⬇ INE viviendas turísticas (municipio, sección, 2020–2026); ⬇ Censo 2021 | ★ | ✓ |
| v02 | ¿Es hoy más difícil pagar el alquiler? Alquiler frente a renta de los hogares | El problema es de precios desbocados | El problema es sobre todo de rentas que no siguen el ritmo | ⬇ SERPAVI (2011–2024); ⬇ ADRH (renta, 2015–2023); ⬇ AEAT | ★★ | ✓ |
| v03 | ¿Falta vivienda o sobra vivienda vacía? | El problema es de oferta: hay que construir más | Hay vivienda de sobra, vacía o infrautilizada: el problema es de uso y distribución | ⬇ Censo 2021 (vacías por consumo eléctrico); ⬇ Censo 2011; ⬇ AEAT (viviendas a disposición); ⬇ iniciadas y terminadas; ⬇ Padrón | ★★ | ✓ |
| v04 | ¿Han bajado los alquileres donde se han aplicado topes? ¿Y la oferta? | Los topes contienen los precios | Los topes reducen la oferta y desplazan el mercado | ⬇ zonas tensionadas (BOE); ⬇ SERPAVI; análisis previo de Cataluña en `_archive/` | ★★★ | ✓ |
| v05 | ¿Se declaran las zonas tensionadas donde hay tensión? | La ley se aplica con criterio político e intervencionista | Algunas CCAA bloquean su aplicación por motivos políticos aunque tengan municipios tensionados | ⬇ BOE (2024 T1 – 2026 T2); ⬇ SERPAVI; ⬇ ADRH (criterio de esfuerzo > 30 %) | ★★★ | ✓ |
| v06 | ¿Qué relación hay entre inmigración y presión sobre la vivienda? | La inmigración aumenta la demanda y encarece la vivienda | Los precios responden sobre todo a turismo, inversión y oferta; los inmigrantes soportan más el problema que lo causan | ⬇ Padrón; ⬇ Censo Anual (nacionalidad, año de llegada); ⬇ ADRH; ⬇ SERPAVI; ⬇ compradores extranjeros (provincia) | ★★★ | ✓ |
| v07 | ¿Pequeños propietarios o grandes tenedores? | El alquiler está en manos de particulares; los fondos son marginales | Rentistas con varias viviendas, grandes tenedores y fondos concentran el mercado | ⬇ AEAT (por ubicación del declarante); ⬇ Censo 2021 (tenencia). Sin datos abiertos de personas jurídicas: el residuo es una cota, no una medida | ★★★ | ✓ |
| v08 | ¿Cuánto ha crecido la okupación y qué peso tiene sobre el parque? | Es un problema extendido | Es marginal y se magnifica | ⬇ Interior: Balance de Criminalidad; ⬇ Censo 2021 | ★★ | ✓ |
| v09 | ¿Qué tipos de mercado de vivienda hay en España y dónde? | — (entrada metodológica: base para mostrar la heterogeneidad en las demás) | — | Tabla municipal analítica; clustering robusto de datos mixtos (G-Gower + k-medoides, `db-robust-clust`) | ★★★ | |

### i · Inmigración

| ID | Pregunta | Tesis A | Tesis B | Datos | Dif. | 29-N |
|:--|:--|:--|:--|:--|:-:|:-:|
| i01 | ¿Cuánto ha crecido la población y qué parte se debe a la inmigración? | — (base factual común del debate) | — | ✔ INE: ECP 56938 (nacional, 2002–2025), 60129 y 60130 (provincial, 2021–); CP 9691 (provincial, 2002–2022) | ★ | ✓ |
| i02 | ¿Qué aportan los inmigrantes al empleo y a la Seguridad Social? | Sostienen el empleo y las pensiones | Su aportación es menor de lo que se dice (empleos de bajo salario, cotizaciones bajas) | ⬇ afiliación por nacionalidad; EPA; EES | ★★ | ✓ |
| i03 | ¿Qué parte de las ayudas reciben los extranjeros, comparada con su peso en la población y en la población en riesgo de pobreza? | Acaparan las ayudas; hay que priorizar a los nacionales | Reciben en proporción a su situación de necesidad | ⬇ IMV y prestaciones por nacionalidad; INE: ECV; ⬇ ADRH (población bajo umbrales de renta por nacionalidad) | ★★ | ✓ |
| i04 | ¿Delinquen más los extranjeros? ¿Cuánto cambia al comparar por edad, sexo y tipo de delito? | La inmigración aumenta la delincuencia | La sobrerrepresentación se explica sobre todo por la composición demográfica y socioeconómica | ⬇ INE: Estadística de Condenados; Interior; ECP | ★★★ | ✓ |

Cuidados específicos en i03 e i04: comparar con el denominador correcto (población que cumple requisitos o en riesgo de pobreza; población de la misma edad y sexo); condenados ≠ detenidos ≠ delitos; extranjeros no residentes en el numerador pero no en el denominador; nacionalidad ≠ origen; dar las cifras completas y hablar de tasas, no de casos.

### e · Economía, empleo y salarios

| ID | Pregunta | Tesis A | Tesis B | Datos | Dif. | 29-N |
|:--|:--|:--|:--|:--|:-:|:-:|
| e01 | ¿Llega el crecimiento económico a los hogares? | España es la economía que más crece de Europa | El crecimiento se debe a la población y no llega al bolsillo | ⬇ INE: Contabilidad Nacional; Eurostat | ★★ | ✓ |
| e02 | ¿Han subido los salarios reales? ¿Qué ha pasado con el empleo tras las subidas del SMI? | El SMI mejora los salarios bajos sin destruir empleo | Frena el empleo de los menos cualificados | ⬇ INE: EES, IPC; EPA | ★★★ | ✓ |
| e03 | ¿Ha reducido la reforma laboral la temporalidad o ha cambiado la forma de medir el paro? | Ha creado empleo estable | Los fijos discontinuos maquillan el paro | ⬇ EPA; afiliación por contrato; SEPE | ★★ | ✓ |

### s · Estado del bienestar y cuentas públicas

| ID | Pregunta | Tesis A | Tesis B | Datos | Dif. | 29-N |
|:--|:--|:--|:--|:--|:-:|:-:|
| s01 | ¿Pagamos más impuestos que en Europa? ¿Ha subido la recaudación por no deflactar el IRPF? | Hay margen para subir impuestos | La recaudación récord es una subida encubierta por la inflación | ⬇ Eurostat; AEAT | ★★ | ✓ |
| s02 | ¿Son sostenibles las pensiones? | Las pensiones están garantizadas | El sistema traslada el coste a los jóvenes | ⬇ Seguridad Social; AIReF; Eurostat | ★★ | ✓ |
| s03 | ¿Han empeorado las listas de espera sanitarias? | Deterioro por falta de financiación | Deterioro por gestión autonómica | ⬇ Ministerio de Sanidad: SISLE | ★★ | |
| s04 | ¿Cómo han evolucionado la deuda y el déficit? | Las cuentas se han saneado | La deuda sigue en máximos | ⬇ Banco de España; IGAE; Eurostat | ★ | |

## Calendario hasta el 29-N

De menos a más dificultad. Lo que no llegue antes del 29-N se publica después: el blog no termina con las elecciones.

| Semana | Fechas | Entradas |
|:-:|:--|:--|
| 1 | 6–12 oct | Reorganización del blog. **i01** (población e inmigración) |
| 2 | 13–19 oct | **v01** (pisos turísticos) |
| 3 | 20–26 oct | **v02** (alquiler frente a renta) |
| 4 | 27 oct–2 nov | **v03** (vacías o escasez), i02 |
| 5 | 3–9 nov | i03, e01 |
| 6 | 10–16 nov | i04, s01 · empieza la campaña (13 nov) |
| 7 | 17–23 nov | s02 y una entrada resumen con todas las respuestas |
| — | 29 nov | Elecciones |
| después | | v04–v07 y v09 (★★★), e02, e03, s03, s04, v08 |

## Datos

Cada entrada descarga y procesa solo lo que necesita, con scripts genéricos por fuente (`src/download/`, `src/process/`) documentados en `data/raw/README.md` y `data/processed/README.md`. Clave territorial común cuando aplique: código INE (provincia de 2 dígitos, municipio de 5), como texto.

| Paso | Script | Estado |
|:--|:--|:--|
| Población por nacionalidad y lugar de nacimiento (i01) | `src/download/download_ine_poblacion.py` → `src/process/01_poblacion_nacionalidad.py` | descargado; procesado por escribir |

## Líneas futuras

- Si la serie de vivienda madura, el material puede dar para un artículo académico (tipología de mercados, RQ0–RQ5) y para el artículo metodológico sobre G-Gower y k-medoides con faltantes estructurados.
- Otros usos de la base municipal: segregación residencial, despoblación, asentamiento de la inmigración.
