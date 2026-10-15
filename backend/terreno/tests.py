import uuid

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import ChecklistPrueba


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
