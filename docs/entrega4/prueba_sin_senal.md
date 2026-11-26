# Prueba de la jornada completa sin señal (H07)

**Fecha:** 26 de noviembre de 2026.
**Dónde:** Firefox controlado por Playwright, pantalla de celular de 400 px, contra una base aparte
(`Entrega_4_SIMA/_fuente/base_sin_senal.py`). Script: `Entrega_4_SIMA/_fuente/prueba_sin_senal.mjs`.
**Técnico:** Luis Muñoz (`luis`). Hoy tiene 4 visitas (Torre Pacífico 3), 22 atrasadas del mes y 4 el 1 de diciembre.

La prueba simula la falta de señal de dos formas a la vez: corta la red del navegador **y apaga el
servidor**. Además cierra el navegador entero dos veces, como si el técnico bloqueara el celular y volviera a
abrir la aplicación.

## Resultado

| Paso | Qué se hizo | Resultado |
|---|---|---|
| 1 | Entrar con señal al empezar el día | "Listo para trabajar sin señal hasta el miércoles 2 de diciembre" (hoy y seis días más) |
| 2 | Cortar la red, apagar el servidor, cerrar y abrir la aplicación | Abre; avisa "Sin señal: se muestra la lista guardada en el celular hoy a las 13:15" y muestra las 4 visitas de hoy |
| 3 | Avanzar al 1 de diciembre sin señal | Se ven las 4 visitas de ese día (Condominio El Bosque 2) |
| 3 | Avanzar al 3 de diciembre, fuera de la jornada | Mensaje: "este día no está guardado en el celular. La jornada guardada llega hasta el 02-12-2026" |
| 4 | Abrir la visita atrasada de Edificio Plaza A2 | Muestra la última mantención: 20-10-2026, quedó detenido, la falla y la observación de P01 |
| 5 | Registrar 5 mantenciones sin señal (una con el equipo detenido) | Las 5 quedan "guardadas en el celular, sin enviar" |
| 6 | Cerrar y volver a abrir la aplicación, aún sin señal | Siguen las 5 pendientes |
| 7 | Devolver la red y encender el servidor, sin tocar nada | Las 5 se envían solas en **3,6 segundos** |
| 8 | Revisar el servidor | 5 registros nuevos, cada uno con su id del celular, en 5 visitas distintas, 1 detenido; ninguno repetido |

Capturas: `capturas/h07_01` a `h07_08`.

## Defecto encontrado y corregido

En la primera ejecución, el paso 2 mostró las visitas **sin** el aviso "Sin señal". Firefox, sin conexión,
entregaba las respuestas de la API que tenía en su caché como si vinieran del servidor. El técnico habría
visto datos posiblemente viejos sin saberlo.

Corrección: el servidor marca toda respuesta de `/api/` con `Cache-Control: no-store`
(`backend/config/sin_cache.py`), así que la única copia sin señal es la de la aplicación, que siempre dice de
qué hora es. Prueba automática: `test_las_respuestas_de_la_api_no_quedan_en_la_cache_del_navegador`.

## Lo que esta prueba no cubre

Un celular real dentro de un subterráneo. Para eso la aplicación tiene que estar publicada con HTTPS, porque
el service worker (lo que permite abrirla sin señal) solo funciona en `localhost` o con HTTPS.
