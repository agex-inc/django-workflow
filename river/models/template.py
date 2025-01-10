from django.db import models

class Template(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(
        help_text="You can use variables like {{borrower_name}} and {{seller_name}} which will be automatically replaced with the corresponding value."
    )
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE)
    actor = models.ForeignKey('Actor', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'river'
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name.capitalize()
    
    def render_template(self, **kwargs):
        return self.template.format(**kwargs)
