# Planificación de la Entrega 2

**Período:** 2 – 15 de noviembre de 2026.
**Fecha de la planificación según el plan:** lunes 2 de noviembre (primer día de la entrega). Este registro se escribió el 10 de noviembre, junto con la construcción.
**Entregable comprometido:** el técnico ve sus visitas y completa el checklist en el celular.

> **SIMULACIÓN.** Ascensores Altavía es una empresa ficticia. Las decisiones que el plan
> le asigna al jefe técnico (dueño del producto) las tomó el equipo en su nombre.

## 1. Capacidad

En la Entrega 1 se construyeron los 8 puntos comprometidos, así que se mantiene la capacidad
supuesta de 8 puntos por entrega. El riesgo R4 (otras asignaturas reducen la capacidad) se revisó
como pide el plan: la Evaluación 3 del 28 y 29 de octubre ocupó tiempo de la Entrega 1 y aun así
cupo, por lo que no se baja la cifra.

## 2. Elementos confirmados

| ID | Elemento | Puntos | Responsable | Depende de |
|---|---|---|---|---|
| H04 | Ver mis visitas del día | 2 | Matias Valenzuela | H03 (Entrega 1) |
| H06 | Completar el checklist en el celular | 5 | Fabio Bermúdez | H04 |
| A02 | Sesión de prueba del checklist con dos técnicos (simulación) | 2 h | Matias Valenzuela | Maquetas de H06 |

Requisitos que se construyen dentro de H06: RF-02 versión 3 (SIMA-33), RNF-01 (SIMA-34) y RF-03 (SIMA-35).

## 3. Decisiones

| N.º | Decisión | Motivo |
|---|---|---|
| D12 | RF-03 (describir la falla cuando el equipo queda detenido) se construye en esta entrega, dentro de H06 | Es una validación más del mismo guardado. Ocupa el punto que quedaba libre: la entrega queda en 8 de 8 |
| D13 | Elegir la comuna de una lista (hallazgo de A03) sigue en el backlog y no entra a esta entrega | Con RF-03 la capacidad queda completa y aporta menos al objetivo de la entrega que el checklist |
| D14 | A02 se hace con las maquetas antes de cerrar el checklist | Así lo dice la respuesta al riesgo R2: probar con dos técnicos antes de cerrarlo |
| D15 | Cada técnico entra con su propio usuario y solo el jefe técnico modifica la cartera y el calendario | H04 necesita saber de quién son las visitas; quedó anotado como pendiente en la Evaluación 3 |

## 4. Lo que no cabe y queda pendiente

- **Prueba de S01 y de RNF-01 en un celular real.** Requiere publicar la aplicación con HTTPS, y la
  aplicación todavía se ejecuta solo en el computador del equipo. En esta entrega RNF-01 se verifica
  en el computador con la señal cortada por software; la prueba en un celular dentro de un
  subterráneo queda para la etapa de cierre, con la primera publicación.
- **H07 (trabajar toda la visita sin conexión)** sigue como posterior a la primera versión.

## 5. Orden de trabajo

1. H04, porque H06 parte de la lista de visitas.
2. A02 con las maquetas de la Evaluación 3.
3. H06 con los ajustes que deje A02, y la verificación de RNF-01.
4. Revisión de la entrega el viernes 13 de noviembre.
