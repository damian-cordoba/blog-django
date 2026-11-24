from django import forms

from .models import Post

TAMANIO_MAXIMO_IMAGEN = 5 * 1024 * 1024  # 5 MB


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["titulo", "subtitulo", "categoria", "contenido", "imagen"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título"}),
            "subtitulo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Una frase que resuma el post"}
            ),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "contenido": forms.Textarea(attrs={"class": "form-control", "rows": 12}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].empty_label = "Sin categoría"

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if imagen and hasattr(imagen, "size") and imagen.size > TAMANIO_MAXIMO_IMAGEN:
            raise forms.ValidationError("La imagen no puede superar los 5 MB.")
        return imagen
