"""Carga datos de prueba con los mínimos exigidos en el enunciado.

  general: 20 libros x 5 ej. | reserva: 20 x 10 | referencia: 20 diccionarios x 3
  hemeroteca: 15 revistas x 2 | mapoteca: 15 mapas | tecnoteca: 5 laptops x 3 + 2 tabletas x 10
Uso: python manage.py seed_catalog
"""
from django.core.management.base import BaseCommand

from resources import db

GENERAL = [
    ("Cien años de soledad", "Gabriel García Márquez"), ("El amor en los tiempos del cólera", "Gabriel García Márquez"),
    ("Rayuela", "Julio Cortázar"), ("La ciudad y los perros", "Mario Vargas Llosa"),
    ("Pedro Páramo", "Juan Rulfo"), ("Ficciones", "Jorge Luis Borges"),
    ("La casa de los espíritus", "Isabel Allende"), ("Don Quijote de la Mancha", "Miguel de Cervantes"),
    ("El túnel", "Ernesto Sábato"), ("Los detectives salvajes", "Roberto Bolaño"),
    ("Crónica de una muerte anunciada", "Gabriel García Márquez"), ("La vorágine", "José Eustasio Rivera"),
    ("María", "Jorge Isaacs"), ("El coronel no tiene quien le escriba", "Gabriel García Márquez"),
    ("Sobre héroes y tumbas", "Ernesto Sábato"), ("La fiesta del chivo", "Mario Vargas Llosa"),
    ("Aura", "Carlos Fuentes"), ("El Aleph", "Jorge Luis Borges"),
    ("Como agua para chocolate", "Laura Esquivel"), ("Cuando era puro cuento", "Antonio Caballero"),
]
RESERVA = [
    ("Ingeniería de Software", "Ian Sommerville"), ("Clean Code", "Robert C. Martin"),
    ("Patrones de diseño", "Erich Gamma"), ("Arquitectura de Software en la práctica", "Len Bass"),
    ("Sistemas de bases de datos", "Silberschatz"), ("Redes de computadoras", "Andrew Tanenbaum"),
    ("Sistemas operativos modernos", "Andrew Tanenbaum"), ("Cálculo", "James Stewart"),
    ("Álgebra lineal", "Stanley Grossman"), ("Estructuras de datos y algoritmos", "Mark Allen Weiss"),
    ("Inteligencia artificial: un enfoque moderno", "Russell y Norvig"), ("Física universitaria", "Sears Zemansky"),
    ("Química general", "Raymond Chang"), ("Probabilidad y estadística", "Walpole"),
    ("Refactoring", "Martin Fowler"), ("Domain-Driven Design", "Eric Evans"),
    ("Introducción a los algoritmos", "Thomas Cormen"), ("Compiladores", "Alfred Aho"),
    ("Ingeniería de requisitos", "Karl Wiegers"), ("Metodologías ágiles", "Ken Schwaber"),
]
DICCIONARIOS = [f"Diccionario {n}" for n in [
    "de la lengua española (RAE)", "de americanismos", "panhispánico de dudas", "inglés-español Collins",
    "francés-español Larousse", "portugués-español", "alemán-español", "etimológico", "de sinónimos y antónimos",
    "de términos informáticos", "de ingeniería", "de matemáticas", "de física", "de química", "de biología",
    "de derecho", "de economía", "de filosofía", "de geografía", "de medicina"]]
REVISTAS = [f"Revista {n}" for n in [
    "Semana", "Cromos", "National Geographic", "Scientific American", "Nature", "IEEE Software", "Communications of the ACM",
    "Ingeniería e Investigación", "Dinero", "El Malpensante", "Revista Javeriana", "Ciencia Hoy", "Muy Interesante",
    "Investigación y Ciencia", "Wired"]]
MAPAS = [(f"Mapa {n}", fmt) for n, fmt in zip([
    "político de Colombia", "físico de Colombia", "hidrográfico de Colombia", "de vías de Colombia", "geológico de Colombia",
    "de resguardos indígenas", "de cuencas hidrográficas", "de zonas climáticas", "de amenaza sísmica", "de cobertura vegetal",
    "mundial político", "de América del Sur", "de relieve de los Andes", "de uso del suelo", "de áreas protegidas"],
    ["jpg", "pdf", "shape", "dwg"] * 4)]


def isbn(i, prefix):
    return f"978-958-{prefix}{i:03d}-0"


class Command(BaseCommand):
    help = "Carga el catálogo de ejemplo en MongoDB"

    def handle(self, *args, **opts):
        col = db.resources()
        col.delete_many({})
        docs = []

        def base(code, collection, title, copies, **extra):
            return {"code": code, "collection": collection, "title": title, "status": "Disponible",
                    "total_copies": copies, "available_copies": copies, **extra}

        for i, (t, a) in enumerate(GENERAL, 1):
            docs.append(base(isbn(i, 1), "general", t, 5, authors=[a], language="es", pages=200 + i * 7,
                             publication_date=f"{1960 + i}-01-01", volume=1, edition=1, publisher="Editorial Demo",
                             summary=f"Resumen de {t}.", binding="tapa dura" if i % 2 else "tapa blanda",
                             dimensions_cm={"width": 14, "height": 21, "depth": 3}))
        for i, (t, a) in enumerate(RESERVA, 1):
            docs.append(base(isbn(i, 2), "reserva", t, 10, authors=[a], language="es", pages=300 + i * 11,
                             publication_date=f"{2000 + i}-01-01", publisher="Editorial Académica", summary=f"Resumen de {t}.",
                             binding="tapa dura", dimensions_cm={"width": 19, "height": 24, "depth": 4}))
        for i, t in enumerate(DICCIONARIOS, 1):
            docs.append(base(isbn(i, 3), "referencia", t, 3, authors=["Varios"], publisher="Editorial Demo", language="es",
                             pages=500 + i * 20, publication_date=f"{1990 + i}-01-01", summary=f"{t}.",
                             dimensions_in={"width": 6.5, "height": 9.5, "depth": 2}))
        for i, t in enumerate(REVISTAS, 1):
            docs.append(base(f"ISSN-{1000 + i}-{2000 + i}", "hemeroteca", t, 2, volume=10 + i, edition=i, publisher="Editorial Demo",
                             language="es", periodicity="mensual", pages=60, publication_date="2026-01-01"))
        for i, (t, fmt) in enumerate(MAPAS, 1):
            # mapas: préstamo en modo lectura por USB, sin cantidad de ejemplares
            docs.append({"code": f"MAP-{i:03d}", "collection": "mapoteca", "title": t, "status": "Disponible",
                         "format": fmt, "description": f"{t} en formato {fmt}.", "total_copies": None, "available_copies": None})
        for i, brand in enumerate(["Lenovo", "HP", "Dell", "Asus", "Acer"], 1):
            docs.append(base(f"LAP-{i:03d}", "tecnoteca", f"Laptop {brand}", 3, kind="laptop", equipment_number=i,
                             brand=brand, model=f"Modelo {i}", charger=True, case=True))
        for i, brand in enumerate(["Samsung", "Apple"], 1):
            docs.append(base(f"TAB-{i:03d}", "tecnoteca", f"Tableta {brand}", 10, kind="tablet", brand=brand,
                             model=f"Tab {i}", charger=True, case=True))

        col.insert_many(docs)
        col.create_index("code", unique=True)
        col.create_index("collection")
        self.stdout.write(self.style.SUCCESS(f"{len(docs)} recursos cargados"))
