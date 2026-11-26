# Revisión de la Entrega 3

**Período:** 16 – 29 de noviembre de 2026.
**Entregable comprometido:** informe mensual en PDF y alertas de certificación.
**Capacidad supuesta:** 8 puntos por entrega.
**Estado al 25 de noviembre:** revisada y cerrada. H09, H10 y A05 están en Terminado en JIRA.

## Qué se entrega

| ID | Elemento | Puntos | Estado en JIRA | Evidencia |
|---|---|---|---|---|
| A05 | Revisar el formato del informe contra la OGUC | 2 h | Terminado | `a05/acta_A05.md` (**simulación**), extracto de la norma y maqueta P-08 |
| H09 | Generar el informe mensual en PDF | 5 | Terminado | `criterios_aceptacion.md`, capturas 03 a 08, `ejemplos_informe/` |
| H10 | Alertar certificaciones por vencer | 3 | Terminado | `criterios_aceptacion.md`, capturas 00 a 02 |
| RF-06 | Alertar las certificaciones vencidas y por vencer | en H10 | Ficha en Confluence | Cinco criterios con prueba automática |
| RF-07 | Emitir el informe mensual de mantención | en H09 | Ficha en Confluence | Cinco criterios con prueba automática |

Puntos construidos: **8 de 8** (H09 y H10). 68 pruebas automáticas aprobadas: 18 de la cartera, los usuarios y
las certificaciones, 23 del calendario y las visitas del día, y 27 del registro en terreno y el informe.

Cada elemento se trabajó en su propia rama (`feature/SIMA-22-alertas`, `feature/SIMA-31-formato-informe` y
`feature/SIMA-21-informe-pdf`), unida a `main` con un commit de unión, y cada commit lleva la clave de JIRA al
inicio, como el flujo de la clase 7. El orden siguió el plan: A05 antes de H09.

## Demostración sugerida (5 minutos)

Antes: `cargar_demo --borrar`, abrir la aplicación y, como `jefe`, generar el calendario del mes. Todos los
usuarios tienen la clave `sima`.

1. Como `jefe`, abrir Certificaciones: las vencidas, las que vencen en 60 días y las sin fecha, cada una con
   el contacto del administrador. "Avisar al administrador" abre un correo ya escrito (H10).
2. Salir y entrar como el técnico del Edificio Plaza (`luis`). Registrar la mantención de A1 con una
   observación en un punto, y la de A2 con "No, quedó detenido" y la falla descrita (lo de la Entrega 2).
3. Entrar como `jefe` y abrir Informes: el Edificio Plaza aparece con sus mantenciones registradas y el
   equipo detenido. Si falta alguna, el botón dice "Descargar informe parcial".
4. Descargar el PDF y mostrarlo: primera hoja con el resumen y el equipo detenido; una hoja por ascensor con
   el checklist, las observaciones, la certificación y el registro del año (H09).
5. Volver a la aplicación: "Escribir al administrador" abre el correo para adjuntar el PDF.
6. Mostrar el acta de A05: qué exige el artículo 5.9.5 y qué quedó fuera de H09.

## Resultado de la revisión

Registrada el 25 de noviembre de 2026. Como en las entregas anteriores, la aceptación del jefe técnico es
**simulación**.

- Se recorrió la demostración con una base aparte (`Entrega_3_SIMA/_fuente/base_evidencia.py`) en pantalla de
  celular de 400 px; cada paso dio el resultado esperado. Capturas 03 a 08.
- Las 68 pruebas automáticas se corrieron el 25 de noviembre: todas aprobadas.
- H09, H10 y A05 cumplen su criterio de término y pasaron a Terminado en JIRA, con un comentario de la revisión.
- La página de Confluence quedó en la versión 11: ficha RF-07, CU-07 en los casos de uso, prototipo P-08,
  BPMN con la tarea A-04 apoyada por SIMA y una fila nueva en el registro de cambios.
- No se agregó alcance a la entrega.

## Qué se aprendió y cambia el plan

- **Capacidad:** cupieron los 8 puntos (H09 5 y H10 3), igual que en las dos entregas anteriores.
- **A05 cambió el informe antes de construirlo:** la norma pide un informe por mantención; como hay una por
  ascensor al mes, el informe mensual trae una hoja completa por ascensor (D16). Sin A05 se habría hecho un
  resumen por edificio, que el certificador podía objetar (riesgo R5).
- **R5:** baja de prioridad Media a Baja. No se cierra hasta que un certificador real vea un informe.
- **Herramienta de PDF (D17):** WeasyPrint, la que nombraba el plan, necesita bibliotecas del sistema que en
  Windows se instalan aparte. Se usó xhtml2pdf, que hace lo mismo desde una plantilla HTML y se instala con
  `pip`. Si el sistema se publica en un servidor Linux, la misma plantilla sirve para WeasyPrint.
- **Lo que falta para cumplir todo el artículo 5.9.5** quedó en el backlog sin tarjeta: el plan del fabricante
  por modelo, los componentes por reemplazar con su plazo y el número de identificación de la instalación.

## Pendiente, bloqueado y próxima acción

| | |
|---|---|
| Pendiente | Prueba de RNF-01 en un celular real (requiere publicar con HTTPS) y opinión de un certificador real sobre el informe. |
| Bloqueado | Nada. |
| En el backlog | Comuna de una lista (D13); plan del fabricante, componentes por reemplazar y número de instalación (acta de A05). |
| Próxima acción | Cierre del proyecto: las tres entregas del plan están construidas. Siguen las historias "Posterior" del backlog (H02 y H07). |
