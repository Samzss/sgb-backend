"""Controladores del servicio de catálogo."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import db
from .policies import POLICIES, STATUSES

REQUIRED_FIELDS = ["code", "collection", "title", "total_copies"]


def _clean(doc):
    doc.pop("_id", None)
    return doc


class HealthView(APIView):
    def get(self, request):
        db.get_db().command("ping")
        return Response({"service": "catalog", "status": "ok", "db": "mongodb"})


class CollectionsView(APIView):
    """Colecciones con su política y cuántos recursos tiene cada una."""

    def get(self, request):
        counts = {
            row["_id"]: row["n"]
            for row in db.resources().aggregate(
                [{"$group": {"_id": "$collection", "n": {"$sum": 1}}}]
            )
        }
        data = [{"name": k, "resources": counts.get(k, 0), **v} for k, v in POLICIES.items()]
        return Response(data)


class ResourceListView(APIView):
    def get(self, request):
        query = {}
        if request.query_params.get("collection"):
            query["collection"] = request.query_params["collection"]
        if request.query_params.get("status"):
            query["status"] = request.query_params["status"]
        if request.query_params.get("q"):
            query["title"] = {"$regex": request.query_params["q"], "$options": "i"}
        limit = min(int(request.query_params.get("limit", 50)), 200)
        skip = int(request.query_params.get("skip", 0))
        cursor = db.resources().find(query).sort("code", 1).skip(skip).limit(limit)
        return Response(
            {"total": db.resources().count_documents(query), "results": [_clean(d) for d in cursor]}
        )

    def post(self, request):
        data = dict(request.data)
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            return Response({"detail": f"Faltan campos: {missing}"}, status=400)
        if data["collection"] not in POLICIES:
            return Response({"detail": "Colección inválida"}, status=400)
        if db.resources().find_one({"code": data["code"]}):
            return Response({"detail": "Ya existe un recurso con ese código"}, status=409)
        data.setdefault("status", "Disponible")
        data.setdefault("available_copies", data["total_copies"])
        db.resources().insert_one(data)
        return Response(_clean(data), status=status.HTTP_201_CREATED)


class ResourceDetailView(APIView):
    def get(self, request, code):
        doc = db.resources().find_one({"code": code})
        if not doc:
            return Response({"detail": "No encontrado"}, status=404)
        return Response(_clean(doc))

    def patch(self, request, code):
        """Cambiar estado / ejemplares (lo usará el servicio de préstamos)."""
        changes = {}
        if "status" in request.data:
            if request.data["status"] not in STATUSES:
                return Response({"detail": f"Estado válido: {STATUSES}"}, status=400)
            changes["status"] = request.data["status"]
            if request.data["status"] == "Dado de baja" and not request.data.get("reason"):
                return Response({"detail": "Dar de baja requiere 'reason'"}, status=400)
            if request.data.get("reason"):
                changes["reason"] = request.data["reason"]
        if "available_copies" in request.data:
            changes["available_copies"] = int(request.data["available_copies"])
        res = db.resources().update_one({"code": code}, {"$set": changes})
        if not res.matched_count:
            return Response({"detail": "No encontrado"}, status=404)
        return Response(_clean(db.resources().find_one({"code": code})))
