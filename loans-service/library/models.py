from django.db import models


class LibraryUser(models.Model):
    class Role(models.TextChoices):
        STUDENT = "estudiante", "Estudiante"
        TEACHER = "profesor", "Profesor"
        LIBRARIAN = "bibliotecario", "Bibliotecario"

    identificacion = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, blank=True, null=True, unique=True)  # solo estudiantes
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=Role.choices)
    plan = models.CharField(max_length=100, blank=True)
    semestre = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rol})"


class Loan(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="loans")
    librarian = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="loans_made")
    resource_code = models.CharField(max_length=40)  # code del recurso en el servicio de catálogo
    collection = models.CharField(max_length=20)
    loaned_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    renewals = models.PositiveSmallIntegerField(default=0)


class Renewal(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="renewal_log")
    resource_code = models.CharField(max_length=40)
    user = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="+")
    librarian = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)


class Reservation(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="reservations")
    librarian = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="reservations_made")
    resource_code = models.CharField(max_length=40)
    reserved_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)  # desde aquí corren los 5 días para prestar
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["reserved_at"]  # cola por orden de llegada


class Fine(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="fines")
    user = models.ForeignKey(LibraryUser, on_delete=models.PROTECT, related_name="fines")
    resource_code = models.CharField(max_length=40)
    days = models.PositiveIntegerField()  # días hábiles de atraso
    amount_cop = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
