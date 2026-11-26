# Entrega 4 · Criterios de aceptación y cómo se comprobaron

Cada criterio tiene una prueba automática (`python manage.py test`) o una captura en `capturas/`,
tomada en pantalla de celular (400 px).

## H07 · Trabajar sin conexión de punta a punta (SIMA-23, 8 puntos)

> Como técnico, quiero trabajar toda la visita sin conexión para registrar en salas de máquinas sin señal.

Requisito: RF-08 (ficha en Confluence). Depende de S01 y H06. Rama: `feature/SIMA-23-sin-conexion`, unida a `main`.

| Criterio | Comprobación |
|---|---|
| CA-01 Con señal, el celular guarda hoy y los seis días siguientes, cada uno igual que en Mis visitas, y avisa hasta qué día | `test_la_jornada_trae_hoy_y_los_seis_dias_siguientes` · `test_cambiar_los_dias_y_rechazar_un_valor_invalido` · captura h07_01 |
| CA-02 Sin señal ni servidor, la aplicación abre, avisa de qué hora es la copia y deja revisar cualquier día guardado; un día no guardado dice hasta cuándo llega la jornada | `test_las_respuestas_de_la_api_no_quedan_en_la_cache_del_navegador` · capturas h07_02 a h07_04 |
| CA-03 Durante la visita se ve la última mantención del equipo (fecha, técnico, si quedó detenido, falla y observaciones), también sin señal | `test_cada_visita_trae_la_ultima_mantencion_del_equipo` · captura h07_05 |
| CA-04 Lo registrado sin señal sobrevive a cerrar la aplicación y se envía solo al volver la señal, una vez cada uno | Prueba de punta a punta (`prueba_sin_senal.md`): 5 de 5 en 3,6 s, sin repetidos · capturas h07_06 a h07_08 |
| Solo un técnico prepara su jornada | `test_solo_un_tecnico_prepara_su_jornada` |

Lo que se agregó sobre H06: el punto `/api/mis-visitas/jornada/`, la última mantención en cada visita, la
descarga automática de la jornada (al entrar, cada 30 minutos y después de cada envío) y el encabezado
`Cache-Control: no-store` en la API.
