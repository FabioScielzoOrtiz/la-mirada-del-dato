# p01 · Evolución de la población de España por nacionalidad y país de origen

**Plan de análisis** · redactado el 2026-10-25, antes de rehacer el análisis en el notebook.
Este documento no se publica. Si algo cambia durante el análisis, se anota en «Cambios al plan» (final), con fecha y motivo.

> **Transparencia.** Este plan se escribe tras una exploración preliminar (una versión anterior del notebook, ya archivada en el historial de git). Los periodos de la sección 4 salen de ella.

## 1. Preguntas

- **P1.** ¿Cómo ha evolucionado la población residente en España según su **nacionalidad** (española / extranjera)?
- **P2.** ¿Cómo ha evolucionado según su **país de origen**, entendido como país de nacimiento (nacidos en España / en el extranjero y, dentro de estos, por región)?

Pregunta de apoyo, necesaria para interpretar las dos: ¿cuánto cambia el resultado según se defina «extranjero» por nacionalidad o por lugar de nacimiento (cruce de ambas)?

## 2. Datos

| Tabla INE | Contenido | Uso |
|:--|:--|:--|
| **56938** (ECP) | Población residente por fecha, sexo, edad simple, nacionalidad y país de nacimiento; 2002 – 1-I-2025 | Fuente principal (P1, P2, cruce) |
| **60129 / 60130** (ECP, 2021 –) | Población por provincia y por edad/nacionalidad o país de nacimiento (marginales, sin cruce) | Solo si se necesita llegar a 2026; **empalme pendiente de verificar** |

- Se usa **la población a 1 de enero** (24 puntos, 2002–2025), con sexo = Total y edad = todas las edades.
- Se descarga y procesa con scripts en `poblacion/src/download` y `poblacion/src/process`; los datos crudos no se tocan.
- Definiciones: *población residente* (ECP del INE), *nacionalidad* (española / extranjera, con apátridas dentro de extranjera), *país de nacimiento* (España / extranjero y regiones).

## 3. Decisiones de medición (fijadas ahora)

1. Una sola fecha por año (1 de enero); la serie semestral/trimestral no se usa.
2. Las dos clasificaciones de «Europa» de la tabla (UE28 hasta 2020 y UE27 desde mediados de 2020) se unifican en una sola región Europa, comprobando que las categorías suman el total.
3. Las regiones de nacimiento se agrupan a partir de las que da el INE; la agrupación final se fija antes de mirar gráficos por región y se describe en el artículo.
4. Medidas: población, variación anual (absoluta y %), tasa anual compuesta por periodo, media anual por periodo, peso sobre el total y contribución de cada grupo a la variación total.
5. La variación entre el 1-I de t-1 y el 1-I de t se atribuye al año t.

## 4. Análisis previstos

**P1 · Nacionalidad**
- Serie 2002–2025: población española, extranjera y total; peso de la extranjera.
- Variación anual y por periodos: 2002–2008, 2008–2014, 2014–2019, 2019–2025, y total 2002–2025. Sensibilidad con bloques de 5 años (2002–2007 … 2022–2025).
- Contribución de cada grupo a la variación total en cada periodo (puede ser negativa o superar el 100 % si el otro grupo cae).

**P2 · País de origen**
- Serie nacidos en España / en el extranjero y su peso.
- Desglose de los nacidos en el extranjero por región de nacimiento (evolución y peso).
- Mismas medidas y periodos que en P1.

**Cruce nacionalidad × lugar de nacimiento (cuatro grupos)**
- Españoles nacidos en España / en el extranjero; extranjeros nacidos en España / en el extranjero.
- Qué parte de la diferencia entre ambas definiciones es población con nacionalidad española nacida fuera, y cuál extranjera nacida en España.

**Gráficos** (Plotly): variación anual en barras con la población total en eje secundario; media anual por periodo con la contribución de cada grupo; pesos en el tiempo; comparación nacionalidad vs. nacimiento.

## 5. Explicaciones y marco teórico (a documentar con fuentes)

Apartados a desarrollar en la sección «Explicaciones», citando la literatura y las fuentes oficiales; nada de esto se afirma sin referencia.
- Dinámica demográfica: saldo natural y envejecimiento; relación entre crecimiento poblacional y migración.
- Migración laboral y ciclo económico (atracción por demanda de trabajo; efecto de la crisis de 2008 en retornos y salidas).
- Redes migratorias y composición por origen.
- Marco jurídico: adquisición de la nacionalidad española y su efecto en la clasificación «española/extranjera» (residencia exigida según el origen; vías extraordinarias recientes).
- Regularizaciones y su efecto en el padrón.
- Estadística: cómo mide el INE la población (ECP, base censal, revisiones).

## 6. Limitaciones previstas

- Son **stocks, no flujos**: la variación mezcla llegadas, salidas, nacimientos, defunciones y cambios de nacionalidad.
- Cambios de nacionalidad: pasan población de «extranjera» a «española» sin que nadie se mueva.
- «Nacido en el extranjero» incluye a españoles nacidos fuera; no equivale a «llegada reciente».
- Posible **ruptura de serie** alrededor de 2021 (transición CP → ECP y revisión censal) y cambio de las clasificaciones de Europa en 2020; se comprueba y se explicita.
- Datos hasta 1-I-2025 (la tabla 56938); el empalme con 2026 requiere comprobar la coherencia en el solape.
- Solo nivel nacional; el análisis territorial queda para otro artículo.
- Descriptivo: no atribuye causas.

## 7. Cambios al plan

<!-- AAAA-MM-DD · qué cambió y por qué -->
