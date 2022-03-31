from django.contrib import admin

from django_book_app.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'isbn', 'author', 'pubYear', 'price')

    def save_model(self, request, obj, form, change):
        obj.save()

