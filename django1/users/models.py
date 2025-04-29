from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Member(models.Model):

    member_code = models.CharField(max_length=20, blank=True)
    member_fname = models.CharField(max_length=32)
    member_lname = models.CharField(max_length=32, blank=True)
    member_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.member_user}"