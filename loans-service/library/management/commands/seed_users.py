"""Carga 50 estudiantes, 10 profesores y 3 bibliotecarios (mínimos del enunciado)."""
from django.core.management.base import BaseCommand

from library.models import LibraryUser

NOMBRES = ["Ana", "Luis", "María", "Carlos", "Sofía", "Juan", "Valentina", "Andrés", "Camila", "Daniel"]
APELLIDOS = ["Gómez", "Rodríguez", "Pérez", "Martínez", "López", "Ramírez", "Torres", "Díaz", "Vargas", "Castro"]


class Command(BaseCommand):
    help = "Carga usuarios de ejemplo"

    def handle(self, *args, **opts):
        LibraryUser.objects.all().delete()
        users = []
        for i in range(50):
            users.append(LibraryUser(identificacion=f"10{i:06d}", codigo=f"2026{i:04d}", nombres=NOMBRES[i % 10],
                                     apellidos=f"{APELLIDOS[(i * 3) % 10]} {APELLIDOS[(i * 7) % 10]}",
                                     correo=f"estudiante{i}@umadeira.edu", rol="estudiante",
                                     plan="Ingeniería de Software", semestre=1 + i % 10))
        for i in range(10):
            users.append(LibraryUser(identificacion=f"20{i:06d}", nombres=NOMBRES[(i + 2) % 10],
                                     apellidos=APELLIDOS[(i + 5) % 10], correo=f"profesor{i}@umadeira.edu", rol="profesor"))
        for i in range(3):
            users.append(LibraryUser(identificacion=f"30{i:06d}", nombres=NOMBRES[(i + 4) % 10],
                                     apellidos=APELLIDOS[(i + 1) % 10], correo=f"biblio{i}@umadeira.edu", rol="bibliotecario"))
        LibraryUser.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS(f"{len(users)} usuarios cargados"))
