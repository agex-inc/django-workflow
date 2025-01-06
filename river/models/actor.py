from django.db import models

class Actor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'river'
        verbose_name = "Actor"
        verbose_name_plural = "Actors"

    def __str__(self):
        return self.name.capitalize()
