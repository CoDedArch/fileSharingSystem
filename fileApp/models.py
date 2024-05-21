from django.db import models

# Create your models here.
def image_save_loc(instance, filename):
    return (f'{instance.__class__.__name__}/{filename}')

class File(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    no_downloads = models.IntegerField(default=0)
    no_emails_sent_to = models.IntegerField(default=0)
    file = models.FileField(upload_to=image_save_loc, null=True, blank=True)