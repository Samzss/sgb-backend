from django.core.management import call_command
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from resources import db


@override_settings(MONGO_URI="mongomock://", MONGO_DB_NAME="test")
class CatalogApiTests(SimpleTestCase):
    def setUp(self):
        db._client = None
        call_command("seed_catalog", verbosity=0)
        self.client = APIClient()

    def test_seed_minimos(self):
        data = {c["name"]: c["resources"] for c in self.client.get("/api/collections").json()}
        self.assertEqual(data["general"], 20)
        self.assertEqual(data["reserva"], 20)
        self.assertEqual(data["referencia"], 20)
        self.assertEqual(data["hemeroteca"], 15)
        self.assertEqual(data["mapoteca"], 15)
        self.assertEqual(data["tecnoteca"], 7)

    def test_listado_y_detalle(self):
        r = self.client.get("/api/resources?collection=general&limit=5").json()
        self.assertEqual(r["total"], 20)
        self.assertEqual(len(r["results"]), 5)
        code = r["results"][0]["code"]
        self.assertEqual(self.client.get(f"/api/resources/{code}").json()["code"], code)

    def test_baja_requiere_motivo(self):
        code = self.client.get("/api/resources?limit=1").json()["results"][0]["code"]
        self.assertEqual(self.client.patch(f"/api/resources/{code}", {"status": "Dado de baja"}, format="json").status_code, 400)
        ok = self.client.patch(f"/api/resources/{code}", {"status": "Dado de baja", "reason": "Deterioro"}, format="json")
        self.assertEqual(ok.status_code, 200)
