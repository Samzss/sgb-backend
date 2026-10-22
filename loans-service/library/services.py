"""Capa lógica: reglas de negocio de préstamos, renovaciones y multas."""
import json
import urllib.error
import urllib.request
from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

from .models import Fine, Loan

POLICIES = {  # colección -> (días de préstamo, máx. renovaciones)
    "general": (15, 5),
    "reserva": (5, 0),
    "referencia": (3, 2),
    "hemeroteca": (1, 1),
    "mapoteca": (1, 0),
    "tecnoteca": (7, 2),
}


class BusinessError(Exception):
    pass


def compute_due_date(collection, start):
    days, _ = POLICIES[collection]
    if collection == "mapoteca":  # 1 día, hasta las 21h
        local = timezone.localtime(start)
        return timezone.make_aware(datetime.combine(local.date(), time(21, 0)))
    return start + timedelta(days=days)


def business_days_late(due_at, returned_at):
    """Cuenta días hábiles (lun-vie) de atraso entre due_at y returned_at."""
    day, count = timezone.localtime(due_at).date(), 0
    end = timezone.localtime(returned_at).date()
    while day < end:
        day += timedelta(days=1)
        if day.weekday() < 5:
            count += 1
    return count


def fine_amount(late_days):
    """1er día 1000; 2º-7º día 2500; desde el 8º se suman 100 COP por cada día extra."""
    if late_days <= 0:
        return 0
    if late_days == 1:
        return 1000
    if late_days <= 7:
        return 2500
    return 2500 + 100 * (late_days - 7)


def has_unpaid_fines(user):
    return Fine.objects.filter(user=user, paid=False).exists()


def create_loan(user, librarian, resource_code, collection):
    if collection not in POLICIES:
        raise BusinessError("Colección inválida")
    if librarian.rol != "bibliotecario":
        raise BusinessError("Solo un bibliotecario puede registrar el préstamo")
    if has_unpaid_fines(user):
        raise BusinessError("El usuario tiene multas pendientes")
    _catalog_take_copy(resource_code)
    now = timezone.now()
    return Loan.objects.create(
        user=user, librarian=librarian, resource_code=resource_code,
        collection=collection, due_at=compute_due_date(collection, now),
    )


def return_loan(loan):
    if loan.returned_at:
        raise BusinessError("El préstamo ya fue devuelto")
    loan.returned_at = timezone.now()
    loan.save(update_fields=["returned_at"])
    late = business_days_late(loan.due_at, loan.returned_at)
    if late > 0:
        Fine.objects.create(loan=loan, user=loan.user, resource_code=loan.resource_code,
                            days=late, amount_cop=fine_amount(late))
    _catalog_return_copy(loan.resource_code)
    return loan


def renew_loan(loan, librarian):
    _, max_renewals = POLICIES[loan.collection]
    if loan.returned_at:
        raise BusinessError("El préstamo ya fue devuelto")
    if loan.renewals >= max_renewals:
        raise BusinessError("Se alcanzó el máximo de renovaciones")
    if has_unpaid_fines(loan.user):
        raise BusinessError("El usuario tiene multas pendientes")
    # TODO: bloquear renovación si hay cola de reservas del recurso (general/tabletas)
    days, _ = POLICIES[loan.collection]
    loan.due_at = loan.due_at + timedelta(days=days)
    loan.renewals += 1
    loan.save(update_fields=["due_at", "renewals"])
    loan.renewal_log.create(resource_code=loan.resource_code, user=loan.user, librarian=librarian)
    return loan


# --- Comunicación con el servicio de catálogo (opcional, vía CATALOG_URL) ---
def _catalog_call(method, path, payload=None):
    if not settings.CATALOG_URL:
        return None
    req = urllib.request.Request(
        f"{settings.CATALOG_URL}{path}", method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise BusinessError("El recurso no existe en el catálogo")
        raise BusinessError(f"Error del catálogo: {e.code}")
    except urllib.error.URLError:
        raise BusinessError("Servicio de catálogo no disponible")


def _catalog_take_copy(code):
    res = _catalog_call("GET", f"/api/resources/{code}")
    if res is None:
        return
    if res.get("available_copies") is not None:
        if res["available_copies"] < 1:
            raise BusinessError("No hay ejemplares disponibles")
        left = res["available_copies"] - 1
        _catalog_call("PATCH", f"/api/resources/{code}",
                      {"available_copies": left, "status": "Prestado" if left == 0 else "Disponible"})


def _catalog_return_copy(code):
    res = _catalog_call("GET", f"/api/resources/{code}")
    if res and res.get("available_copies") is not None:
        _catalog_call("PATCH", f"/api/resources/{code}",
                      {"available_copies": res["available_copies"] + 1, "status": "Disponible"})
