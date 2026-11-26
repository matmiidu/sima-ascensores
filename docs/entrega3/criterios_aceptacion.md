# Entrega 3 · Criterios de aceptación y cómo se comprobaron

Cada criterio tiene una prueba automática (`python manage.py test`, 68 pruebas en total) o una captura
en `capturas/`, tomada en pantalla de celular (400 px).

## H10 · Alertar certificaciones por vencer (SIMA-22, 3 puntos)

> Como jefe técnico, quiero una alerta de las certificaciones por vencer para avisar al administrador con anticipación.

Requisito: RF-06 (ficha en Confluence). Prototipo: P-07, maqueta revisada antes de construir (captura 00).
Rama: `feature/SIMA-22-alertas`, unida a `main`.

| Criterio | Comprobación |
|---|---|
| CA-01 El jefe técnico ve aparte las certificaciones vencidas, las que vencen en los próximos 60 días y los ascensores sin fecha, ordenadas por fecha | `test_separa_vencidas_por_vencer_y_sin_fecha` · capturas 01 y 02 |
| CA-02 No se avisan las certificaciones vigentes más allá del plazo ni los ascensores o edificios inactivos | `test_no_avisa_las_vigentes_mas_alla_del_plazo_ni_los_equipos_inactivos` |
| CA-03 Cada alerta trae el contacto del administrador y abre un correo ya escrito para avisarle | `test_cada_alerta_trae_el_contacto_del_administrador` · captura 01 |
| CA-04 El plazo de anticipación se puede cambiar (1 a 365 días) y un valor inválido se rechaza | `test_el_plazo_de_anticipacion_se_puede_cambiar_y_se_valida` |
| CA-05 Un técnico no ve las alertas: solo el jefe técnico | `test_un_tecnico_no_ve_las_alertas` |

Con los datos de demostración, el 24 de noviembre de 2026 la pantalla muestra 20 ascensores que necesitan
aviso: 10 vencidas y 10 que vencen en los próximos 60 días.

Queda fuera de esta historia registrar en SIMA que el aviso se envió: el correo sale desde la aplicación de
correo del jefe técnico.

## A05 · Revisar el formato del informe contra la OGUC (SIMA-31, acción del riesgo R5)

Se hizo antes de construir H09, como pide el plan. Acta en `a05/acta_A05.md` (la reunión con el jefe técnico
es SIMULACIÓN; la lectura de la norma y la comparación con los datos de SIMA sí se ejecutaron). Texto vigente
del artículo 5.9.5 en `a05/OGUC_art_5.9.5_extracto.txt` y maqueta P-06 en `a05/maqueta_P-06.png`.
Rama: `feature/SIMA-31-formato-informe`, unida a `main`.

| Criterio de término | Comprobación |
|---|---|
| Acción ejecutada | Acta con las nueve exigencias de la norma (E1 a E9), qué tiene SIMA para cada una y el formato acordado |
| Riesgo reevaluado | R5 baja de prioridad Media a Baja; no se cierra (sección 5 del acta) |

## H09 · Generar el informe mensual en PDF (SIMA-21, 5 puntos)

> Como administrador de edificio, quiero recibir el informe mensual de mantención en PDF para archivarlo y mostrarlo al certificador.

Requisito: RF-07 (ficha en Confluence). Prototipo: P-06, maqueta revisada en A05. Depende de H06 y de A05.
Rama: `feature/SIMA-21-informe-pdf`, unida a `main`.

| Criterio | Comprobación |
|---|---|
| CA-01 El informe trae una hoja por ascensor con su identificación, la fecha de la mantención, el técnico y los ocho puntos del checklist con su resultado y observación | `test_cada_ascensor_trae_su_mantencion_y_las_tareas_revisadas` · captura 07 · `ejemplos_informe/` |
| CA-02 Un equipo detenido aparece en la primera hoja y en su sección, con la falla y el aviso de que no se usa hasta la conformidad del mantenedor | `test_un_equipo_detenido_se_ve_en_el_resumen_con_su_falla` · capturas 06 y 07 |
| CA-03 Si falta una mantención del mes, el informe sale como parcial y dice cuándo está programada la visita; la lista del mes muestra cuántas faltan por edificio | `test_si_falta_una_mantencion_el_informe_es_parcial` · `test_la_lista_del_mes_dice_que_informes_estan_completos` · capturas 03, 06 y 08 |
| CA-04 Cada ascensor trae el registro del año (fecha y técnico de cada mantención) y su certificación con la periodicidad que fija la OGUC según el destino | `test_registro_del_anio_y_certificacion_segun_el_destino` · captura 07 |
| CA-05 Solo el jefe técnico descarga informes; un mes mal escrito o sin visitas se rechaza con un mensaje | `test_solo_el_jefe_tecnico_y_con_un_mes_valido` · `rechazo_tecnico.json` en la evidencia |

Recorrido en pantalla de celular (400 px), con una base de demostración aparte
(`Entrega_3_SIMA/_fuente/base_evidencia.py`): la pantalla Informes muestra primero los edificios con el
informe completo; el Edificio Plaza aparece con 2 de 3 mantenciones y 1 equipo detenido; el botón descarga
`Informe_Edificio_Plaza_2026-11.pdf` (4 hojas, parcial) y ofrece escribir al administrador con el correo ya
redactado, para adjuntar el archivo. Las mantenciones de octubre de esa base son datos de ejemplo escritos
directo en la base, porque SIMA ya no deja registrar un mes terminado.

Decisión técnica (D17): el informe EV2 nombraba WeasyPrint. WeasyPrint necesita las bibliotecas Pango y GTK
del sistema, que en Windows se instalan aparte; el equipo trabaja en Windows. Se usó xhtml2pdf, que también
convierte una plantilla HTML en PDF y se instala solo con `pip`. La plantilla
(`backend/terreno/templates/terreno/informe_mensual.html`) sirve para cualquiera de las dos.

Queda fuera de esta historia (backlog, acta de A05, sección 4): el plan del fabricante por modelo, los
componentes por reemplazar con su plazo y el número de identificación de la instalación que fija la OGUC.
