# Acta A02 · Sesión de prueba del checklist con dos técnicos

> **SIMULACIÓN.** Ascensores Altavía y sus técnicos son ficticios. La sesión no ocurrió con
> personas reales: las opiniones de los técnicos y del jefe técnico son supuestos del caso,
> escritos para ejercitar la acción de respuesta al riesgo R2. Lo que sí se ejecutó es la
> medición de la pantalla del checklist (sección 2).

| | |
|---|---|
| Elemento JIRA | SIMA-29 · A02 |
| Riesgo | R2: los técnicos rechazan la aplicación o la llenan al final del día |
| Entrega | Entrega 2 (2 – 15 de noviembre de 2026) |
| Responsable | Matias Valenzuela |
| Participan (simulado) | Luis Muñoz y Camila Rojas, técnicos; jefe técnico |
| Material | Maquetas de H04 y H06 de la Evaluación 3 y, después, el checklist construido |

## 1. Qué se quería validar

La Evaluación 3 dejó cuatro acuerdos como supuestos del equipo, por validar en esta sesión, además
de los puntos del checklist:

| Supuesto | Dónde está | Resultado (simulado) |
|---|---|---|
| Un punto "con observación" exige escribir la observación | RF-02, CA-03 | Se confirma. Piden que el campo aparezca justo debajo del punto, como en la maqueta |
| Una visita no se registra dos veces | RF-02, CA-04 | Se confirma. Sirve que avise cuándo se registró |
| Una visita atrasada se puede registrar; una futura, no | RF-02 versión 3 | Lo confirma el jefe técnico, con un límite: solo mientras siga siendo su mes |
| Si el equipo queda detenido hay que describir la falla | RF-03 | Se confirma. El jefe técnico necesita ese texto para programar la visita correctiva |
| Ocho puntos del checklist | Maqueta de H06 | Se confirman los ocho. "No aplica" hace falta: en un equipo hidráulico no hay cables de tracción |

## 2. Medición de la pantalla (ejecutada)

Hecha sobre el checklist construido, en pantalla de 400 px de ancho, el 10 de noviembre de 2026.

| Medida | Resultado |
|---|---|
| Toques para registrar una mantención sin novedades | 10 (ocho puntos, estado del equipo y guardar) |
| Campos de texto obligatorios en ese caso | 0 |
| Alto mínimo de los botones | 54 px |
| Ancho mínimo de los botones | 108 px |
| Desplazamiento horizontal | No hay |

La factibilidad social del plan pedía botones grandes y pocos campos de texto, para usar la
aplicación con una mano y con poca luz. La medición lo respalda.

## 3. Lo que pidieron los técnicos (simulado) y qué se hizo

| Pedido | Decisión | Estado |
|---|---|---|
| Que el botón del equipo detenido diga la consecuencia y no solo "No" | Se acepta: el botón dice "No, quedó detenido" | Hecho en H06 |
| Saber cuántos puntos van respondidos sin subir por la pantalla | Se acepta: junto al botón de guardar aparece "7 de 8 puntos respondidos" | Hecho en H06 |
| Ver las visitas que quedaron de días anteriores | Se acepta: aparecen aparte como atrasadas y se pueden registrar | Hecho en H04 |
| Que lo que falta se vaya desmarcando al corregirlo | Se acepta: el aviso se actualiza mientras se completa | Hecho en H06 |
| Un botón para marcar todos los puntos como "Bien" | Se rechaza. Lo decide el jefe técnico: es justo la conducta del riesgo R2 (llenar sin revisar) | No se construye |

## 4. Reevaluación del riesgo R2

| | Antes | Después |
|---|---|---|
| Probabilidad | Media | Baja, si la prueba en terreno confirma lo simulado |
| Impacto | Alto | Alto: sin registros confiables no hay informe |
| Prioridad | Alta | **Media** |

La baja depende de un supuesto: que técnicos reales reaccionen como los simulados. Por eso R2 no
se cierra. Se vuelve a revisar en la capacitación de la etapa de cierre, con técnicos reales y en un
edificio.

## 5. Decisiones

1. Los cuatro supuestos de la Evaluación 3 quedan validados solo en simulación. Como no hay un
   interesado real, RF-02, RF-03 y RNF-01 siguen en estado Propuesto en su ficha.
2. El checklist se cierra con ocho puntos y tres respuestas por punto. El jefe técnico puede
   cambiar los puntos desde el panel, sin modificar el programa.
3. No habrá un botón para marcar todo como "Bien".

Fecha del acta: 10 de noviembre de 2026.
