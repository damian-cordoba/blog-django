from django import forms

from usuarios.forms import agregar_clases_bootstrap

from .models import Consulta, Servicio


class ConsultaForm(forms.ModelForm):
    # Campo trampa: los humanos no lo ven; si viene completo, es un bot.
    sitio_web = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}))

    class Meta:
        model = Consulta
        fields = ["nombre", "email", "empresa", "telefono", "servicio", "mensaje"]
        widgets = {
            "mensaje": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Contame brevemente qué necesitás o qué problema querés resolver."}
            ),
        }
        labels = {"email": "Correo electrónico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["servicio"].queryset = Servicio.objects.filter(activo=True)
        self.fields["servicio"].empty_label = "No estoy seguro / otro"
        agregar_clases_bootstrap(self)
        self.fields["sitio_web"].widget.attrs["class"] = "campo-trampa"

    def es_spam(self):
        return bool(self.cleaned_data.get("sitio_web"))
