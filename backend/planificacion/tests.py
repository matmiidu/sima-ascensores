from collections import Counter
from datetime import date
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from cartera.models import Ascensor, Edificio, Tecnico

from .calendario import dias_habiles, generar_calendario
from .models import Feriado, Visita


def edificio(nombre, tecnico, n_ascensores, comuna="Providencia"):
    e = Edificio.objects.create(nombre=nombre, direccion=f"{nombre} 100", comuna=comuna,
                                tipo_uso="residencial", tecnico_asignado=tecnico)
    for i in range(n_ascensores):
        Ascensor.objects.create(edificio=e, identificador=f"A{i + 1}", tipo="electrico")
    return e


class CalendarioTests(TestCase):
    """Criterios de aceptación de H03."""

    def setUp(self):
        self.juan = Tecnico.objects.create(nombre="Juan", capacidad_diaria=4)
        self.camila = Tecnico.objects.create(nombre="Camila", capacidad_diaria=4)
        for i in range(10):
            edificio(f"Edificio {i}", self.juan if i % 2 else self.camila, 1 + i % 3)

    def test_ningun_equipo_activo_queda_sin_visita(self):
        generar_calendario(2026, 11)
        activos = Ascensor.objects.filter(activo=True).count()
        self.assertEqual(Visita.objects.filter(mes=date(2026, 11, 1)).count(), activos)

    def test_solo_dias_habiles_sin_feriados(self):
        generar_calendario(2026, 10)
        habiles = set(dias_habiles(2026, 10))
        self.assertNotIn(date(2026, 10, 12), habiles)  # lunes feriado
        for v in Visita.objects.all():
            self.assertLess(v.fecha.weekday(), 5)
            self.assertFalse(Feriado.objects.filter(fecha=v.fecha).exists())

    def test_los_ascensores_de_un_edificio_van_el_mismo_dia_con_su_tecnico(self):
        generar_calendario(2026, 11)
        for e in Edificio.objects.all():
            visitas = Visita.objects.filter(ascensor__edificio=e)
            self.assertEqual(len({v.fecha for v in visitas}), 1)
            self.assertEqual({v.tecnico for v in visitas}, {e.tecnico_asignado})

    def test_generar_dos_veces_no_duplica(self):
        generar_calendario(2026, 11)
        r = generar_calendario(2026, 11)
        self.assertEqual(r.creadas, 0)
        self.assertEqual(Visita.objects.count(), Ascensor.objects.count())

    def test_volver_a_generar_agrega_solo_lo_nuevo(self):
        generar_calendario(2026, 11)
        edificio("Nuevo", self.juan, 2)
        r = generar_calendario(2026, 11)
        self.assertEqual(r.creadas, 2)

    def test_reparte_los_edificios_a_lo_largo_de_todo_el_mes(self):
        generar_calendario(2026, 11)
        dias = dias_habiles(2026, 11)
        for tecnico in (self.juan, self.camila):
            visitas = Visita.objects.filter(tecnico=tecnico)
            edificios = visitas.values("ascensor__edificio").distinct().count()
            fechas = sorted(set(visitas.values_list("fecha", flat=True)))
            # Cada edificio en su propio día y el último en la segunda mitad del mes.
            self.assertEqual(len(fechas), edificios)
            self.assertGreater(fechas[-1], dias[len(dias) // 2])

    def test_ascensor_agregado_despues_va_el_mismo_dia_que_su_edificio(self):
        generar_calendario(2026, 11)
        e = Edificio.objects.get(nombre="Edificio 1")
        dia = Visita.objects.filter(ascensor__edificio=e).first().fecha
        nuevo = Ascensor.objects.create(edificio=e, identificador="A9", tipo="electrico")
        self.assertEqual(generar_calendario(2026, 11).creadas, 1)
        visita = Visita.objects.get(ascensor=nuevo)
        self.assertEqual((visita.fecha, visita.tecnico), (dia, self.juan))

    def test_reemplazar_conserva_las_visitas_realizadas(self):
        generar_calendario(2026, 11)
        hecha = Visita.objects.first()
        hecha.estado = Visita.Estado.REALIZADA
        hecha.save()
        generar_calendario(2026, 11, reemplazar=True)
        self.assertTrue(Visita.objects.filter(pk=hecha.pk).exists())
        self.assertEqual(Visita.objects.count(), Ascensor.objects.count())

    def test_no_programa_equipos_inactivos(self):
        Ascensor.objects.filter(identificador="A1").update(activo=False)
        generar_calendario(2026, 11)
        self.assertFalse(Visita.objects.filter(ascensor__activo=False).exists())

    def test_edificio_sin_tecnico_se_asigna_y_se_avisa(self):
        edificio("Huérfano", None, 1)
        r = generar_calendario(2026, 11)
        self.assertTrue(any("Huérfano" in a for a in r.advertencias))
        self.assertTrue(Visita.objects.filter(ascensor__edificio__nombre="Huérfano").exists())

    def test_respeta_la_capacidad_diaria(self):
        generar_calendario(2026, 11)
        por_dia = Counter((v.tecnico_id, v.fecha) for v in Visita.objects.all())
        self.assertLessEqual(max(por_dia.values()), 4)

    def test_avisa_cuando_la_carga_supera_la_capacidad(self):
        Tecnico.objects.update(capacidad_diaria=1)
        edificio("Grande", self.juan, 30)
        r = generar_calendario(2026, 11)
        self.assertTrue(any("supera su capacidad" in a for a in r.advertencias))
        self.assertEqual(Visita.objects.count(), Ascensor.objects.count())


class CalendarioApiTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(get_user_model().objects.create_user("jefe", password="x", is_staff=True))
        t = Tecnico.objects.create(nombre="Juan")
        edificio("Mirador", t, 3)

    def test_generar_y_consultar_el_resumen(self):
        r = self.client.post("/api/calendario/generar/", {"anio": 2026, "mes": 11}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["cobertura"]["sin_visita"], [])
        r = self.client.get("/api/calendario/resumen/?mes=2026-11")
        self.assertEqual(r.data["con_visita"], 3)
        self.assertEqual(r.data["carga"][0]["total"], 3)
        self.assertEqual(r.data["ultima_generacion"]["visitas_creadas"], 3)

    def test_filtra_visitas_por_mes_y_tecnico(self):
        self.client.post("/api/calendario/generar/", {"anio": 2026, "mes": 11}, format="json")
        t = Tecnico.objects.get().id
        self.assertEqual(len(self.client.get(f"/api/visitas/?mes=2026-11&tecnico={t}").data), 3)
        self.assertEqual(len(self.client.get("/api/visitas/?mes=2026-12").data), 0)

    def test_mes_invalido(self):
        r = self.client.post("/api/calendario/generar/", {"anio": 2026, "mes": 13}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.get("/api/calendario/resumen/?mes=noviembre").status_code, 400)

    def test_mover_una_visita_fuera_de_su_mes_se_rechaza(self):
        self.client.post("/api/calendario/generar/", {"anio": 2026, "mes": 11}, format="json")
        v = Visita.objects.first()
        r = self.client.patch(f"/api/visitas/{v.id}/", {"fecha": "2026-12-02"}, format="json")
        self.assertEqual(r.status_code, 400)


class MisVisitasTests(APITestCase):
    """Criterios de aceptación de H04: el técnico ve sus visitas del día."""

    HOY = date(2026, 11, 18)  # miércoles

    def setUp(self):
        reloj = mock.patch("planificacion.views.timezone.localdate", return_value=self.HOY)
        reloj.start()
        self.addCleanup(reloj.stop)
        User = get_user_model()
        self.luis = Tecnico.objects.create(nombre="Luis Muñoz", usuario=User.objects.create_user("luis", password="x"))
        self.camila = Tecnico.objects.create(nombre="Camila Rojas", usuario=User.objects.create_user("camila", password="x"))
        self.plaza = edificio("Edificio Plaza", self.luis, 2, comuna="Santiago")
        self.torre = edificio("Torre Andes", self.camila, 1, comuna="Las Condes")
        for a in self.plaza.ascensores.all():
            self.visita(a, self.luis, self.HOY)
        self.visita(self.torre.ascensores.get(), self.camila, self.HOY)
        self.client.force_authenticate(self.luis.usuario)

    def visita(self, ascensor, tecnico, fecha, **extra):
        return Visita.objects.create(ascensor=ascensor, tecnico=tecnico, mes=fecha.replace(day=1), fecha=fecha, **extra)

    def test_el_tecnico_ve_solo_sus_visitas_de_hoy(self):
        r = self.client.get("/api/mis-visitas/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["tecnico"]["nombre"], "Luis Muñoz")
        self.assertEqual(r.data["fecha"], "2026-11-18")
        self.assertEqual([v["ascensor_identificador"] for v in r.data["visitas"]], ["A1", "A2"])
        self.assertEqual({v["tecnico"] for v in r.data["visitas"]}, {self.luis.id})

    def test_cada_visita_dice_a_que_edificio_ir_y_a_quien_llamar(self):
        self.plaza.administrador_nombre, self.plaza.administrador_telefono = "Patricia Fuentes", "+56 2 2598 2203"
        self.plaza.save()
        v = self.client.get("/api/mis-visitas/").data["visitas"][0]
        self.assertEqual((v["edificio_nombre"], v["direccion"], v["comuna"]),
                         ("Edificio Plaza", "Edificio Plaza 100", "Santiago"))
        self.assertEqual((v["administrador_nombre"], v["administrador_telefono"]),
                         ("Patricia Fuentes", "+56 2 2598 2203"))
        self.assertEqual(v["paradas"], 2)
        self.assertEqual(v["estado"], "programada")

    def test_puede_revisar_otro_dia(self):
        otro = edificio("Edificio Parque", self.luis, 1, comuna="Santiago")
        self.visita(otro.ascensores.get(), self.luis, date(2026, 11, 19))
        r = self.client.get("/api/mis-visitas/?fecha=2026-11-19")
        self.assertEqual([v["edificio_nombre"] for v in r.data["visitas"]], ["Edificio Parque"])
        self.assertEqual(r.data["hoy"], "2026-11-18")
        self.assertEqual(self.client.get("/api/mis-visitas/?fecha=mañana").status_code, 400)
        # Un día sin visitas dice cuándo es la siguiente.
        self.assertEqual(self.client.get("/api/mis-visitas/").data["proxima_fecha"], "2026-11-19")
        r = self.client.get("/api/mis-visitas/?fecha=2026-11-20")
        self.assertEqual((r.data["visitas"], r.data["proxima_fecha"]), ([], None))

    def test_las_visitas_atrasadas_del_mes_aparecen_aparte(self):
        pendiente = edificio("Edificio Parque", self.luis, 1, comuna="Santiago")
        hecha = edificio("Edificio Portal", self.luis, 1, comuna="Santiago")
        octubre = edificio("Edificio Nogales", self.luis, 1, comuna="Santiago")
        self.visita(pendiente.ascensores.get(), self.luis, date(2026, 11, 16))
        self.visita(hecha.ascensores.get(), self.luis, date(2026, 11, 13), estado=Visita.Estado.REALIZADA)
        self.visita(octubre.ascensores.get(), self.luis, date(2026, 10, 30))
        r = self.client.get("/api/mis-visitas/")
        self.assertEqual([v["edificio_nombre"] for v in r.data["atrasadas"]], ["Edificio Parque"])
        self.assertEqual(len(r.data["visitas"]), 2)

    def test_el_jefe_tecnico_elige_de_quien_son_las_visitas(self):
        self.client.force_authenticate(get_user_model().objects.create_user("jefe", password="x", is_staff=True))
        self.assertEqual(self.client.get("/api/mis-visitas/").status_code, 400)
        r = self.client.get(f"/api/mis-visitas/?tecnico={self.camila.id}")
        self.assertEqual([v["edificio_nombre"] for v in r.data["visitas"]], ["Torre Andes"])

    def test_un_usuario_sin_tecnico_asociado_no_ve_visitas(self):
        self.client.force_authenticate(get_user_model().objects.create_user("nuevo", password="x"))
        r = self.client.get("/api/mis-visitas/")
        self.assertEqual(r.status_code, 403)
        self.assertIn("no está asociado a un técnico", r.data["detail"])

    def test_un_tecnico_no_genera_ni_cambia_el_calendario(self):
        r = self.client.post("/api/calendario/generar/", {"anio": 2026, "mes": 12}, format="json")
        self.assertEqual(r.status_code, 403)
        v = Visita.objects.filter(tecnico=self.luis).first()
        cambio = self.client.patch(f"/api/visitas/{v.id}/", {"fecha": "2026-11-20"}, format="json")
        self.assertEqual(cambio.status_code, 403)
        self.assertEqual(self.client.delete(f"/api/visitas/{v.id}/").status_code, 403)
        self.assertEqual(Visita.objects.filter(mes=date(2026, 12, 1)).count(), 0)
