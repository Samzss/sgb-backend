"""Capa de presentación del servicio: controladores REST."""
from django.db import connection
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Fine, LibraryUser, Loan, Reservation
from .serializers import FineSerializer, LibraryUserSerializer, LoanSerializer, ReservationSerializer


class HealthView(APIView):
    def get(self, request):
        with connection.cursor() as c:
            c.execute("SELECT 1")
        return Response({"service": "loans", "status": "ok", "db": connection.vendor})


class UserViewSet(viewsets.ModelViewSet):
    queryset = LibraryUser.objects.order_by("id")
    serializer_class = LibraryUserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.query_params.get("rol")
        return qs.filter(rol=rol) if rol else qs


class LoanViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Loan.objects.select_related("user", "librarian").order_by("-loaned_at")
    serializer_class = LoanSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            loan = services.create_loan(d["user"], d["librarian"], d["resource_code"], d["collection"])
        except services.BusinessError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        return Response(self.get_serializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="return")
    def return_(self, request, pk=None):
        try:
            loan = services.return_loan(self.get_object())
        except services.BusinessError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        try:
            librarian = LibraryUser.objects.get(pk=request.data.get("librarian"), rol="bibliotecario")
            loan = services.renew_loan(self.get_object(), librarian)
        except LibraryUser.DoesNotExist:
            return Response({"detail": "Bibliotecario inválido"}, status=400)
        except services.BusinessError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        return Response(self.get_serializer(loan).data)


class ReservationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class FineViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Fine.objects.order_by("-created_at")
    serializer_class = FineSerializer
