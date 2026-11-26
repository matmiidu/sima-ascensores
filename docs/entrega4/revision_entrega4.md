# Revisión de la Entrega 4

**Período:** 26 de noviembre – 3 de diciembre de 2026 (entrega adicional, ver `planificacion_entrega4.md`).
**Entregable comprometido:** el técnico trabaja la jornada completa sin señal y la cartera se carga desde la planilla.
**Estado al 26 de noviembre:** revisada y cerrada. H07 y H02 están en Terminado en JIRA.

## Qué se entrega

| ID | Elemento | Puntos | Estado en JIRA | Evidencia |
|---|---|---|---|---|
| H07 | Trabajar sin conexión de punta a punta | 8 | Terminado | `criterios_aceptacion.md`, `prueba_sin_senal.md`, capturas h07_01 a h07_08 |
| H02 | Importar la cartera desde la planilla | 3 | Terminado | `criterios_aceptacion.md`, capturas h02_01 a h02_06 |
| RF-08 | Preparar la jornada para trabajar sin señal | en H07 | Ficha en Confluence | Cuatro criterios con prueba automática o de punta a punta |
| RF-09 | Importar la cartera con revisión previa | en H02 | Ficha en Confluence | Cinco criterios con prueba automática |

Puntos construidos: **11** (sobre la capacidad de 8, aceptado en la planificación, D18). 79 pruebas automáticas
aprobadas, también contra PostgreSQL en el ambiente de despliegue.

Además, fuera de las historias: el ambiente de despliegue (PostgreSQL, gunicorn y Caddy con HTTPS en Docker),
documentado en `docs/despliegue.md`.

## Demostración sugerida (5 minutos)

1. **H02.** Entrar como `asistente`, Cartera > Importar planilla, elegir `docs/entrega1/a03/planilla_actual.csv`
   y Revisar: 144 filas, 139 equipos nuevos, 5 que no se importan con su motivo y 14 con avisos (sobre una
   cartera vacía; con la cartera de demostración casi todo sale "sin cambios", que también muestra que no duplica).
2. **H07.** Entrar como `luis` con señal: "Listo para trabajar sin señal hasta el...". Cortar la señal
   (F12 > Red > Sin conexión, o desconectar el wifi), recargar: abre igual y avisa de qué hora es la copia.
   Avanzar unos días, abrir una visita y mostrar la última mantención del equipo. Registrar una mantención:
   queda "En el celular". Devolver la señal: se envía sola.
3. Mostrar `prueba_sin_senal.md`: la prueba con el servidor apagado y el navegador cerrado dos veces.

## Resultado de la revisión

Registrada el 26 de noviembre de 2026. Como en las entregas anteriores, la aceptación del jefe técnico es
**simulación**.

- Se recorrieron H07 y H02 en pantalla de celular de 400 px con bases aparte; cada paso dio el resultado esperado.
- Las 79 pruebas automáticas se corrieron el 26 de noviembre con SQLite y con PostgreSQL: todas aprobadas.
- H07 y H02 cumplen su criterio de término y pasaron a Terminado en JIRA. Con ellas, las cuatro épicas quedan
  con todas sus historias terminadas y pasan a Terminado.
- La página de Confluence quedó en la versión 12.

## Qué se aprendió

- **La prueba de punta a punta encontró un defecto que las pruebas automáticas no veían:** sin señal, Firefox
  mostraba respuestas viejas de la API sacadas de su caché, sin el aviso "Sin señal". Se corrigió con
  `Cache-Control: no-store` en la API. Probar con el servidor apagado y la aplicación cerrada, no solo con la red
  cortada, fue lo que lo mostró.
- **H07 costó menos que su estimación** porque S01 y H06 ya habían resuelto lo difícil (guardar en el celular,
  envío automático, reintentos). La estimación de 8 puntos se hizo antes de S01.
- **H02 reutilizó A03:** las mismas reglas que se usaron a mano en la Entrega 1 dan los mismos hallazgos
  (4 repetidos, 1 retirado, 9 sin fecha, 5 comunas) al importar.
- **Riesgos:** R1 (sin señal) baja otra vez de prioridad: la jornada completa funciona sin señal; sigue abierto
  hasta probar en un celular real. R3 (planilla con errores) queda controlado: la importación no deja entrar
  repetidos ni retirados y muestra todo antes de guardar.

## Pendiente

| | |
|---|---|
| Pendiente | Publicar con un dominio propio y probar en un celular real dentro de un subterráneo (RNF-01, H07). |
| En el backlog | Comuna de una lista (D13); plan del fabricante, componentes por reemplazar y número de instalación (acta de A05). |
| Próxima acción | Cierre del proyecto: el backlog del plan está completo. |
