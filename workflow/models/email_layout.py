from django.db import models
from workflow.models import Actor

class EmailLayout(models.Model):
    """
    Model to store custom email html or texts for different actors.
    """
    name = models.CharField(max_length=100, unique=True)
    #subject = models.CharField(max_length=255)
    body = models.TextField()
    footer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name.capitalize()