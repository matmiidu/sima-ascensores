# Acta A05 · Revisión del formato del informe contra la OGUC

> **SIMULACIÓN.** Ascensores Altavía y su jefe técnico son ficticios. La reunión no ocurrió con
> una persona real: las opiniones y decisiones del jefe técnico son supuestos del caso, escritos
> para ejercitar la acción de respuesta al riesgo R5. Lo que sí se ejecutó es la lectura del texto
> vigente del artículo 5.9.5 de la OGUC y su comparación con los datos que SIMA ya registra
> (secciones 1 y 2).

| | |
|---|---|
| Elemento JIRA | SIMA-31 · A05 |
| Riesgo | R5: el contenido exigido al informe de mantención se interpreta sin revisar la norma |
| Entrega | Entrega 3 (16 – 29 de noviembre de 2026) |
| Responsable | Matias Valenzuela |
| Participan (simulado) | Jefe técnico de Ascensores Altavía |
| Material | Texto vigente del artículo 5.9.5 (`OGUC_art_5.9.5_extracto.txt`), registros de H06 y maqueta P-08 del informe |
| Bloquea a | SIMA-21 · H09 Generar el informe mensual en PDF |

## 1. Qué exige la norma (ejecutado)

Se leyó el artículo 5.9.5 de la Ordenanza General de Urbanismo y Construcciones en la Biblioteca del
Congreso Nacional el 25 de noviembre de 2026. El numeral 3 (Mantención) y el numeral 4
(Certificación) dicen lo siguiente sobre el informe:

| N.° | Exigencia del artículo 5.9.5 | Numeral |
|---|---|---|
| E1 | La mantención se hace una vez por mes como mínimo | 3 |
| E2 | En cada mantención, el mantenedor entrega al propietario o al administrador un informe | 3 |
| E3 | El informe muestra el seguimiento del plan anual de mantención especificado por el fabricante | 3 |
| E4 | El informe detalla las acciones preventivas y correctivas hechas a cada instalación | 3 |
| E5 | Cuando corresponda, el informe dice qué componentes deben reemplazarse y en qué plazo | 3 |
| E6 | Si hay riesgo inminente, el informe detalla las fallas y la instalación queda sin servicio hasta que el mantenedor dé su conformidad | 3 |
| E7 | En la cabina va un cuadro anual con la fecha de cada mantención, la empresa y el técnico que la hizo | 3 |
| E8 | El mantenedor está inscrito en el Registro de la Ley 20.296; el aviso de instalación no operativa lleva su número de inscripción y el número de identificación de la instalación | 3 |
| E9 | La certificación es cada 2 años en vivienda y cada 1 o 2 años en los demás destinos; para certificar, la carpeta del edificio debe tener los informes de mantención del período | 4 |

Hallazgo: la norma pide un informe **por mantención**, no uno al mes por edificio. Como SIMA programa
una sola mantención mensual por ascensor (H03), el informe mensual del edificio cumple si trae una
sección completa por cada ascensor.

## 2. Qué tiene SIMA para cada exigencia (ejecutado)

| N.° | Dato en SIMA | ¿Alcanza? |
|---|---|---|
| E1 | Una visita por ascensor y mes (H03, restricción en la base de datos) | Sí |
| E2 | Un registro de mantención por visita (H06) | Sí, falta armar el documento: es H09 |
| E3 | Checklist de ocho puntos, el mismo para todos los equipos (A02) | En parte: no es el plan del fabricante de cada equipo |
| E4 | Resultado de cada punto, observación escrita, observaciones generales y falla (RF-02, RF-03) | Sí |
| E5 | No hay un campo para componentes ni para el plazo | No |
| E6 | "El equipo quedó detenido" con la falla descrita (RF-03) | Sí |
| E7 | Fecha y técnico de cada visita realizada; la empresa es una sola | Sí |
| E8 | No hay número de inscripción ni el número de identificación de la instalación; el ascensor se reconoce por "A1", "A2" | No |
| E9 | Vencimiento de la certificación de cada ascensor (H01, H10) y tipo de uso del edificio | Sí |

## 3. Formato acordado para H09 (simulado)

El jefe técnico revisó la maqueta P-08 (`maqueta_P-08.png`) con la tabla anterior y acordó este
formato:

| Parte del informe | Contenido | Cubre |
|---|---|---|
| Encabezado | Empresa mantenedora, número de inscripción en el Registro de la Ley 20.296, mes del informe y fecha de emisión | E2, E8 |
| Edificio | Nombre, dirección, comuna, tipo de uso, administrador | E2 |
| Resumen | Ascensores del edificio, mantenciones registradas, equipos detenidos y mantenciones que faltan | E1 |
| Una sección por ascensor | Identificación (identificador, tipo, uso, marca, número de serie), fecha de la mantención, técnico y código del registro | E2, E7 |
| Tareas revisadas | Los ocho puntos del checklist con su resultado y la observación escrita | E3, E4 |
| Observaciones y falla | Observaciones del técnico; si el equipo quedó detenido, un recuadro "Equipo detenido" con la falla y el recordatorio de que no se usa hasta que el mantenedor dé su conformidad | E4, E6 |
| Certificación | Vencimiento y periodicidad según el destino del edificio (cada 2 años vivienda, cada 1 año equipamiento) | E9 |
| Registro del año | Por ascensor, fecha y técnico de cada mantención del año, para pasarlo al cuadro de la cabina | E7 |

Pedidos del jefe técnico (simulado) y decisión:

| Pedido | Decisión |
|---|---|
| Que un equipo detenido se vea en la primera hoja, no solo en su sección | Se acepta: el resumen nombra los equipos detenidos |
| Poder sacar el informe antes de que termine el mes, para un administrador que lo pide | Se acepta, pero el título dice "Informe parcial" y la sección del ascensor sin registro dice cuándo está programada su visita |
| Que el informe diga "plan del fabricante" para que el certificador no lo objete | Se rechaza: SIMA usa el checklist de Altavía y el informe lo dice tal cual. Escribir otra cosa sería justo el riesgo R5 |
| Agregar la firma del administrador | Se rechaza para esta entrega: la norma no la exige en el informe y la firma es H08 (Posterior) |

## 4. Lo que queda fuera de H09

Tres exigencias no se cubren con los datos actuales. Cambiar la cartera o el checklist modificaría
historias ya terminadas (H01 y H06), y el plan dice que todo cambio entra al backlog como elemento
nuevo. Quedan registradas como propuesta, sin tarjeta, igual que D13:

1. E3: cargar el plan anual de mantención del fabricante por modelo de ascensor y seguirlo en el checklist.
2. E5: en el checklist, marcar un componente por reemplazar y el plazo; hoy el técnico lo escribe en la observación.
3. E8: el número de identificación de la instalación que fija la OGUC (región y comuna del SII, rol de avalúo,
   número correlativo y letra) como campo de la cartera.

El número de inscripción de la empresa sí entra en H09, porque no cambia ninguna historia: es un dato
de configuración. Como Ascensores Altavía es ficticia, el informe dice que el número no está registrado.

## 5. Reevaluación del riesgo R5

| | Antes | Después |
|---|---|---|
| Probabilidad | Baja | Baja |
| Impacto | Alto | Medio: el formato ya se comparó con la norma y lo que falta está escrito |
| Prioridad | Media | **Baja** |

R5 no se cierra: lo que falta (sección 4) y la opinión de un certificador real siguen pendientes.
Se vuelve a revisar si un certificador observa el primer informe real.

## 6. Decisiones

1. El informe es mensual por edificio, con una sección completa por ascensor (D16).
2. El informe usa el nombre real del checklist ("Checklist de mantención mensual de Ascensores Altavía"),
   no el de plan del fabricante.
3. Los puntos E3, E5 y E8 quedan en el backlog como propuesta; H09 se construye con el formato de la sección 3.
4. La acción A05 se da por ejecutada y R5 baja a prioridad Baja.

Fecha del acta: 25 de noviembre de 2026.
