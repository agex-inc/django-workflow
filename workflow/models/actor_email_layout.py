from django.db import models
from workflow.models import Actor, EmailLayout

class ActorEmailLayout(models.Model):
    actor = models.ForeignKey(Actor, related_name= 'actors_email_layouts',  on_delete=models.CASCADE)
    email_layout = models.ForeignKey(EmailLayout, related_name= 'email_layout_actors', on_delete=models.CASCADE)


    class Meta:
        app_label = 'workflow'
        verbose_name = "Actor Email Layout"
        verbose_name_plural = "Actor Email Layouts"
        unique_together = ('actor', 'email_layout')

    def __str__(self):
        return self.actor.name + " - " + self.email_layout.name