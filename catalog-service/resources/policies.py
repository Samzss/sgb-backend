"""Reglas por colección (tabla del enunciado)."""

# colección -> (días de préstamo, máximo de renovaciones)
POLICIES = {
    "general": {"loan_days": 15, "max_renewals": 5, "reservable": True},
    "reserva": {"loan_days": 5, "max_renewals": 0, "reservable": False},
    "referencia": {"loan_days": 3, "max_renewals": 2, "reservable": False},
    "hemeroteca": {"loan_days": 1, "max_renewals": 1, "reservable": False},
    "mapoteca": {"loan_days": 1, "max_renewals": 0, "reservable": False},  # hasta las 21h
    "tecnoteca": {"loan_days": 7, "max_renewals": 2, "reservable": False},  # tabletas sí reservables
}

STATUSES = ["Disponible", "Prestado", "Reservado", "Perdido", "Dado de baja"]
