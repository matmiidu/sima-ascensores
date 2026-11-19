# Revisión de la Entrega 2

**Período:** 2 – 15 de noviembre de 2026.
**Entregable comprometido:** el técnico ve sus visitas y completa el checklist en el celular.
**Capacidad supuesta:** 8 puntos por entrega.
**Estado al 19 de noviembre:** revisada y cerrada. H04, H06 y A02 están en Terminado en JIRA.

## Qué se entrega

| ID | Elemento | Puntos | Estado en JIRA | Evidencia |
|---|---|---|---|---|
| H04 | Ver mis visitas del día | 2 | Terminado | `criterios_aceptacion.md`, capturas 01, 02 y 08 |
| H06 | Completar el checklist en el celular | 5 | Terminado | `criterios_aceptacion.md`, capturas 03 a 12 |
| RF-02 | Registrar el checklist de la visita (versión 3) | en H06 | Terminado, verificado con H06 | Cuatro criterios con prueba automática y captura |
| RF-03 | Exigir la descripción de la falla | 1 (D12) | Terminado, verificado con H06 | Dos criterios con prueba automática y captura |
| RNF-01 | Confiabilidad sin conexión del checklist | en H06 | Terminado, verificado con H06 | `RNF01_resultado.md`, capturas rnf01_01 a rnf01_04 |
| A02 | Sesión de prueba del checklist con dos técnicos | 2 h | Terminado | `a02/acta_A02.md` (**simulación**) |

Puntos construidos: **8 de 8** (H04, H06 y RF-03). 56 pruebas automáticas aprobadas: 12 de la cartera y los
usuarios, 23 del calendario y las visitas del día, y 21 del registro en terreno.

H04, H06 y A02 pasaron a **Terminado** después de la revisión de la entrega, como pide el criterio de término
(ver "Resultado de la revisión"). Las tarjetas de los requisitos (SIMA-33, SIMA-34 y SIMA-35) ya estaban Terminadas porque su
análisis está cerrado; su ficha se actualizó con el resultado de la verificación. En este caso ficticio la revisión con el jefe técnico y los técnicos se registra como simulación.

## Demostración sugerida (5 minutos)

Antes: `cargar_demo --borrar` y abrir la aplicación. Todos los usuarios tienen la clave `sima`.

1. Entrar como `jefe`, ir a Calendario y pulsar "Generar calendario": 140 de 140 equipos con visita.
2. Salir y entrar como un técnico (`juan`, `rodrigo`, `camila`, `luis`, `andres` o `felipe`), con la ventana
   angosta como un celular. Aparece "Mis visitas de hoy" con sus edificios y, más abajo, las atrasadas del mes.
3. Pulsar "Registrar" en un equipo. Responder todo menos un punto y guardar: **rechazo**, se marca el punto
   que falta y lo respondido se conserva.
4. Marcar ese punto "Con observación" y guardar sin escribirla: **rechazo**. Escribirla y guardar: **éxito**,
   "Mantención M-0001 guardada".
5. Registrar otro equipo con "No, quedó detenido" y sin describir la falla: **rechazo**. Describirla: se guarda.
6. Cortar la conexión (modo avión o desconectar la red), registrar otro equipo: queda "En el celular".
   Volver a conectar: en unos segundos pasa a "Realizada" sin tocar nada.
7. Entrar como `jefe`, Calendario: "3 de 140 visitas realizadas", la tarjeta del equipo detenido con su
   falla y, en el día, cada equipo marcado como realizada o detenido. Al tocar uno se abre su registro.

Si el técnico elegido no tiene visitas hoy, igual puede registrar las atrasadas, o se elige otro técnico.

## Resultado de la revisión

Registrada el 19 de noviembre de 2026. Como en la Entrega 1, la aceptación del jefe técnico es **simulación**.

- Se recorrió la demostración sugerida completa (pasos 1 a 7) y cada paso dio el resultado esperado.
- Las 56 pruebas automáticas se volvieron a correr el 19 de noviembre: todas aprobadas.
- H04, H06 y A02 cumplen su criterio de término y pasaron a Terminado en JIRA, con un comentario de la revisión.
- La página de Confluence quedó en la versión 8: requisitos y prototipos de la Entrega 2 marcados como Terminados
  y una fila nueva en el registro de cambios.
- No se agregó alcance a la entrega. La prueba de RNF-01 en un celular real sigue pendiente.

## Qué se aprendió y cambia el plan

- **Capacidad:** cupieron los 8 puntos, con RF-03 en el punto libre. Se mantiene 8 para la Entrega 3
  (8 comprometidos: H09 y H10).
- **RF-03 sirve a la Entrega 3:** el informe mensual (H09) ya tiene de dónde sacar la falla y el estado del equipo.
- **A02:** los cuatro supuestos de la Evaluación 3 se confirmaron solo en simulación; R2 baja de prioridad Alta
  a Media y se revisa de nuevo con técnicos reales en la capacitación del cierre.
- **RNF-01:** cumple en el computador (10 de 10 en 5,3 segundos). Falta la prueba en un celular real.
- **Usuarios:** cada técnico tiene el suyo y solo el jefe técnico modifica la cartera y el calendario. Antes
  cualquier usuario podía hacerlo.
- **Pantalla de prueba de S01:** se retiró, porque H06 usa el mismo esquema con el checklist definitivo. Su
  resultado sigue en `docs/entrega1/S01_resultado.md`.
- **Calendario:** ahora abre en el mes en curso, que es el que el jefe técnico va siguiendo.
- **Panel de administración:** `/admin` abre también sin la barra final.

## Pendiente, bloqueado y próxima acción

| | |
|---|---|
| Pendiente | Prueba de RNF-01 en un celular real, que requiere publicar con HTTPS. |
| Bloqueado | Nada. H09 queda desbloqueada por H06, y antes de construirla va A05. |
| En el backlog | Elegir la comuna de una lista (D13). |
| Próxima acción | Entrega 3 (16 – 29 de noviembre): A05, revisar el formato del informe contra la OGUC; luego H09 y H10. |
