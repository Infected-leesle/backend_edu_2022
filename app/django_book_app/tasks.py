from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task

import csv
import names
import random

from .models import Book


@shared_task(max_retries=1)
def create_book_report(minPubYear, maxPubYear):
    current_id = current_task.request.id

    if minPubYear is not None and maxPubYear is not None:
        with open('django_book_app/books_report_files/' + str(current_id) + '.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('title', 'author', 'pubYear', 'isbn', 'price'))
            books = Book.objects.filter(pubYear__gte=minPubYear,
                                        pubYear__lte=maxPubYear).values_list('title',
                                                                             'author',
                                                                             'pubYear',
                                                                             'isbn',
                                                                             'price')
            writer.writerows(books)


@shared_task(max_retries=1)
def generate_many_books(count):
    for _ in range(int(count)):
        Book.objects.bulk_create([
            Book(title='Python Crash Course', isbn='978-' + str(random.randint(0, 9)) + '-' +
                                                   str(random.randint(10, 99)) + '-' +
                                                   str(random.randint(100000, 999999)) + '-0',
                 author=names.get_full_name(), pubYear=random.randint(1930, 2021), price=random.randint(1, 500)),
        ])
