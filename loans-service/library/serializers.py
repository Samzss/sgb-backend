from rest_framework import serializers

from .models import Fine, LibraryUser, Loan, Reservation


class LibraryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryUser
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ["loaned_at", "due_at", "returned_at", "renewals"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ["reserved_at", "notified_at", "active"]


class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = "__all__"
