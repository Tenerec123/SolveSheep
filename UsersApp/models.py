from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular con email y username.
        """
        if not email:
            raise ValueError("El email es obligatorio")
        if not username:
            raise ValueError("El username es obligatorio")

        email = self.normalize_email(email)  # normaliza mayúsculas/minúsculas
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)  # encripta la contraseña
        user.save(using=self._db)    # guarda en la DB
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con email y username.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superusuario debe tener is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superusuario debe tener is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_username_change = models.DateTimeField(null=True, blank=True)

    objects = UserManager()              # dice a Django que use este manager
    USERNAME_FIELD = 'email'             # campo para login
    REQUIRED_FIELDS = ['username']       # campos requeridos en createsuperuser

    def __str__(self):
        return self.username

    # ---------------------------
    # Método de dominio: cooldown
    # ---------------------------
    def can_change_username(self):
        """
        Devuelve True si han pasado más de 30 días desde el último cambio.
        """
        if not self.last_username_change:
            return True
        now = timezone.now()
        return (now - self.last_username_change).days >= 30