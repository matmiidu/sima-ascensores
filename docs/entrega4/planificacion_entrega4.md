# Planificación de la Entrega 4 (entrega adicional)

**Período:** 26 de noviembre – 3 de diciembre de 2026 (una semana).
**Fecha de la planificación:** 26 de noviembre de 2026, al día siguiente de cerrar la Entrega 3.
**Entregable comprometido:** el técnico trabaja la jornada completa sin señal y la cartera se carga desde la planilla.

> **SIMULACIÓN.** Ascensores Altavía es una empresa ficticia. Las decisiones que el plan
> le asigna al jefe técnico (dueño del producto) las tomó el equipo en su nombre.

## 1. Por qué hay una cuarta entrega

El plan de la Evaluación 2 tenía tres entregas y dejaba H07 y H02 como "Posterior". Las tres
entregas se cerraron el 25 de noviembre, antes de lo previsto (29 de noviembre), y quedó tiempo
hasta la presentación final del 3 de diciembre. Como dice el plan, lo que sigue en el backlog se
ordena por prioridad: el jefe técnico (simulado) eligió las dos historias que quedaban.

## 2. Capacidad

La capacidad supuesta es de 8 puntos por entrega de dos semanas. H07 (8) y H02 (3) suman 11 puntos
en una semana, más que la capacidad. Se acepta igual, por dos motivos:

- Las tres entregas anteriores cumplieron sus 8 puntos y la Entrega 3 terminó cuatro días antes.
- H07 se apoya en lo ya construido para S01, H04 y H06 (guardado en el celular, envío automático y
  reintentos), así que su trabajo nuevo es menor que su estimación original.

Riesgo R4 (capacidad): si no alcanza, H02 se saca de la entrega y vuelve al backlog. H07 va primero.

## 3. Elementos confirmados

| ID | Elemento | Puntos | Responsable | Depende de |
|---|---|---|---|---|
| H07 | Trabajar sin conexión de punta a punta | 8 | Fabio Bermúdez | S01 (Entrega 1), H06 (Entrega 2) |
| H02 | Importar la cartera desde la planilla | 3 | Matias Valenzuela | A03 (Entrega 1) |

## 4. Decisiones

| N.º | Decisión | Motivo |
|---|---|---|
| D18 | Se abre una cuarta entrega, de una semana, con H07 y H02 | Las entregas del plan terminaron y el backlog solo tiene estas dos historias |
| D19 | H07 se define como la jornada completa sin señal: el celular guarda hoy y los seis días siguientes, y durante la visita muestra la última mantención del equipo | S01 dejó como límite que el técnico debía abrir con señal cada día; en terreno puede pasar varios días sin señal estable |
| D20 | H02 reutiliza las reglas de la revisión de la planilla de A03 (duplicados y fechas sin registrar) y muestra lo que se va a cargar antes de guardar | Es la respuesta al riesgo R3: no importar datos erróneos sin verlos |

## 5. Lo que queda fuera

- La prueba en un celular real dentro de un subterráneo, que requiere publicar con HTTPS. En esta
  entrega se prueba la jornada completa sin señal en el navegador, en pantalla de celular.
- Las propuestas del acta de A05 (plan del fabricante, componentes por reemplazar, número de la instalación).
