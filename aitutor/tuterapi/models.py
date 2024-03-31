from django.db import models

class request(models.Model):
  user_id = models.IntField()
  request_id = models.IntField()
  question = models.TextField()
  answer = models.TextField()
