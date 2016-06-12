from django.db import models

# Create your models here.
class Account(models.Model):
    username=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    interest=models.CharField(max_length=20)
    start_time=models.DateField(null=True,blank=True)
    end_time=models.DateField(null=True,blank=True)
    liveness=models.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.username
