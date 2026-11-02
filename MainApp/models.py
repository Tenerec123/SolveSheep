from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
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


class AreaTag(models.Model):
    class Kind(models.TextChoices):
        COGNITIVE = "cognitive", "Cognitive"
        MATHEMATICAL = "mathematical", "Mathematical"

    kind = models.CharField(max_length=16, choices=Kind.choices)
    name = models.CharField(max_length=80)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("kind", "name"), name="mainapp_area_tag_kind_name_uniq"),
        ]
        ordering = ("kind", "name")

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="problems/")    
    video = models.URLField(blank=True, null=True)

    embedding = VectorField(blank=True, null=True,dimensions=384)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    type_tags = models.ManyToManyField(TypeTag, blank=True)
    area_tags = models.ManyToManyField(
        AreaTag,
        through="ProblemAreaWeight",
        related_name="problems",
        blank=True,
    )
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

    
class ProblemAreaWeight(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="area_weights")
    area = models.ForeignKey(AreaTag, on_delete=models.CASCADE, related_name="problem_weights")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001")), MaxValueValidator(Decimal("1.0000"))],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("problem", "area"), name="mainapp_problem_area_uniq"),
            models.CheckConstraint(check=models.Q(weight__gt=0, weight__lte=1), name="mainapp_area_weight_range"),
        ]

    def __str__(self):
        return f"{self.problem}: {self.area} ({self.weight})"


class ProblemProgress(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SOLVED = "solved", "Solved"
        GIVEN_UP = "given_up", "Given up"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="problem_progress")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="user_progress")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "problem"), name="mainapp_progress_user_problem_uniq"),
        ]

    def __str__(self):
        return f"{self.user}: {self.problem} ({self.status})"


class ProblemAttempt(models.Model):
    class Outcome(models.TextChoices):
        PENDING = "pending", "Pending"
        SOLVED = "solved", "Solved"
        GIVEN_UP = "given_up", "Given up"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="problem_attempts")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attempts")
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("attempted_at", "pk")

    def __str__(self):
        return f"{self.user}: {self.problem} ({self.outcome})"


class AreaRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="area_ratings")
    area = models.ForeignKey(AreaTag, on_delete=models.CASCADE, related_name="user_ratings")
    rating = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "area"), name="mainapp_area_rating_user_area_uniq"),
        ]

    def __str__(self):
        return f"{self.user}: {self.area} ({self.rating})"


class ProblemHint(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="hints")
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    text = models.TextField()

    class Meta:
        ordering = ("position", "pk")
        constraints = [
            models.UniqueConstraint(fields=("problem", "position"), name="mainapp_hint_problem_position_uniq"),
            models.CheckConstraint(check=models.Q(position__gte=1), name="mainapp_hint_position_positive"),
        ]

    def __str__(self):
        return f"{self.problem} — hint {self.position}"


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
        
        if self.pk and self.embedding:
            orig = Bundle.objects.get(pk=self.pk)
            update_embeds = (orig.title != self.title) or (orig.description != self.description)

        if not self.embedding or update_embeds:
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
