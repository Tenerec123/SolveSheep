from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.text import slugify
from pgvector.django import VectorField
from sentence_transformers import SentenceTransformer

hex_color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6})$',
    message='Ingrese un color hexadecimal válido, por ejemplo: #ff0000'
)

_embedding_model = None

def get_embedding_model():
    """Load and cache the embedding model on first use"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    return _embedding_model
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
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="problems/")    
    video = models.URLField(blank=True, null=True)

    embedding = VectorField(blank=True, null=True,dimensions=384)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    type_tags = models.ManyToManyField(TypeTag, blank=True)
    dif_tag = models.ForeignKey(DifTag, null=True, blank=True, on_delete=models.SET_NULL)

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_problems', blank=True)
    likes_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def class_name(self):
        return self.__class__.__name__
    
    def save(self, *args, **kwargs):
        if not self.slug:
            clean_title = self.title.replace('$', '').replace('{', '').replace('}', '')
            self.slug = slugify(clean_title)
        
        update_embeds = False
        if not self.embedding:
            update_embeds = True
        if self.pk and update_embeds == False:
            orig = Problem.objects.get(pk=self.pk)
            update_embeds = (orig.title != self.title) or (orig.text != self.text)

        if update_embeds:
            model = get_embedding_model()
            text_to_embed = self.title 
            if self.text:
                text_to_embed += " " + self.text
            self.embedding = model.encode(text_to_embed).tolist()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    
class Solution(models.Model):
    text = models.CharField(max_length=1000)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='Solutions')

    accepted = models.BooleanField(default=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.text[:15]

class Bundle(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="bundles/")

    embedding = VectorField(blank=True, null=True,dimensions=384)

    problems = models.ManyToManyField(Problem, related_name="Problems", blank=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_bundles', blank=True)
    likes_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    needs_reload = models.BooleanField(default=False)
    relodeable = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def class_name(self):
        return self.__class__.__name__
    
    def save(self, *args, **kwargs):
        if not self.slug:
            clean_title = self.title.replace('$', '').replace('{', '').replace('}', '')
            self.slug = slugify(clean_title)
        
        update_embeds = False
        if not self.embedding:
            update_embeds = True
        if self.pk and update_embeds == False:
            orig = Problem.objects.get(pk=self.pk)
            update_embeds = (orig.title != self.title) or (orig.description != self.description)

        if update_embeds:
            model = get_embedding_model()
            text_to_embed = self.title 
            if self.description:
                text_to_embed += " " + self.description
            self.embedding = model.encode(text_to_embed).tolist()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
