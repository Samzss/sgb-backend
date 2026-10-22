from datetime import datetime, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from library import services
from library.models import LibraryUser


class FineRulesTests(TestCase):
    def test_tabla_de_multas(self):
        self.assertEqual([services.fine_amount(n) for n in (0, 1, 2, 7, 8, 10)], [0, 1000, 2500, 2500, 2600, 2800])

    def test_dias_habiles(self):
        due = timezone.make_aware(datetime(2026, 10, 16, 12))  # viernes
        ret = due + timedelta(days=4)  # martes siguiente: lunes y martes cuentan
        self.assertEqual(services.business_days_late(due, ret), 2)


class LoanFlowTests(TestCase):
    def setUp(self):
        call_command("seed_users", verbosity=0)
        self.api = APIClient()
        self.student = LibraryUser.objects.filter(rol="estudiante").first()
        self.librarian = LibraryUser.objects.filter(rol="bibliotecario").first()

    def test_seed_minimos(self):
        self.assertEqual(LibraryUser.objects.filter(rol="estudiante").count(), 50)
        self.assertEqual(LibraryUser.objects.filter(rol="profesor").count(), 10)
        self.assertEqual(LibraryUser.objects.filter(rol="bibliotecario").count(), 3)

    def test_prestar_renovar_devolver(self):
        r = self.api.post("/api/loans", {"user": self.student.id, "librarian": self.librarian.id,
                                         "resource_code": "978-958-1001-0", "collection": "reserva"}, format="json")
        self.assertEqual(r.status_code, 201)
        loan_id = r.json()["id"]
        # reserva: 0 renovaciones
        r = self.api.post(f"/api/loans/{loan_id}/renew", {"librarian": self.librarian.id}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.api.post(f"/api/loans/{loan_id}/return").status_code, 200)

    def test_estudiante_no_puede_prestar(self):
        r = self.api.post("/api/loans", {"user": self.student.id, "librarian": self.student.id,
                                         "resource_code": "x", "collection": "general"}, format="json")
        self.assertEqual(r.status_code, 409)
