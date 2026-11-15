# p01 · ¿Crece España solo gracias a la inmigración? — Plan previo

**Estado:** borrador vivo (actualizado 2026-11-15). No se ha mirado ningún resultado nuevo.
Este documento no se publica; la entrada recoge su contenido relevante.

> **Plan flexible, con registro.** Las afirmaciones, los criterios y las decisiones de medición
> se pueden ajustar durante la revisión de la entrada. Cada cambio se anota en la sección 9
> con fecha y motivo, y la entrada indica qué se cambió después de ver los datos.

> **Transparencia sobre lo que ya sabemos.** Antes de este plan conocemos dos hechos públicos:
> el INE atribuye el crecimiento reciente al aumento de los nacidos en el extranjero, y la
> versión anterior del análisis (tabla 56938) mostraba la caída de los nacidos en España.

## 1. El debate que motiva la pregunta (precampaña y campaña del 29-N de 2026)

Estas voces **inspiran** la pregunta; ninguna formula literalmente las afirmaciones de la
sección 2, y la entrada no se las atribuye. Citas literales; *pendiente*: comprobar cada
una en su fuente primaria (programas, transcripciones, vídeos) antes de publicar.

- **PSOE / Gobierno.** Pedro Sánchez, Spain Investors Day, 15-I-2026: «En España no sobra
  nadie, no sobra nadie. Al contrario, nos falta gente» (transcripción, La Moncloa). En la
  presentación del plan de integración, 30-VI-2026: «en un país que envejece, la inmigración
  ayuda a cubrir necesidades laborales» (La Moncloa).
- **Vox.** Santiago Abascal, mitin en Guadalajara, 7-XI-2026: «Ahora mismo no queremos que
  venga nadie», «Ha venido demasiada gente» (La Bandera). Entrevista en *La Razón*,
  18-X-2026: «No cabe nadie más» (titular, Infomigrante). Programa electoral, 12-XI-2026:
  «recibir a 5 millones de personas en 5 años» (citado por una guía de terceros; verificar
  en el programa).
- **PP.** Alberto Núñez Feijóo, entrevista en *The Objective*, 10-XI-2026: «el caos y el
  efecto llamada están provocando una invasión de inmigración irregular en nuestro país».
  Programa, 10-XI-2026: prohibir las regularizaciones «masivas e indiscriminadas».
- **Empresarios.** CEOE, diciembre de 2025: pide un pacto de Estado para atraer inmigración
  y «sostener el crecimiento» (titular de *Artículo 14*; buscar la cita literal).
- **Sumar, Podemos y sindicatos:** no se han encontrado declaraciones recientes sobre
  población o demografía (solo sobre regularización y acogida). *Pendiente: seguir buscando
  para que el contexto no quede sesgado.*
- **INE**, nota ECP 4T 2025: «El crecimiento poblacional de España se debió al incremento de
  personas nacidas en el extranjero».

## 2. Afirmaciones que se contrastan (formuladas por el blog)

**A1.** *La población residente en España crece solo por la llegada de población del
extranjero: el saldo natural (nacimientos menos defunciones) es negativo, y todo el
crecimiento procede del saldo migratorio.*

- A1a. Componentes del crecimiento anual: saldo natural y saldo migratorio.
- A1b. Población nacida en España frente a nacida en el extranjero: variación anual.

**A2.** *La población de origen español disminuye mientras aumenta la de origen extranjero.*

- A2a. «Origen» = país de nacimiento.
- A2b. «Origen» = nacionalidad (las nacionalizaciones pasan personas de un grupo a otro).

**Análisis complementario.** «Sin inmigración» es un contrafactual: se cuantifica qué parte
de los nacimientos es de madres extranjeras o nacidas fuera, y cuál sería el saldo natural
sin ellos.

## 3. Periodo

- **Núcleo: 2002–2026**, el máximo con la misma fuente homogénea para población por
  nacionalidad y país de nacimiento (ECP, tabla 56938) y nacimientos y defunciones (MNP).
- **Contexto largo: desde 1975** para población total, nacimientos y defunciones (saldo
  natural), si las series lo permiten. El saldo migratorio anterior a 2008 se obtiene como
  residuo (crecimiento − saldo natural), indicándolo.
- Los criterios del veredicto se aplican a la etapa reciente (afirmaciones en presente) y se
  muestra si el veredicto cambia según la etapa.

## 4. Etapas de gobierno (descriptivo, no causal)

Los gráficos marcan los periodos de gobierno (Aznar hasta 2004, Zapatero 2004–2011, Rajoy
2011–2018, Sánchez desde 2018) para ver **si hay cambios de tendencia que coincidan** con
ellos. Advertencias que la entrada recoge:

- Coincidir no es causar: los ciclos económicos (crisis de 2008, recuperación, pandemia),
  los flujos internacionales y la normativa europea pesan tanto o más que el gobierno.
- Las políticas actúan con retraso, y los cortes de legislatura son arbitrarios.
- Contraste mínimo: la tasa de paro como contexto y la comparación con países de la UE
  (Eurostat), para ver si el patrón es español o compartido.
- Las medidas concretas (regularizaciones de 2005 y de 2026) se señalan como eventos.

## 5. Datos (INE; descarga en `src/download/download_ine_tables.py`)

- **79273** (ECP): población por nacionalidad y país de nacimiento (España/extranjero),
  trimestral, 1-IV-2002 – 1-X-2026. Sustituye a la 56938 (edad simple), que no hace falta.
- **24310** y **69760** (Estadística de Migraciones): saldo migratorio con el extranjero,
  2008–2021 y 2021–2024. Antes de 2008, residuo (crecimiento − saldo natural).
- **6525** y **6562** (MNP): nacimientos y defunciones desde 1975; **6566 / 6580 / 6581 /
  48861**: fenómenos demográficos (variantes por revisar).
- **58929–58932** (MNP): nacimientos por nacionalidad y país de nacimiento de la madre;
  **58701, 70648, 31915**: defunciones por nacionalidad y país de nacimiento.
- **1416, 5224, 2776** (IDB): saldo vegetativo y crecimiento por mil, % de nacidos de madre
  extranjera (contraste de nuestros cálculos).
- *Pendiente*: datos provisionales del MNP de 2025 (operación 311); tasa de paro (EPA);
  Eurostat para la comparación con la UE.

## 6. Criterios del veredicto (provisionales; revisables con registro)

Categorías: *se sostiene · se sostiene con matices · no se sostiene · no contrastable*.

**A1** (etapa reciente, últimos diez años)
- Se sostiene: saldo natural ≤ 0 en todos los años y crecimiento ≤ saldo migratorio.
- Con matices: se cumple en la mayoría de los años (≥ 7 de 10) o con una sola traducción.
- No se sostiene: saldo natural positivo en la mayoría de los años.

**A2**
- Se sostiene: el grupo «español» disminuye y el «extranjero» aumenta con las dos
  definiciones.
- Con matices: se cumple con una definición y no con la otra.
- No se sostiene: no se cumple con ninguna.

## 7. Fuera del alcance de esta entrada (con su motivo)

- «Sustitución» o «reemplazo» como plan deliberado: afirmación sobre intenciones, no
  falsable; la literatura la clasifica como teoría conspirativa («Gran Reemplazo»).
- «Nos falta gente», «sobra gente», «no cabe nadie más», «ha venido demasiada gente»:
  juicios normativos o de capacidad sin un criterio medible.
- «5 millones de personas en 5 años» y el aumento de las llegadas por gobiernos: falsables,
  pero sobre **flujos**; candidatos para la entrada de migraciones (p07).
- «Efecto llamada» de las regularizaciones: afirmación causal; requiere diseño causal.
- «La mitad del crecimiento del PIB se debe a la inmigración»: otra entrada (economía).

## 8. Notas del corrector de sesgo

- Las inspiraciones cubren Gobierno, PP, Vox, CEOE e INE; faltan voces de Sumar, Podemos y
  sindicatos sobre demografía: seguir buscando.
- A1 y A2 se tratan con los mismos criterios; es probable que ambas se sostengan en lo
  esencial, y la entrada debe decirlo sin rebajarlo.
- Marcar los gobiernos invita a una lectura causal: el texto debe frenarla explícitamente.
- Lenguaje simétrico y no valorativo («población nacida en el extranjero»).

## 9. Cambios al plan

- 2026-11-15 · Entrada renumerada como p01 (primera publicada). Debate actualizado a la
  precampaña del 29-N. Periodo ampliado a 2002–2026 (contexto desde 1975) y etapas de
  gobierno añadidas, a petición del autor. Plan declarado flexible con registro de cambios.
- 2026-11-15 · Fuente de stocks: tabla 79273 en lugar de la 56938 (misma operación, sin
  edad simple, llega a 1-X-2026). Se eliminan los scripts y datos de la 56938.
- 2026-11-16 · Nacimientos y defunciones de 2025: el MNP provisional (operación 311) no
  publica tablas; se usan las estimaciones experimentales EMN (46682) y EDeS (62277),
  señaladas como tales en el texto y en la figura 1.
- 2026-11-16 · Saldo migratorio: tabla 24310 hasta 2020 y 69760 desde 2021 (nueva
  Estadística de Migraciones y Cambios de Residencia; el dato de 2021 pasa de 148.070 a
  191.094). Antes de 2008 y en 2025 no hay saldo publicado: se usa el implícito
  (crecimiento − saldo natural), identificado como tal en figuras y tablas.
- 2026-11-16 · Nacimientos según nacionalidad de la madre 2002–2008: se reconstruyen con
  el porcentaje de la tabla 2776 (Indicadores Demográficos Básicos), porque la 58929
  empieza en 2009.
- 2026-11-16 · Etapas de gobierno: cada año se asigna al gobierno que lo ocupó en su mayor
  parte (Aznar 2002–2003, Zapatero 2004–2011, Rajoy 2012–2017, Sánchez 2018–2025).
- 2026-11-16 · Tras ver los datos: el texto de A1a añade que el saldo natural ya fue
  negativo en 2015 y que entre 2010 y 2015 el saldo migratorio fue negativo. No cambian
  las afirmaciones ni los criterios.
- 2026-11-16 · Verificación independiente: todas las cifras coinciden al recalcularlas desde
  los CSV. Correcciones de texto: veredicto de A1 «desde 2016» (en 2015 la población bajó);
  población de 49,6 M a 1-I-2026; volumen de nacionalizaciones (EANER); máximo de nacidos en
  España el 1-I-2013; la nacionalidad española aumenta entre 2016 y 2026, pero no todos los
  años; pies de la figura de madres y de la tabla de gobiernos; la interpretación pasa a
  formularse como hipótesis hasta añadir EPA y referencias. Las cuatro citas están verificadas;
  la de Abascal solo en un medio secundario (pendiente: vídeo original).
- 2026-11-16 · Nueva sección «¿Sigue la inmigración al ciclo económico?», a petición del autor
  (antes era una hipótesis sin contrastar en la interpretación). Fuente: EPA (ocupados y tasa
  de paro por nacionalidad, medias anuales). Medida principal: r de Pearson entre el saldo
  migratorio del año t (implícito antes de 2008 y en 2025) y la variación de los ocupados de
  nacionalidad española entre t−1 y t, 2003–2025. Se usa el empleo español y no el total para
  evitar la relación mecánica (el total incluye a los inmigrantes ocupados). Criterios fijados
  antes de descargar la EPA: se sostiene si r ≥ 0,7; con matices si 0,4 ≤ r < 0,7; no se
  sostiene si r < 0,4. Comprobaciones: empleo de t−1, solo años con saldo publicado
  (2008–2024), tasa de paro total. Limitación declarada: las nacionalizaciones inflan la
  variación del empleo español en 2023–2025.
- 2026-11-16 · EPA descargada: tablas trimestrales 65112 (ocupados por nacionalidad, sexo y
  edad) y 65336 (tasas de paro por nacionalidad, sexo y CCAA; fila «Total Nacional»). Se
  descartan sus versiones anuales (65963, 66057). Decisión tras ver la tabla, antes de calcular
  r: en la EPA «Española» excluye la doble nacionalidad, que va aparte; la medida principal usa
  «Española» sin doble nacionalidad (reduce el efecto de las nacionalizaciones) y se añade como
  comprobación r con española + doble. Resultado: r = 0,55 → hipótesis H «se sostiene con
  matices» (t−1: 0,71; con doble: 0,55; 2008–2024: 0,41; tasa de paro: −0,94). La lectura
  señala la reacción con retraso como pista, no como resultado (no era el criterio fijado).
- 2026-11-16 · Verificación independiente de la sección del ciclo: cifras de r correctas.
  Cambios: r con doble nacionalidad calculada sobre los mismos 23 años (0,56); muestra de la EPA
  descrita como ~65.000 viviendas (~47.500 entrevistadas) y ocupados incluyendo ausentes
  temporales (ERTE 2020); se mencionan los cambios de la EPA (cuestionario 2005, base Censo 2021);
  el retraso pasa a «los datos sugieren» y se añade 2008–2009; se añade r sin 2003–2007 (0,43)
  y r con la variación de la tasa de paro (−0,38) junto a la de su nivel (−0,94); la hipótesis H
  se formula como «va acompasada con el ciclo» (sin sentido causal).
