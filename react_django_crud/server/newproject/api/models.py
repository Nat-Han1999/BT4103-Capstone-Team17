from django.db import models

class Book(models.Model): #Input accepts a model
    title = models.CharField(max_length=50) # Defining a string in Django
    release_year = models.IntegerField() # Can be rep as an integer

    # Define how the class will be represented
    def __str__(self):
        return self.title # Output when you print a Book