from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.urls import include, reverse
from django.conf.urls import url

"""
        Ensure we can create validate isbn when post book object.
"""


class PostValidatorsTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        url(r'^', include('django_book_app.urls')),
    ]

    def test_user_can_post_with_right_isbn_thirteen_nums(self):
        # right data (13 nums and 4 dashes)
        data_case1 = {'title': 'new idea', 'isbn': '978-3-16-148410-0', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case1, format='json')
        response = self.client.get(book_list_url, format='json')
        assert response.status_code == 200

        # import pdb
        # pdb.set_trace()

    def test_user_can_post_with_right_isbn_nine_nums(self):
        # right data (9 nums and 3 dashes)
        data_case2 = {'title': 'new idea', 'isbn': '16-148-410-0', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case2)
        response = self.client.get(book_list_url, format='json')
        assert response.status_code == 200





"""
    def test_user_can_post_with_wrong_isbn_too_short(self):
        # too short data
        data_case3 = {'title': 'new idea', 'isbn': '148410-0', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case3)
        response = self.client.get(book_list_url, format='json')
        assert response.status_code == 400

    def test_user_can_post_with_wrong_isbn_too_long(self):
        # too long data
        data_case4 = {'title': 'new idea', 'isbn': '978-978-3-16-148410-0', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case4)
        response = self.client.get(book_list_url, format='json')
        assert response.status_code == 400

    def test_user_can_post_with_wrong_isbn_only_nums(self):
        # only nums
        data_case5 = {'title': 'new idea', 'isbn': '9783161484100', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case5)
        response = self.client.get(book_list_url)
        import pdb
        pdb.set_trace()
        assert response.status_code == 400

    def test_user_can_post_with_wrong_isbn_many_dashes(self):
        # too many dashes
        data_case6 = {'title': 'new idea', 'isbn': '97-8-3-16-148-410-0', 'author': 'real Author', 'pubYear': '1999',
                      'price': '300'}
        factory = APIRequestFactory()
        book_list_url = reverse('book_list')
        request = factory.post('/books/', data_case6)
        response = self.client.get(book_list_url, format='json')
        assert response.status_code == 400

"""