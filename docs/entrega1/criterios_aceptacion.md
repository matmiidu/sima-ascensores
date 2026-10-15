# Entrega 1 · Criterios de aceptación y cómo se comprobaron

Cada criterio tiene una prueba automática (`python manage.py test`) o una captura.

## H01 · Registrar edificios y ascensores (SIMA-16, 3 puntos)

> Como jefe técnico, quiero registrar edificios y ascensores con su tipo de uso para saber qué equipos mantiene la empresa.

| Criterio | Comprobación |
|---|---|
| Se registra un edificio con nombre, dirección, comuna, **tipo de uso** y técnico asignado | `test_registra_edificio_con_tipo_de_uso` · captura 02 |
| El tipo de uso es obligatorio y se elige de una lista (residencial, oficinas, comercial, salud, educación, mixto) | `test_tipo_de_uso_es_obligatorio_y_de_la_lista` |
| No se puede registrar dos veces la misma dirección en la misma comuna | `test_no_duplica_la_misma_direccion` |
| Se agregan ascensores a un edificio, con tipo, uso, paradas y vencimiento de la certificación | `test_registra_ascensores_y_aparecen_en_su_edificio` · captura 03 |
| El identificador del ascensor no se repite dentro del edificio | `test_identificador_unico_dentro_del_edificio` |
| La cartera se puede buscar por nombre, dirección o comuna y filtrar por tipo de uso | `test_busca_por_comuna_y_filtra_por_tipo_de_uso` · captura 01 |
| La ficha del edificio muestra si cada certificación está vigente, por vencer (60 días) o vencida | captura 03 |
| Solo se entra con usuario y clave | `test_exige_sesion` |
| Funciona en la pantalla del celular | capturas 01 a 03 (400 px de ancho) |

## H03 · Generar el calendario mensual (SIMA-18, 3 puntos)

> Como jefe técnico, quiero generar el calendario mensual de mantenciones por técnico para que ningún equipo quede sin visita.

| Criterio | Comprobación |
|---|---|
| Con un botón se genera el mes completo: **cada ascensor activo queda con una visita** | `test_ningun_equipo_activo_queda_sin_visita` · captura 05 (142 de 142) |
| Solo se programan días hábiles: ni fines de semana ni feriados | `test_solo_dias_habiles_sin_feriados` |
| Los ascensores de un edificio se visitan el mismo día y con el técnico asignado | `test_los_ascensores_de_un_edificio_van_el_mismo_dia_con_su_tecnico` |
| No se supera la capacidad diaria del técnico; si la carga no cabe, igual se programa y se avisa | `test_respeta_la_capacidad_diaria` · `test_avisa_cuando_la_carga_supera_la_capacidad` |
| Un edificio sin técnico se asigna al menos cargado y se avisa | `test_edificio_sin_tecnico_se_asigna_y_se_avisa` |
| Generar dos veces no duplica; si se agregan equipos, solo se programan los nuevos | `test_generar_dos_veces_no_duplica` · `test_volver_a_generar_agrega_solo_lo_nuevo` |
| "Volver a repartir" no borra las visitas ya realizadas | `test_reemplazar_conserva_las_visitas_realizadas` |
| Se ve el calendario por día y por técnico, con la cobertura del mes | capturas 05 a 07 |

## S01 y A03

Ver `S01_resultado.md` y `a03/acta_A03.md`.
