from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=100)
    template = models.CharField(blank=False)

    class Meta:
        verbose_name_plural = "Channels"

    def __str__(self):
        return self.name.capitalize()
