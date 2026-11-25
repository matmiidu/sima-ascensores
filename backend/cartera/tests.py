from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase

from .models import Ascensor, Edificio, Tecnico


class RegistroCarteraTests(APITestCase):
    """Criterios de aceptación de H01."""

    def setUp(self):
        self.user = get_user_model().objects.create_user("jefe", password="x", is_staff=True)
        self.client.force_authenticate(self.user)
        self.tecnico = Tecnico.objects.create(nombre="Juan Pérez")

    def crear_edificio(self, **extra):
        datos = {"nombre": "Edificio Mirador", "direccion": "Los Leones 1234", "comuna": "Providencia",
                 "tipo_uso": "residencial", "tecnico_asignado": self.tecnico.id, **extra}
        return self.client.post("/api/edificios/", datos, format="json")

    def test_registra_edificio_con_tipo_de_uso(self):
        r = self.crear_edificio()
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["tipo_uso_display"], "Residencial")
        self.assertEqual(r.data["tecnico_nombre"], "Juan Pérez")

    def test_tipo_de_uso_es_obligatorio_y_de_la_lista(self):
        self.assertEqual(self.crear_edificio(tipo_uso="").status_code, 400)
        self.assertEqual(self.crear_edificio(tipo_uso="industrial").status_code, 400)

    def test_no_duplica_la_misma_direccion(self):
        self.crear_edificio()
        r = self.crear_edificio(nombre="Otro nombre")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Ya hay un edificio registrado", r.data["direccion"][0])

    def test_registra_ascensores_y_aparecen_en_su_edificio(self):
        edificio_id = self.crear_edificio().data["id"]
        for ident in ["A1", "A2"]:
            r = self.client.post("/api/ascensores/", {
                "edificio": edificio_id, "identificador": ident, "tipo": "electrico", "paradas": 8,
                "vencimiento_certificacion": "2027-03-31",
            }, format="json")
            self.assertEqual(r.status_code, 201, r.data)
        r = self.client.get(f"/api/edificios/{edificio_id}/")
        self.assertEqual(r.data["total_ascensores"], 2)
        self.assertEqual([a["identificador"] for a in r.data["ascensores"]], ["A1", "A2"])

    def test_identificador_unico_dentro_del_edificio(self):
        edificio_id = self.crear_edificio().data["id"]
        datos = {"edificio": edificio_id, "identificador": "A1", "tipo": "electrico", "paradas": 5}
        self.client.post("/api/ascensores/", datos, format="json")
        r = self.client.post("/api/ascensores/", datos, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Ya existe el ascensor A1 en este edificio", r.data["identificador"][0])

    def test_rechaza_menos_de_dos_paradas(self):
        edificio_id = self.crear_edificio().data["id"]
        r = self.client.post("/api/ascensores/", {"edificio": edificio_id, "identificador": "A1",
                                                  "tipo": "electrico", "paradas": 1}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_busca_por_comuna_y_filtra_por_tipo_de_uso(self):
        self.crear_edificio()
        self.crear_edificio(nombre="Torre Andes", direccion="Apoquindo 3000", comuna="Las Condes", tipo_uso="oficinas")
        self.assertEqual(len(self.client.get("/api/edificios/?q=condes").data), 1)
        self.assertEqual(len(self.client.get("/api/edificios/?tipo_uso=residencial").data), 1)

    def test_exige_sesion(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/edificios/").status_code, 401)


class CargaDemoTests(APITestCase):
    def test_la_cartera_ficticia_tiene_el_tamano_del_caso(self):
        call_command("cargar_demo", stdout=StringIO())
        self.assertEqual(Edificio.objects.count(), 62)
        self.assertEqual(Edificio.objects.filter(tipo_uso="residencial").count(), 48)
        self.assertEqual(Ascensor.objects.count(), 140)
        self.assertEqual(Tecnico.objects.count(), 6)

    def test_cada_tecnico_queda_con_su_usuario(self):
        """H04: la carga deja un usuario por técnico y el del jefe técnico."""
        call_command("cargar_demo", stdout=StringIO())
        nombres = {"juan", "rodrigo", "camila", "luis", "andres", "felipe"}
        self.assertEqual(set(Tecnico.objects.values_list("usuario__username", flat=True)), nombres)
        User = get_user_model()
        self.assertTrue(User.objects.get(username="jefe").is_staff)
        self.assertFalse(User.objects.get(username="luis").is_staff)
        # Volver a cargar no cambia los nombres de usuario ni deja usuarios sueltos.
        call_command("cargar_demo", borrar=True, stdout=StringIO())
        self.assertEqual(set(Tecnico.objects.values_list("usuario__username", flat=True)), nombres)
        self.assertEqual(User.objects.count(), 7)


class UsuariosYPermisosTests(APITestCase):
    """H04: cada técnico entra con su usuario; consulta la cartera, pero no la modifica."""

    def setUp(self):
        User = get_user_model()
        self.tecnico = Tecnico.objects.create(nombre="Luis Muñoz", usuario=User.objects.create_user("luis", password="x"))
        self.jefe = User.objects.create_user("jefe", password="x", is_staff=True)

    def test_la_aplicacion_sabe_quien_entro(self):
        self.client.force_authenticate(self.tecnico.usuario)
        r = self.client.get("/api/yo/")
        self.assertEqual(r.data["nombre"], "Luis Muñoz")
        self.assertEqual(r.data["tecnico"], {"id": self.tecnico.id, "nombre": "Luis Muñoz"})
        self.assertFalse(r.data["es_jefe"])
        self.client.force_authenticate(self.jefe)
        r = self.client.get("/api/yo/")
        self.assertTrue(r.data["es_jefe"])
        self.assertIsNone(r.data["tecnico"])

    def test_se_entra_a_la_aplicacion_despues_de_entrar_al_panel(self):
        # El navegador queda con la sesión del panel; el ingreso con usuario y
        # clave no debe pedir el código CSRF por eso (antes daba 403).
        from rest_framework.test import APIClient
        navegador = APIClient(enforce_csrf_checks=True)
        navegador.force_login(self.jefe)
        r = navegador.post("/api/token/", {"username": "jefe", "password": "x"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.data)
        r = navegador.post("/api/token/", {"username": "jefe", "password": "mala"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_un_tecnico_consulta_la_cartera_pero_no_la_modifica(self):
        self.client.force_authenticate(self.tecnico.usuario)
        self.assertEqual(self.client.get("/api/edificios/").status_code, 200)
        r = self.client.post("/api/edificios/", {"nombre": "Edificio Mirador", "direccion": "Los Leones 1234",
                                                 "comuna": "Providencia", "tipo_uso": "residencial"}, format="json")
        self.assertEqual(r.status_code, 403)
        self.assertIn("Solo el jefe técnico", r.data["detail"])
        self.assertEqual(Edificio.objects.count(), 0)


class AlertasCertificacionTests(APITestCase):
    """Criterios de aceptación de H10 (RF-06)."""

    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        User = get_user_model()
        self.jefe = User.objects.create_user("jefe", password="x", is_staff=True)
        self.tecnico = Tecnico.objects.create(nombre="Luis Muñoz", usuario=User.objects.create_user("luis", password="x"))
        self.hoy = timezone.localdate()
        d = lambda n: self.hoy + timedelta(days=n)  # noqa: E731
        self.plaza = Edificio.objects.create(
            nombre="Edificio Plaza", direccion="Lira 157", comuna="Santiago", tipo_uso="residencial",
            administrador_nombre="Patricia Fuentes", administrador_correo="pfuentes@ejemplo.cl",
            administrador_telefono="+56 2 2598 2203")
        self.palmas = Edificio.objects.create(nombre="Edificio Las Palmas", direccion="Av. Grecia 1450", comuna="Ñuñoa",
                                              tipo_uso="oficinas")
        Ascensor.objects.create(edificio=self.plaza, identificador="A1", tipo="electrico", vencimiento_certificacion=d(16))
        Ascensor.objects.create(edificio=self.plaza, identificador="A2", tipo="electrico", vencimiento_certificacion=d(-22))
        Ascensor.objects.create(edificio=self.plaza, identificador="A3", tipo="electrico", vencimiento_certificacion=d(200))
        Ascensor.objects.create(edificio=self.palmas, identificador="A1", tipo="electrico", vencimiento_certificacion=d(0))
        Ascensor.objects.create(edificio=self.palmas, identificador="A2", tipo="electrico", vencimiento_certificacion=None)
        Ascensor.objects.create(edificio=self.palmas, identificador="A3", tipo="electrico", vencimiento_certificacion=d(-5),
                                activo=False)

    def pedir(self, consulta=""):
        self.client.force_authenticate(self.jefe)
        return self.client.get(f"/api/certificaciones/{consulta}")

    def test_separa_vencidas_por_vencer_y_sin_fecha(self):
        r = self.pedir()
        self.assertEqual(r.status_code, 200)
        nombres = lambda lista: [f"{x['edificio']} {x['identificador']}" for x in lista]  # noqa: E731
        self.assertEqual(nombres(r.data["vencidas"]), ["Edificio Plaza A2"])
        # Ordenadas por fecha: la que vence hoy va antes que la de dentro de 16 días.
        self.assertEqual(nombres(r.data["por_vencer"]), ["Edificio Las Palmas A1", "Edificio Plaza A1"])
        self.assertEqual(nombres(r.data["sin_fecha"]), ["Edificio Las Palmas A2"])
        self.assertEqual(r.data["por_vencer"][1]["dias_restantes"], 16)
        self.assertEqual(r.data["vencidas"][0]["dias_restantes"], -22)

    def test_no_avisa_las_vigentes_mas_alla_del_plazo_ni_los_equipos_inactivos(self):
        r = self.pedir()
        todos = r.data["vencidas"] + r.data["por_vencer"] + r.data["sin_fecha"]
        self.assertNotIn(("Edificio Plaza", "A3"), [(x["edificio"], x["identificador"]) for x in todos])
        self.assertNotIn(("Edificio Las Palmas", "A3"), [(x["edificio"], x["identificador"]) for x in todos])
        self.palmas.activo = False
        self.palmas.save()
        r = self.pedir()
        self.assertEqual([x["edificio"] for x in r.data["por_vencer"]], ["Edificio Plaza"])

    def test_cada_alerta_trae_el_contacto_del_administrador(self):
        alerta = self.pedir().data["por_vencer"][1]
        self.assertEqual(alerta["administrador"], {"nombre": "Patricia Fuentes", "correo": "pfuentes@ejemplo.cl",
                                                   "telefono": "+56 2 2598 2203"})
        self.assertEqual(alerta["direccion"], "Lira 157")

    def test_el_plazo_de_anticipacion_se_puede_cambiar_y_se_valida(self):
        r = self.pedir("?dias=10")
        self.assertEqual([x["identificador"] for x in r.data["por_vencer"]], ["A1"])
        self.assertEqual(r.data["por_vencer"][0]["edificio"], "Edificio Las Palmas")
        self.assertEqual(self.pedir("?dias=0").status_code, 400)
        self.assertEqual(self.pedir("?dias=abc").status_code, 400)

    def test_un_tecnico_no_ve_las_alertas(self):
        self.client.force_authenticate(self.tecnico.usuario)
        r = self.client.get("/api/certificaciones/")
        self.assertEqual(r.status_code, 403)
        self.assertIn("Solo el jefe técnico", r.data["detail"])
