from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

TAMANIO_MAXIMO_AVATAR = 2 * 1024 * 1024  # 2 MB


def agregar_clases_bootstrap(form):
    """Aplica las clases de Bootstrap a todos los campos de un formulario."""
    for campo in form.fields.values():
        widget = campo.widget
        if isinstance(widget, forms.CheckboxInput):
            continue
        clase = "form-select" if isinstance(widget, forms.Select) else "form-control"
        widget.attrs["class"] = f"{widget.attrs.get('class', '')} {clase}".strip()


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agregar_clases_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agregar_clases_bootstrap(self)


class UsuarioForm(forms.ModelForm):
    """Datos básicos del usuario que se pueden editar desde el perfil."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "Nombre", "last_name": "Apellido", "email": "Correo electrónico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        agregar_clases_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otra cuenta con ese correo.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "sitio_web"]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Contá en pocas líneas a qué te dedicás"}),
            "sitio_web": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agregar_clases_bootstrap(self)

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "size") and avatar.size > TAMANIO_MAXIMO_AVATAR:
            raise forms.ValidationError("El avatar no puede superar los 2 MB.")
        return avatar
