from rest_framework.decorators import api_view # Define HTTP requests eg. 'GET' from backend
from rest_framework.response import Response 
from rest_framework import status 
from .models import Book # Manipulate data and read from DB 
from .seralizer import BookSerializer # Convert data from JSON to Python model when working with API

@api_view(['GET'])
# Test function in urls.py
def get_books(request): # Access request using the argument 
    books = Book.objects.all() # Returns all entries in table
    serializedData = BookSerializer(books, many=True).data # Set many = T as books is an array
    return Response(serializedData)

@api_view(['POST']) # Altering or creating data 
def create_book(request): # Get data from front end and use it to create book
    data = request.data #Access what front-end user is sending 
    serializer = BookSerializer(data=data)
    if serializer.is_valid(): # Req to check if data is valid when trying to serialise from front-end 
        serializer.save() # Save data from frontend to DB
        return Response(serializer.data, status=status.HTTP_201_CREATED) # Tell user there was successful return
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
# Delete and update a book
def book_detail(request, pk): #Access primary key which is identifier of each book
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        data = request.data
        serializer = BookSerializer(book, data.data) # Add book for serializer to know we are not adding a new book but modifying entry
        if serializer.is_valid():
            serializer.save() #Save book data for specific book in database 
            return Response(serializer.data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        