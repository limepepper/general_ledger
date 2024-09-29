from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from general_ledger.models import Contact, Book
from general_ledger.serializers.book import BookSerializer
from general_ledger.serializers.contact import ContactSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
