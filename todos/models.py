from django.contrib.auth.models import User
from django.db import models

class Todo(models.Model):
    user = models.ForeignKey(to=User, related_name="todos", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.CharField(max_length=255, blank=True, null=True)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.title