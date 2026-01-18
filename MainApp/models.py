from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

hex_color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6})$',
    message='Ingrese un color hexadecimal válido, por ejemplo: #ff0000'
)
# Create your models here.

class TypeTag(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, validators=[hex_color_validator], default="#000000")
    def __str__(self):
        return self.name
    
class DifTag(models.Model):
    name = models.FloatField()
    color = models.CharField(max_length=7, validators=[hex_color_validator], default="#000000")
    def __str__(self):
        return str(self.name)

class Problem(models.Model):
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="problems/")

    video = models.URLField(blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    type_tags = models.ManyToManyField(TypeTag, null=True, blank=True)
    dif_tag = models.ForeignKey(DifTag, null=True, blank=True, on_delete=models.SET_NULL)

    likes = models.ManyToManyField(User, related_name='liked_problems', blank=True)
    likes_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def class_name(self):
        return self.__class__.__name__
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    
class Solution(models.Model):
    text = models.CharField(max_length=1000)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='Solutions')

    def __str__(self):
        return self.text[:15]

class Bundle(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="bundles/")

    problems = models.ManyToManyField(Problem, related_name="Problems", blank=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    likes = models.ManyToManyField(User, related_name='liked_bundles', blank=True)
    likes_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def class_name(self):
        return self.__class__.__name__
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
