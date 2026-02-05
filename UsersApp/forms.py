from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User  # Tu modelo custom

class CustomUserCreationForm(UserCreationForm):
    """
    This form is used to register new users.
    Child of UserCreationForm to validate passwords.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
            field.help_text = None


    class Meta:
        model = User
        # Definimos qué campos queremos en el formulario de registro.
        # IMPORTANTE: Incluimos email (tu USERNAME_FIELD) y username.
        fields = ('email', 'username')


    # Al heredar de UserCreationForm, ya tenemos 'password1' y 'password2'
    # validados automáticamente por Django.

class CustomUserChangeForm(UserChangeForm):
    password = None
    """
    Este formulario se usa para editar usuarios existentes (normalmente en el Admin).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        help_text_fields = []

        if self.instance and  self.instance.pk and not self.instance.can_change_username():
            self.fields["username"].disabled = True
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
            if name not in help_text_fields:
                field.help_text = None
    
    class Meta:
        model = User
        # Aquí puedes poner todos los campos que quieras que sean editables
        fields = ('email', 'username',)