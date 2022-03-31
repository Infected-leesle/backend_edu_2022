from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^api/books/$', views.book_list, name="book_list"),
    url(r'^api/books/(?P<pk>[0-9]+)$', views.BookDetailApiView),
    path("api/create_books/", views.create_books, name="create_books"),
    url(r'^api/report/', views.report, name="report"),
]
