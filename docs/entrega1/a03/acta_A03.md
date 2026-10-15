# Acta A03 · Validación de una muestra de la planilla contra terreno

> **SIMULACIÓN.** Ascensores Altavía es una empresa ficticia. La planilla se generó
> con datos inventados y la visita a terreno no ocurrió: los resultados de la
> columna "terreno" son supuestos del caso, escritos para ejercitar la acción de
> respuesta al riesgo R3. La revisión automática de la planilla sí se ejecutó.

| | |
|---|---|
| Elemento JIRA | SIMA-30 · A03 |
| Riesgo | R3: la planilla tiene equipos duplicados y fechas de certificación sin registrar |
| Entrega | Entrega 1 (19 oct – 1 nov 2026) |
| Responsable | Fabio Bermúdez |
| Participan (simulado) | Jefe técnico y asistente administrativa |

## 1. Revisión automática de la planilla (ejecutada)

Herramienta: `herramientas/validar_planilla.py` sobre `planilla_actual.csv` (144 filas).

| Hallazgo | Filas |
|---|---|
| Sin fecha de certificación | 9 |
| Comuna mal escrita | 5 |
| Equipo repetido (escrito de otra forma) | 4 |
| Marcado como retirado | 1 |
| **Filas con al menos un problema** | **19 de 144 (13 %)** |

La planilla dice 144 equipos; la cartera real son 140. La diferencia son los 4 repetidos.

## 2. Muestra para terreno

20 equipos (`muestra_terreno.csv`): 10 con hallazgos, priorizando los repetidos y el retirado,
que son los que generan visitas de más, y 10 sin hallazgos elegidos al azar para estimar el error
de las filas que parecen limpias.

## 3. Resultado en terreno (simulado)

| Grupo | Revisados | Resultado |
|---|---|---|
| Repetidos | 3 | Los 3 son el mismo equipo físico que su fila original. Se confirma la regla: misma dirección y mismo número de equipo es el mismo ascensor. |
| Retirado | 1 | El equipo ya no existe. Debe salir de la cartera. |
| Sin fecha de certificación | 5 | En 4 la placa del certificador muestra la fecha. En 1 la placa no se lee: hay que pedir el certificado al administrador. |
| Sin hallazgos | 10 | 9 coinciden. En 1 la fecha de la planilla no coincide con la placa (se transcribió mal el año). |
| Comuna mal escrita | 1 | Solo error de escritura; el edificio es el mismo. |

Error en las filas sin hallazgos: 1 de 10. Es una muestra chica, pero indica que la revisión
automática no basta: la fecha de certificación hay que confirmarla con el documento.

## 4. Reevaluación del riesgo R3

| | Antes | Después |
|---|---|---|
| Probabilidad | Alta | Alta: los defectos existen y se confirmaron |
| Impacto | Medio | Bajo, si la importación aplica las reglas de abajo |
| Prioridad | Media | **Baja**, condicionada a que H02 incluya las reglas |

## 5. Decisiones

1. **H02 (importar la planilla) deja de estar bloqueada por A03**, pero su criterio de aceptación
   suma tres reglas: unir repetidos por dirección y número de equipo normalizados (mostrando la
   unión antes de guardar); excluir los marcados como retirados; aceptar filas sin fecha de
   certificación, pero dejarlas en una lista "por confirmar" para el jefe técnico.
2. La comuna se elige de una lista en SIMA, no se escribe a mano. (Ya está así en el formulario
   de H01 como texto libre: **queda como ajuste menor para la Entrega 2**.)
3. Antes de la carga real (etapa de cierre), la asistente pide a los administradores los
   certificados de los equipos sin fecha.

Fecha del acta: 15 de octubre de 2026 (adelantada dentro del refinamiento de la Entrega 1).
