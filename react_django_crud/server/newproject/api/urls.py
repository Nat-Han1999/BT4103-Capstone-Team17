from django.urls import path
from .views import get_books,create_book,book_detail # Function that you want to test

urlpatterns = [
    path('books/', get_books, name = 'get_books'), # Must copy URL pattern to urls.pt in newproject folder
    path('books/create/', create_book, name ="create_book"),
    path('books/<int:pk>', book_detail, name='book_detail')
]