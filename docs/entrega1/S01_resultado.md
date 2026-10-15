# S01 · Prueba de concepto sin conexión: resultado y decisión

| | |
|---|---|
| Elemento JIRA | SIMA-17 · S01 (2 puntos) |
| Riesgo | R1: las salas de máquinas y los fosos no tienen señal de celular |
| Pregunta | ¿Puede la aplicación web (PWA) guardar un checklist sin señal y enviarlo sola al recuperarla, sin perder ni duplicar registros? |
| Responsable | Fabio Bermúdez |

## Qué se construyó

- La aplicación se instala como PWA y su service worker guarda la aplicación en el celular, así que abre aunque no haya señal.
- El checklist de prueba (cinco puntos y observaciones; **no** es el checklist definitivo de H06) se guarda en IndexedDB, la base de datos del navegador.
- Cada registro lleva un identificador generado en el celular (`id_local`). Si un envío se repite porque la respuesta se perdió, el servidor responde "ya lo tengo" y no lo duplica (`POST /api/poc/checklists/`).
- La lista de ascensores queda copiada en el celular para poder elegir el equipo sin señal.
- Al volver la señal, lo pendiente se envía sin que el técnico haga nada, y mientras quede algo pendiente se reintenta cada 20 segundos.

## Cómo se probó

Navegador Firefox con pantalla de 400 px de ancho y la conexión cortada por software (Playwright), contra el servidor local.

| Paso | Resultado |
|---|---|
| Abrir la aplicación con señal e ingresar | La aplicación queda guardada en el celular |
| Cortar la señal y recargar | La aplicación abre; avisa "Sin señal" |
| Elegir ascensor sin señal | Disponible (lista copiada: 142 equipos) |
| Guardar 3 checklists sin señal | Quedan como "Pendiente" |
| Cerrar y volver a abrir sin señal | Los 3 siguen guardados |
| Devolver la señal | Se envían solos en unos 5 segundos |
| Revisar el servidor | Llegan los 3, con sus respuestas y observaciones, sin duplicados |
| Reenviar el mismo registro (prueba automática) | El servidor no lo duplica |

Capturas: `capturas/08a_sin_senal_guardado.png`, `08_sin_senal_pendientes.png`, `09_senal_recuperada_enviados.png`.

## Lo que se aprendió

1. **El aviso de "volvió la señal" no es confiable.** En la primera prueba el navegador no avisó el regreso de la conexión y los registros quedaron pendientes. Se agregó una revisión cada 5 segundos y reintentos cada 20. En terreno será peor (la señal va y viene), así que el reintento periódico queda como regla de diseño.
2. **La lista de equipos también debe vivir en el celular.** La copia automática del navegador no la entregó sin señal; se guardó aparte.
3. **El service worker exige HTTPS.** En el computador se prueba en `localhost`, pero para probar en un celular real hay que publicar la aplicación con HTTPS.
4. **El primer ingreso necesita señal.** El técnico debe abrir la aplicación con señal al menos una vez al día para tener su lista al día.

## Conclusión

**Viable con límites.** El trabajo sin conexión funciona con la tecnología elegida, siempre que:
la aplicación se publique con HTTPS, el técnico abra la aplicación con señal al inicio del día y el envío se reintente solo.

## Decisión

- **Se mantiene la PWA.** No se activa la alternativa C (software comercial).
- **H07 (trabajar sin conexión de punta a punta) sigue como "Posterior"**: no hace falta adelantarla, porque lo básico ya funciona.
- **H06 (checklist definitivo, Entrega 2) se construye sobre este mismo esquema**: IndexedDB, `id_local` y reintento periódico.
- **Pendiente para cerrar del todo:** probarlo en un celular real dentro de un subterráneo o una sala de máquinas. Se hará con la primera publicación HTTPS, junto con la sesión A02 (Entrega 2).
- **R1 se reevalúa:** la probabilidad sigue Alta (no hay señal), pero el impacto baja de Alto a Medio. La prioridad pasa de Alta a Media.
