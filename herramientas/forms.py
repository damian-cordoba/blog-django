from decimal import Decimal

from django import forms

from .diagnostico import PREGUNTAS


def _dinero(label, help_text="", required=True):
    return forms.DecimalField(
        label=label,
        help_text=help_text,
        required=required,
        min_value=Decimal("0"),
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "inputmode": "decimal"}),
    )


def _porcentaje(label, help_text="", required=True, maximo=Decimal("99.9")):
    return forms.DecimalField(
        label=label,
        help_text=help_text,
        required=required,
        min_value=Decimal("0"),
        max_value=maximo,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "inputmode": "decimal"}),
    )


class PuntoEquilibrioForm(forms.Form):
    costos_fijos = _dinero("Costos fijos mensuales ($)", "Alquiler, sueldos, servicios, abonos: lo que pagás vendas o no.")
    precio = _dinero("Precio de venta por unidad ($)", "Sin IVA.")
    costo_variable = _dinero("Costo variable por unidad ($)", "Mercadería, insumos o comisiones por cada unidad vendida.")
    ganancia_deseada = _dinero("Ganancia mensual deseada ($)", "Opcional.", required=False)

    def clean(self):
        datos = super().clean()
        precio, costo = datos.get("precio"), datos.get("costo_variable")
        if precio is not None and costo is not None and precio <= costo:
            raise forms.ValidationError("El precio tiene que ser mayor que el costo variable por unidad.")
        return datos


class PrecioMargenForm(forms.Form):
    MODOS = [
        ("margen", "Tengo el margen que quiero y busco el precio"),
        ("precio", "Tengo el precio y quiero saber mi margen"),
    ]
    modo = forms.ChoiceField(choices=MODOS, initial="margen", widget=forms.RadioSelect)
    costo = _dinero("Costo por unidad ($)", "Lo que te cuesta el producto o servicio, sin IVA.")
    margen = _porcentaje("Margen deseado (%)", "Porcentaje de ganancia sobre el precio de venta.", required=False)
    precio = _dinero("Precio de venta ($)", "Sin IVA.", required=False)
    iva = forms.TypedChoiceField(
        label="Mostrar precio con IVA",
        choices=[("", "No"), ("21", "21 %"), ("10.5", "10,5 %"), ("27", "27 %")],
        coerce=Decimal,
        empty_value=None,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean(self):
        datos = super().clean()
        modo = datos.get("modo")
        if modo == "margen" and datos.get("margen") is None:
            self.add_error("margen", "Ingresá el margen que querés obtener.")
        if modo == "precio":
            if not datos.get("precio"):
                self.add_error("precio", "Ingresá el precio de venta.")
        return datos


class DescuentoForm(forms.Form):
    margen = _porcentaje("Margen actual (%)", "Ganancia sobre el precio de venta, antes del descuento.")
    descuento = _porcentaje("Descuento a aplicar (%)", "Por ejemplo, una promoción del 15 %.")

    def clean(self):
        datos = super().clean()
        m, d = datos.get("margen"), datos.get("descuento")
        if m is not None and d is not None and d >= m:
            raise forms.ValidationError(
                "Con ese descuento vendés al costo o a pérdida: no hay volumen de ventas que compense la ganancia."
            )
        return datos


class DiagnosticoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for numero, (clave, area, texto, opciones, _) in enumerate(PREGUNTAS, start=1):
            self.fields[clave] = forms.ChoiceField(
                label=f"{numero}. {texto}",
                choices=[(str(i), opcion) for i, opcion in enumerate(opciones)],
                widget=forms.RadioSelect,
                error_messages={"required": "Elegí una opción."},
            )
            self.fields[clave].area = area
