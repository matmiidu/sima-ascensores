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

## H02 · Importar la cartera desde la planilla (SIMA-24, 3 puntos)

> Como asistente administrativa, quiero importar la cartera desde la planilla actual para no digitar 140 equipos.

Requisito: RF-09 (ficha en Confluence). Depende de A03, cuya planilla (`docs/entrega1/a03/planilla_actual.csv`)
se usó para probarla. Rama: `feature/SIMA-24-importar-planilla`, unida a `main`. La asistente entra con el usuario
`asistente`, que es personal de la oficina, igual que el jefe técnico.

| Criterio | Comprobación |
|---|---|
| CA-01 Antes de guardar se ve qué pasará con cada fila; los defectos que encontró A03 aparecen con su motivo (4 repetidos, 1 retirado, 9 sin fecha, 5 comunas mal escritas) | `test_la_revision_muestra_lo_mismo_que_encontro_a03_sin_guardar_nada` · capturas h02_01 a h02_03 |
| CA-02 Al confirmar se crean los equipos válidos y sus edificios, con el técnico de la planilla; los sin fecha quedan "sin fecha" para Certificaciones | `test_al_confirmar_se_guarda_todo_y_repetir_no_duplica` · capturas h02_04 y h02_05 |
| CA-03 Importar de nuevo no duplica nada; si un equipo trae otra fecha, se muestra el cambio y se corrige | `test_al_confirmar_se_guarda_todo_y_repetir_no_duplica` · `test_un_equipo_con_otro_vencimiento_se_actualiza` · captura h02_06 |
| CA-04 La misma planilla se lee igual desde CSV o desde Excel (.xlsx) | `test_tambien_lee_excel` |
| CA-05 Un archivo que no es planilla o sin las columnas obligatorias se rechaza y dice qué falta; un técnico no puede importar | `test_archivo_o_columnas_invalidas_se_rechazan_con_un_mensaje` · `test_solo_el_personal_de_la_oficina_importa` |

Recorrido en pantalla de celular con una base aparte, cartera vacía y la planilla de A03: 144 filas revisadas,
139 equipos nuevos en 62 edificios, 5 filas no importadas y 14 con avisos; la segunda vez, 139 sin cambios y
"No hay nada que importar".
