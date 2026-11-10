import uuid
from datetime import date, datetime, timedelta
from datetime import timezone as zona
from unittest import mock

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from cartera.models import Ascensor, Edificio, Tecnico
from planificacion.models import Visita

from .models import ChecklistPrueba, PuntoChecklist, RegistroMantencion


class SincronizacionTests(APITestCase):
    """S01: lo guardado sin señal llega una sola vez aunque el envío se repita."""

    def setUp(self):
        self.client.force_authenticate(get_user_model().objects.create_user("tecnico", password="x"))

    def test_reenvio_no_duplica(self):
        datos = {"id_local": str(uuid.uuid4()), "respuestas": {"frenos": "ok"},
                 "guardado_en_dispositivo": "2026-10-20T10:00:00-03:00"}
        self.assertEqual(self.client.post("/api/poc/checklists/", datos, format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/poc/checklists/", datos, format="json").status_code, 200)
        self.assertEqual(ChecklistPrueba.objects.count(), 1)


class ConVisitaDeHoy(APITestCase):
    """Datos comunes: el técnico Luis Muñoz con una visita programada para hoy."""

    def setUp(self):
        User = get_user_model()
        self.tecnico = Tecnico.objects.create(nombre="Luis Muñoz", usuario=User.objects.create_user("luis", password="x"))
        self.otro = Tecnico.objects.create(nombre="Camila Rojas", usuario=User.objects.create_user("camila", password="x"))
        self.jefe = User.objects.create_user("jefe", password="x", is_staff=True)
        edificio = Edificio.objects.create(nombre="Edificio Plaza", direccion="Lira 157", comuna="Santiago",
                                           tipo_uso="residencial", tecnico_asignado=self.tecnico)
        self.ascensor = Ascensor.objects.create(edificio=edificio, identificador="A3", tipo="electrico")
        hoy = timezone.localdate()
        self.visita = Visita.objects.create(ascensor=self.ascensor, tecnico=self.tecnico, mes=hoy.replace(day=1),
                                            fecha=hoy)
        # Los puntos del checklist los carga la migración 0003.
        self.puntos = list(PuntoChecklist.objects.filter(activo=True))
        self.client.force_authenticate(self.tecnico.usuario)

    def completo(self, **cambios):
        datos = {
            "visita": self.visita.id,
            "respuestas": [{"punto": p.id, "resultado": "bien"} for p in self.puntos],
            "operativo": True,
            "observaciones": "",
        }
        datos.update(cambios)
        return datos

    def registrar(self, datos):
        return self.client.post("/api/mantenciones/", datos, format="json")

    def sigue_programada(self):
        self.visita.refresh_from_db()
        return self.visita.estado == Visita.Estado.PROGRAMADA and not RegistroMantencion.objects.exists()


class RegistroMantencionTests(ConVisitaDeHoy):
    """H06 y RF-02: el técnico registra la mantención de una visita con el checklist completo."""

    def test_el_checklist_tiene_ocho_puntos(self):
        r = self.client.get("/api/puntos-checklist/")
        self.assertEqual([p["codigo"] for p in r.data], [f"P0{i}" for i in range(1, 9)])

    def test_checklist_completo_deja_la_visita_realizada(self):
        """RF-02 CA-02: queda Realizada, con fecha, hora y técnico, y se puede consultar."""
        r = self.registrar(self.completo())
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["codigo"], f"M-{r.data['id']:04d}")
        self.assertEqual(r.data["tecnico_nombre"], "Luis Muñoz")
        self.assertEqual(len(r.data["respuestas"]), 8)
        self.assertTrue(r.data["operativo"])
        self.visita.refresh_from_db()
        self.assertEqual(self.visita.estado, Visita.Estado.REALIZADA)
        # El jefe técnico la ve Realizada en su calendario y puede abrir el registro.
        self.client.force_authenticate(self.jefe)
        visita = self.client.get(f"/api/visitas/{self.visita.id}/").data
        self.assertEqual(visita["estado"], "realizada")
        self.assertEqual(visita["registro"]["codigo"], r.data["codigo"])
        self.assertIsNotNone(visita["registro"]["guardado_en_dispositivo"])
        historial = self.client.get(f"/api/mantenciones/?ascensor={self.ascensor.id}").data
        self.assertEqual([h["id"] for h in historial], [r.data["id"]])
        mes = self.visita.mes.strftime("%Y-%m")
        self.assertEqual(self.client.get(f"/api/calendario/resumen/?mes={mes}").data["realizadas"], 1)

    def test_checklist_incompleto_no_se_guarda_e_indica_el_punto(self):
        """RF-02 CA-01: no guarda, dice qué punto falta y la visita sigue pendiente."""
        datos = self.completo()
        falta = datos["respuestas"].pop(3)
        r = self.registrar(datos)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data["detail"], "No se guardó: falta responder 1 punto del checklist.")
        self.assertEqual(list(r.data["puntos"].keys()), [str(falta["punto"])])
        self.assertIn(self.puntos[3].descripcion, r.data["puntos"][str(falta["punto"])])
        self.assertTrue(self.sigue_programada())

    def test_respuesta_fuera_de_la_lista_cuenta_como_faltante(self):
        datos = self.completo()
        datos["respuestas"][0]["resultado"] = "regular"
        r = self.registrar(datos)
        self.assertEqual(r.status_code, 400)
        self.assertIn(str(self.puntos[0].id), r.data["puntos"])
        self.assertTrue(self.sigue_programada())

    def test_observacion_sin_escribir_no_se_guarda(self):
        """RF-02 CA-03: un punto con observación necesita la observación escrita."""
        datos = self.completo()
        datos["respuestas"][1] = {"punto": self.puntos[1].id, "resultado": "observacion", "comentario": " "}
        r = self.registrar(datos)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data["detail"], "No se guardó: falta escribir la observación de 1 punto.")
        self.assertIn("Escribe la observación", r.data["puntos"][str(self.puntos[1].id)])
        self.assertTrue(self.sigue_programada())
        datos["respuestas"][1]["comentario"] = "Cable con desgaste leve; revisar el próximo mes"
        r = self.registrar(datos)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["respuestas"][1]["comentario"], "Cable con desgaste leve; revisar el próximo mes")

    def test_debe_indicar_si_el_equipo_quedo_operativo(self):
        r = self.registrar(self.completo(operativo=None))
        self.assertEqual(r.status_code, 400)
        self.assertIn("operativo", r.data)
        self.assertTrue(self.sigue_programada())

    def test_no_se_registra_dos_veces_la_misma_visita(self):
        """RF-02 CA-04: avisa la fecha y la hora del registro anterior."""
        primero = self.registrar(self.completo())
        self.assertEqual(primero.status_code, 201)
        r = self.registrar(self.completo())
        self.assertEqual(r.status_code, 409)
        cuando = timezone.localtime(RegistroMantencion.objects.get().guardado_en_dispositivo)
        self.assertEqual(
            r.data["detail"],
            f"Esta visita ya fue registrada el {cuando:%d-%m-%Y a las %H:%M}. No se puede registrar dos veces.",
        )
        self.assertEqual(RegistroMantencion.objects.count(), 1)

    def test_no_se_registra_una_visita_futura(self):
        self.visita.fecha = timezone.localdate() + timedelta(days=1)
        self.visita.mes = self.visita.fecha.replace(day=1)
        self.visita.save()
        r = self.registrar(self.completo())
        self.assertEqual(r.status_code, 400)
        self.assertIn("no se puede registrar antes de esa fecha", r.data["detail"])
        # Tampoco si el reloj del celular está adelantado.
        adelantado = (timezone.now() + timedelta(days=2)).isoformat()
        r = self.registrar(self.completo(guardado_en_dispositivo=adelantado))
        self.assertEqual(r.status_code, 400)
        self.assertTrue(self.sigue_programada())


class VisitaAtrasadaTests(APITestCase):
    """RF-02 versión 3: una visita atrasada se registra mientras siga siendo su mes."""

    AHORA = datetime(2026, 11, 18, 14, 30, tzinfo=zona.utc)  # miércoles 18 de noviembre, 11:30 en Santiago

    def setUp(self):
        reloj = mock.patch("terreno.registro.timezone.now", return_value=self.AHORA)
        reloj.start()
        self.addCleanup(reloj.stop)
        self.tecnico = Tecnico.objects.create(
            nombre="Luis Muñoz", usuario=get_user_model().objects.create_user("luis", password="x"))
        edificio = Edificio.objects.create(nombre="Edificio Plaza", direccion="Lira 157", comuna="Santiago",
                                           tipo_uso="residencial", tecnico_asignado=self.tecnico)
        self.ascensor = Ascensor.objects.create(edificio=edificio, identificador="A3", tipo="electrico")
        self.puntos = list(PuntoChecklist.objects.filter(activo=True))
        self.client.force_authenticate(self.tecnico.usuario)

    def registrar(self, fecha, **extra):
        visita = Visita.objects.create(ascensor=self.ascensor, tecnico=self.tecnico, mes=fecha.replace(day=1), fecha=fecha)
        datos = {"visita": visita.id, "operativo": True,
                 "respuestas": [{"punto": p.id, "resultado": "bien"} for p in self.puntos], **extra}
        return self.client.post("/api/mantenciones/", datos, format="json")

    def test_visita_atrasada_del_mismo_mes_se_registra(self):
        r = self.registrar(date(2026, 11, 16))
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["fecha_programada"], "2026-11-16")

    def test_visita_de_un_mes_que_ya_termino_no_se_registra(self):
        r = self.registrar(date(2026, 10, 30))
        self.assertEqual(r.status_code, 400)
        self.assertIn("Esta visita era de octubre de 2026 y ese mes ya terminó", r.data["detail"])
        self.assertEqual(RegistroMantencion.objects.count(), 0)

    def test_vale_la_hora_en_que_se_guardo_en_el_celular(self):
        """Guardada sin señal el día de la visita y recibida después: queda con la hora del celular."""
        r = self.registrar(date(2026, 11, 17), guardado_en_dispositivo="2026-11-17T16:05:00-03:00")
        self.assertEqual(r.status_code, 201, r.data)
        guardado = RegistroMantencion.objects.get().guardado_en_dispositivo
        self.assertEqual(timezone.localtime(guardado).strftime("%d-%m-%Y %H:%M"), "17-11-2026 16:05")


class FallaDelEquipoTests(ConVisitaDeHoy):
    """RF-03: si el equipo queda detenido hay que describir la falla."""

    def test_falla_sin_describir_no_se_guarda(self):
        """RF-03 CA-01."""
        r = self.registrar(self.completo(operativo=False))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data["detail"], "No se guardó: el equipo quedó detenido, describe la falla.")
        self.assertIn("falla_descripcion", r.data)
        self.assertTrue(self.sigue_programada())

    def test_falla_descrita_queda_a_la_vista_del_jefe_tecnico(self):
        """RF-03 CA-02: la visita queda Realizada, el equipo detenido y el jefe técnico ve la falla."""
        r = self.registrar(self.completo(operativo=False, falla_descripcion="Freno con ruido; equipo detenido"))
        self.assertEqual(r.status_code, 201, r.data)
        self.assertFalse(r.data["operativo"])
        self.visita.refresh_from_db()
        self.assertEqual(self.visita.estado, Visita.Estado.REALIZADA)
        self.client.force_authenticate(self.jefe)
        mes = self.visita.mes.strftime("%Y-%m")
        detenidos = self.client.get(f"/api/mantenciones/?mes={mes}&detenidos=1").data
        self.assertEqual([(d["edificio_nombre"], d["ascensor_identificador"], d["falla_descripcion"]) for d in detenidos],
                         [("Edificio Plaza", "A3", "Freno con ruido; equipo detenido")])
        self.assertFalse(self.client.get(f"/api/visitas/{self.visita.id}/").data["registro"]["operativo"])

    def test_si_quedo_operativo_no_se_guarda_una_falla(self):
        r = self.registrar(self.completo(falla_descripcion="texto que sobró"))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["falla_descripcion"], "")
        self.assertEqual(self.client.get("/api/mantenciones/?detenidos=1").data, [])


class QuienRegistraTests(ConVisitaDeHoy):
    """H06: solo el técnico de la visita registra su mantención."""

    def test_otro_tecnico_no_registra_la_visita(self):
        self.client.force_authenticate(self.otro.usuario)
        r = self.registrar(self.completo())
        self.assertEqual(r.status_code, 403)
        self.assertIn("Esta visita está asignada a Luis Muñoz", r.data["detail"])
        self.assertTrue(self.sigue_programada())

    def test_el_jefe_tecnico_no_registra_por_el_tecnico(self):
        self.client.force_authenticate(self.jefe)
        self.assertEqual(self.registrar(self.completo()).status_code, 403)
        self.assertTrue(self.sigue_programada())

    def test_sin_sesion_no_se_registra(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.registrar(self.completo()).status_code, 401)


class EnvioSinConexionTests(ConVisitaDeHoy):
    """Base de RNF-01 en el servidor: cada checklist queda una sola vez aunque el celular repita el envío."""

    def test_reenvio_con_el_mismo_id_local_no_duplica(self):
        datos = self.completo(id_local=str(uuid.uuid4()))
        primero = self.registrar(datos)
        self.assertEqual(primero.status_code, 201)
        segundo = self.registrar(datos)
        self.assertEqual(segundo.status_code, 200)
        self.assertEqual(segundo.data["id"], primero.data["id"])
        self.assertEqual(RegistroMantencion.objects.count(), 1)

    def test_diez_checklists_guardados_sin_senal_llegan_una_sola_vez(self):
        """Diez registros pendientes de una jornada, enviados dos veces: quedan diez, ninguno repetido."""
        hoy = timezone.localdate()
        envios = []
        for i in range(10):
            ascensor = Ascensor.objects.create(edificio=self.ascensor.edificio, identificador=f"B{i}", tipo="electrico")
            visita = Visita.objects.create(ascensor=ascensor, tecnico=self.tecnico, mes=hoy.replace(day=1), fecha=hoy)
            envios.append(self.completo(visita=visita.id, id_local=str(uuid.uuid4())))
        for datos in envios + envios:
            self.assertIn(self.registrar(datos).status_code, (200, 201))
        self.assertEqual(RegistroMantencion.objects.count(), 10)
        self.assertEqual(len(set(RegistroMantencion.objects.values_list("id_local", flat=True))), 10)
        self.assertEqual(Visita.objects.filter(estado=Visita.Estado.REALIZADA).count(), 10)


class ReinicioDeLaDemostracionTests(APITestCase):
    def test_recargar_la_cartera_borra_tambien_las_mantenciones(self):
        """Las mantenciones protegen a su visita; recargar la demostración igual deja todo limpio."""
        call_command("cargar_demo", stdout=StringIO())
        tecnico = Tecnico.objects.get(usuario__username="luis")
        hoy = timezone.localdate()
        ascensor = Ascensor.objects.filter(edificio__tecnico_asignado=tecnico).first()
        visita = Visita.objects.create(ascensor=ascensor, tecnico=tecnico, mes=hoy.replace(day=1), fecha=hoy)
        self.client.force_authenticate(tecnico.usuario)
        puntos = PuntoChecklist.objects.filter(activo=True)
        r = self.client.post("/api/mantenciones/", {"visita": visita.id, "operativo": True,
                             "respuestas": [{"punto": p.id, "resultado": "bien"} for p in puntos]}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        call_command("cargar_demo", borrar=True, stdout=StringIO())
        self.assertEqual((RegistroMantencion.objects.count(), Visita.objects.count()), (0, 0))
        self.assertEqual(Ascensor.objects.count(), 140)
        self.assertEqual(PuntoChecklist.objects.count(), 8)
