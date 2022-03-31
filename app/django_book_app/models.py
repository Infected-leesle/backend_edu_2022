from django.db import models


class Book(models.Model):
    title = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    author = models.CharField(max_length=40, blank=True)
    pubYear = models.DecimalField(max_digits=4, decimal_places=0, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

