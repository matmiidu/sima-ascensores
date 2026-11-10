# Entrega 2 · Criterios de aceptación y cómo se comprobaron

Cada criterio tiene una prueba automática (`python manage.py test`, 56 pruebas en total) o una captura
en `capturas/`, tomada en pantalla de celular.

## H04 · Ver mis visitas del día (SIMA-19, 2 puntos)

> Como técnico, quiero ver mis visitas del día en el celular para saber a qué edificio ir.

| Criterio | Comprobación |
|---|---|
| Cada técnico entra con su propio usuario y ve solo sus visitas | `test_el_tecnico_ve_solo_sus_visitas_de_hoy` · `test_la_aplicacion_sabe_quien_entro` · `test_cada_tecnico_queda_con_su_usuario` |
| Al entrar ve las visitas de hoy, agrupadas por edificio, con dirección, equipo y contacto del administrador | `test_cada_visita_dice_a_que_edificio_ir_y_a_quien_llamar` · captura 01 |
| Ve cuántos equipos del día lleva registrados | capturas 01 y 08 |
| Las visitas atrasadas del mes aparecen aparte | `test_las_visitas_atrasadas_del_mes_aparecen_aparte` · captura 01 |
| Puede revisar otro día; si no tiene visitas, se le dice cuándo es la siguiente | `test_puede_revisar_otro_dia` · captura 02 |
| Un técnico consulta, pero no modifica la cartera ni el calendario | `test_un_tecnico_consulta_la_cartera_pero_no_la_modifica` · `test_un_tecnico_no_genera_ni_cambia_el_calendario` |
| El jefe técnico puede mirar las visitas de cualquier técnico; un usuario sin técnico asociado no ve visitas | `test_el_jefe_tecnico_elige_de_quien_son_las_visitas` · `test_un_usuario_sin_tecnico_asociado_no_ve_visitas` |
| Funciona en la pantalla del celular | capturas 01 y 02 |

## H06 · Completar el checklist en el celular (SIMA-20, 5 puntos)

> Como técnico, quiero completar el checklist de mantención desde el celular para no transcribirlo después.

### RF-02 Registrar el checklist de la visita (SIMA-33)

| Criterio | Comprobación |
|---|---|
| CA-01 Checklist incompleto: no se guarda, indica qué punto falta y la visita sigue pendiente | `test_checklist_incompleto_no_se_guarda_e_indica_el_punto` · captura 03 |
| CA-02 Checklist completo: la visita queda Realizada en el calendario del jefe técnico, con fecha, hora y técnico | `test_checklist_completo_deja_la_visita_realizada` · capturas 05, 10 y 12 |
| CA-03 Observación sin escribir: no se guarda e indica en qué punto falta | `test_observacion_sin_escribir_no_se_guarda` · captura 04 |
| CA-04 Visita ya registrada: no se guarda otra vez y avisa la fecha y la hora del registro anterior | `test_no_se_registra_dos_veces_la_misma_visita` · captura 09 |
| Hay que indicar si el equipo quedó operativo | `test_debe_indicar_si_el_equipo_quedo_operativo` |
| Una visita futura no se registra, tampoco con el reloj del celular adelantado | `test_no_se_registra_una_visita_futura` |
| Una visita atrasada se registra mientras siga siendo su mes | `test_visita_atrasada_del_mismo_mes_se_registra` · `test_visita_de_un_mes_que_ya_termino_no_se_registra` |
| Solo el técnico de la visita registra su mantención | `test_otro_tecnico_no_registra_la_visita` · `test_el_jefe_tecnico_no_registra_por_el_tecnico` · `test_sin_sesion_no_se_registra` |

### RF-03 Exigir la descripción de la falla cuando el equipo queda detenido (SIMA-35)

| Criterio | Comprobación |
|---|---|
| CA-01 Falla sin describir: no se guarda, indica que falta y conserva lo respondido | `test_falla_sin_describir_no_se_guarda` · captura 06 |
| CA-02 Falla descrita: la visita queda Realizada, el equipo aparece detenido y el jefe técnico ve la falla | `test_falla_descrita_queda_a_la_vista_del_jefe_tecnico` · capturas 07, 10 y 11 |

### RNF-01 Confiabilidad sin conexión del checklist (SIMA-34)

| Criterio | Comprobación |
|---|---|
| CA-01 Sin señal: 10 checklists guardados siguen en el celular, como pendientes, al cerrar y abrir la aplicación | Prueba en el navegador (ver `RNF01_resultado.md`) · capturas rnf01_01 a rnf01_03 |
| CA-02 Vuelve la señal: los 10 llegan en 60 segundos o menos, ninguno repetido, sin que el técnico haga nada | Llegaron los 10 en 5,3 segundos · captura rnf01_04 · `test_diez_checklists_guardados_sin_senal_llegan_una_sola_vez` · `test_reenvio_con_el_mismo_id_local_no_duplica` |
| Vale la hora en que se guardó en el celular, no la de llegada | `test_vale_la_hora_en_que_se_guardo_en_el_celular` |

RNF-01 pide además repetir la prueba en un celular real dentro de un subterráneo. Eso sigue pendiente:
requiere publicar la aplicación con HTTPS.

## A02

Ver `a02/acta_A02.md`.
