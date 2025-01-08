from django.db import models

class Template(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField()
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE)
    actor = models.ForeignKey('Actor', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'river'
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name.capitalize() + '-' + self.channel.name.capitalize() + '-' + self.actor.name.capitalize()
    
    def render_template(self, **kwargs):
        return self.template.format(**kwargs)
