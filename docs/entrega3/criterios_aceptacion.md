# Entrega 3 · Criterios de aceptación y cómo se comprobaron

Cada criterio tiene una prueba automática (`python manage.py test`, 62 pruebas en total) o una captura
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
