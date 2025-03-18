from django.db import models

# Create your models here.
class File(models.Model):
    path = models.FileField()
    date_created = models.DateTimeField()
    # title = models.CharField(max_length=200, default="")
    hidden = models.BooleanField(default=False)
    # processed = models.BooleanField(default=False)
    # description = models.CharField(max_length=200, default="")
    
    def __str__(self):
        return self.path
    
        
    