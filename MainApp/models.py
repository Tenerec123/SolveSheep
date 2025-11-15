from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class TypeTag(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
    
class DifTag(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="problems/")

    type_tags = models.ManyToManyField(TypeTag)
    dif_tags = models.ManyToManyField(DifTag)

    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    likes_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class Solution(models.Model):
    text = models.CharField(max_length=1000)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='soluciones')

    def __str__(self):
        return self.text[:15]

class Bundle(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="bundles/")

    problems = models.ManyToManyField(Problem, related_name="Problems", blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title