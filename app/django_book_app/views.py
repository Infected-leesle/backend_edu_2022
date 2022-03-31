import mimetypes
import os
from django_filters.rest_framework import DjangoFilterBackend
from django.db.migrations import serializer
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.http import HttpResponse, StreamingHttpResponse
from wsgiref.util import FileWrapper

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from celery.result import AsyncResult

from typing import Any

from .serializers import BookSerializer
from .models import Book
from .post_validators import post_isbn_verificate

from .tasks import generate_many_books, create_book_report


# api/create_books/?count=
@api_view(['GET'])
def create_books(request):
    count = request.GET.get("count")
    generate_many_books.delay(count)
    return Response({"res": "In progress!"}, status=status.HTTP_200_OK)


# api/report
@api_view(['GET', 'POST'])
def report(request):
    if request.method == 'GET':
        if request.GET.get("task_id") is None:
            return Response({"res": "create task or enter task id"}, status=status.HTTP_200_OK)

        task_id = request.GET.get("task_id")
        celery_result = AsyncResult(task_id, app=create_book_report)

        if celery_result.state == "SUCCESS":
            the_file = 'django_book_app/books_report_files/' + str(task_id) + '.csv'
            filename = os.path.basename(the_file)
            chunk_size = 8192
            response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                                             content_type=mimetypes.guess_type(the_file)[0])
            response['Content-Length'] = os.path.getsize(the_file)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response

        return Response({"res": "check task status here: localhost:5555/tasks",
                         "task_id": task_id,
                         "task_status": celery_result.state,
                         "link:": "http://localhost:8080/api/report/?task_id=" + task_id},
                        status=status.HTTP_200_OK)

    elif request.method == 'POST':
        pubYearMin = request.data.get("pubYearMin")
        pubYearMax = request.data.get("pubYearMax")
        if pubYearMin is None and pubYearMax is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        create_book_report_obj = create_book_report.delay(pubYearMin, pubYearMax)
        return redirect("http://localhost:8080/api/report/?task_id=" + create_book_report_obj.task_id)


# api/books
@api_view(['GET', 'POST', 'DELETE'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()

        title = request.query_params.get('title', None)
        if title is not None:
            books = books.filter(title__icontains=title)

        author = request.query_params.get('author', None)
        if author is not None:
            books = books.filter(author__icontains=author)

        pubYear = request.query_params.get('pubYear', None)
        if pubYear is not None:
            books = books.filter(pubYear__icontains=pubYear)

        paginator = Paginator(books, 100)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        books_serializer = BookSerializer(page_obj, many=True)
        return Response(books_serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':

        if not post_isbn_verificate(request.data.get('isbn')):
            return Response({'message': 'isbn wrong!'}, status=status.HTTP_400_BAD_REQUEST)

        book_data = request.data
        book_serializer = BookSerializer(data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
            return Response(book_serializer.data, status=status.HTTP_201_CREATED)
        return Response(book_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Book.objects.all().delete()
        return Response({"res": "objects deleted!"}, status=status.HTTP_200_OK)


# api/books/<int>
@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({'message': 'The book does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        book_serializer = BookSerializer(book)
        return Response(book_serializer.data)

    elif request.method == 'PUT':
        book_data = JSONParser().parse(request)
        book_serializer = BookSerializer(book, data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
            return Response(book_serializer.data)
        return Response(book_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        min_year = self.request.GET.get('pubYearMin')
        max_year = self.request.GET.get('pubYearMax')
        queryset = Book.objects.all()

        if min_year is None and max_year is None:
            return queryset
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if max_year is not None:
            return self.queryset.filter(pubYear__lte=max_year)

        if min_year is not None:
            return self.queryset.filter(pubYear__gte=min_year)

        return self.queryset.filter(pubYear__gte=min_year, pubYear__lte=max_year)

    @api_view(['POST'])
    def post(request: Request) -> Response:
        '''
        Create the book with given book data
        '''

        data = {
            'title': request.data.get('title'),
            'isbn': post_isbn_verificate(request.data.get('isbn').str()),
            'author': request.data.get('author'),
            'pubYear': request.data.get('pubYear'),
            'price': request.data.get('price')
        }
        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        # List all books items for given requested user

        books = Book.objects.filter(book=request.book.id)
        serializer = BookSerializer(books, many=True)

        queryset = Book.objects.all().order_by('id')
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the book with given book data
        '''

        data = {
            'title': request.data.get('title'),
            'isbn': post_isbn_verificate(request.data.get('isbn').str()),
            'author': request.data.get('author'),
            'pubYear': request.data.get('pubYear'),
            'price': request.data.get('price')
        }
        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    @api_view(['GET'])
    def test(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ this is function """

    def get_object(self, book_id):

        # Helper method to get the object with given book_id

        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, book_id, *args, **kwargs):
        '''
        Updates the book item with given book_id if exists
        '''
        book_instance = self.get_object(book_id)
        if not book_instance:
            return Response(
                {"res": "Object with book id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'title': request.data.get('title'),
            'isbn': request.data.get('isbn'),
            'author': request.data.get('author'),
            'pubYear': request.data.get('pubYear'),
            'price': request.data.get('price')
        }
        serializer = BookSerializer(instance=book_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 5. Delete

    def delete(self, request, book_id, *args, **kwargs):
        '''
        Deletes the book item with given book_id if exists
        '''
        book_instance = self.get_object(id)
        if not book_instance:
            return Response(
                {"res": "Object with book id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        book_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
