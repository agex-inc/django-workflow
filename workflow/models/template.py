from django.db import models
from django.utils.safestring import mark_safe

class Template(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(
        help_text=mark_safe("""
        You can use variables like {borrower_name} and {seller_name} which will be automatically replaced with the corresponding value.
        <ul>
            <li>Use {borrower_name} for the borrower's name</li>
            <li>Use {seller_name} for the seller's name</li>
            <li>Use {amount} for the trade amount</li>
            <li>Use {trade_id} for the trade ID</li>
            <li>Use {status} for the trade status</li>
            <li>Use {due_date} for the trade due date</li>
        </ul>
        """)
    )
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE)
    actor = models.ForeignKey('Actor', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'workflow'
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name.capitalize()
    
    def render_template(self, **kwargs):
        return self.template.format(**kwargs)
