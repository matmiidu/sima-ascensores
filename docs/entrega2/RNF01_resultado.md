# RNF-01 · Confiabilidad sin conexión del checklist: verificación

| | |
|---|---|
| Elemento JIRA | SIMA-34 · RNF-01; se exige completo en SIMA-20 (H06) |
| Riesgo | R1: las salas de máquinas y los fosos no tienen señal de celular |
| Requisito | Bajo falta de señal, el sistema conserva los checklists en el celular y los envía solos en 60 segundos o menos al volver la señal, sin perder ni duplicar ninguno |
| Responsable | Fabio Bermúdez |
| Fecha de la prueba | 10 de noviembre de 2026 |

## Cómo quedó construido

Es el esquema que se probó en S01, ahora con el checklist definitivo:

- Al abrir "Mis visitas" con señal, el celular guarda una copia de las visitas del día y de los puntos del checklist.
- Al guardar, la mantención queda primero en el celular (IndexedDB) con un identificador propio (`id_local`). Si hay señal se envía de inmediato; si no, queda pendiente.
- Las reglas de RF-02 y RF-03 se revisan también en el celular, porque sin señal el servidor no puede rechazar.
- Lo pendiente se envía solo al abrir la aplicación, cuando vuelve la señal y cada 20 segundos mientras quede algo.
- Si un envío se repite, el servidor reconoce el `id_local` y no lo duplica.
- Si el servidor no acepta una mantención (por ejemplo, la visita ya estaba registrada), no se reintenta: queda a la vista del técnico con el motivo.

## Cómo se probó

Navegador Firefox con pantalla de 400 px de ancho y la conexión cortada por software (Playwright), con la
aplicación compilada y el servidor en el mismo computador. Usuario del técnico Juan Pérez, con 11 visitas
por registrar.

| Paso | Resultado |
|---|---|
| Abrir la aplicación con señal e ingresar | La lista de visitas y el checklist quedan copiados en el celular |
| Cortar la señal | Aviso "Sin señal: lo que guardes queda en el celular" |
| Guardar 10 checklists (uno con equipo detenido y uno con observación) | Los 10 quedan "En el celular"; aviso "10 mantenciones guardadas en el celular, sin enviar" |
| Revisar el servidor mientras no hay señal | 0 registros |
| Cerrar y volver a abrir la aplicación, sin señal | La aplicación abre; los 10 siguen guardados y pendientes (CA-01) |
| Devolver la señal, sin tocar nada | Los 10 llegan al servidor en 5,3 segundos (CA-02; el límite es 60) |
| Contar en el servidor | 10 registros, 10 `id_local` distintos, 10 visitas distintas, las 10 visitas Realizadas |
| Revisar el celular | 10 enviadas, 0 pendientes, 0 rechazadas |

La prueba se hizo dos veces (9 y 10 de noviembre): 5,7 y 5,3 segundos. Casi todo ese tiempo es lo que
tarda la aplicación en notar que volvió la señal, que revisa cada 5 segundos.

Capturas: `capturas/rnf01_01_guardada_en_el_celular.png`, `rnf01_02_diez_pendientes.png`,
`rnf01_03_reabierta_sin_senal.png` y `rnf01_04_enviadas.png`.

Además hay dos pruebas automáticas en el servidor: el mismo envío repetido no duplica, y diez registros
enviados dos veces quedan como diez.

## Límites

1. **Falta la prueba en un celular real.** El método de RNF-01 pide repetirla dentro de un subterráneo. Para
   eso hay que publicar la aplicación con HTTPS, y hoy se ejecuta solo en el computador del equipo.
2. **El técnico tiene que abrir la aplicación con señal al empezar el día**, para que su lista quede en el celular.
3. **El primer ingreso necesita señal.**
4. Si el técnico cierra su sesión con mantenciones sin enviar, no se pierden: se envían cuando vuelve a
   entrar con su usuario en ese celular. La aplicación se lo avisa antes de salir.

## Conclusión

**Cumple en el computador; pendiente en un celular real.** Los dos criterios se cumplen con holgura en la
prueba de escritorio. RNF-01 no se da por verificado del todo hasta repetir la prueba en terreno.

R1 se mantiene como quedó tras S01: probabilidad Alta, impacto Medio, prioridad Media.
