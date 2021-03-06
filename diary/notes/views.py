from django.db.models import Q
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models.functions import Extract

from .serializers import NotesSerializer
from .models import Notes


class NotesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class NotesViewSet(viewsets.ModelViewSet):
    lookup_field = "pk"
    pagination_class = NotesPagination
    serializer_class = NotesSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly,
    # ]

    # Cache object
    def get_object(self, *args, **kwargs):
        if not getattr(self, "_object", None):
            self._object = super().get_object(*args, **kwargs)
        return self._object

    def get_queryset(self):
        notes = Notes.objects.all()

        query = self.request.GET.get("q", None)
        print(query)
        if query is not None:
            notes = notes.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).distinct()

        year = self.request.GET.get("year", None)
        if year is not None:
            notes = notes.filter(created_at__year__icontains=year).distinct()

        month = self.request.GET.get("month", None)
        if month is not None:
            notes = notes.filter(created_at__month__icontains=month).distinct()

        default_order = "desc"
        sorts = {
            "asc": "created_at",
            "desc": "-created_at",
        }
        order_by = sorts.get(self.request.GET.get("sort", default_order))

        notes = notes.order_by(order_by)
        return notes
