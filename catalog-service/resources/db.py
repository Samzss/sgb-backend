"""Acceso a MongoDB (capa de persistencia del servicio)."""
from django.conf import settings

_client = None


def get_db():
    global _client
    if _client is None:
        if settings.MONGO_URI.startswith("mongomock"):
            import mongomock  # solo en tests

            _client = mongomock.MongoClient()
        else:
            from pymongo import MongoClient

            _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client[settings.MONGO_DB_NAME]


def resources():
    return get_db()["resources"]
