from django import forms

from .models import BookingRequest


FIELD_CLASS = "field-input"


class PhotographerSearchForm(forms.Form):
    specialty = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + [
            ("Wedding", "Wedding"),
            ("Portrait", "Portrait"),
            ("Family", "Family"),
            ("Fashion", "Fashion"),
            ("Travel", "Travel"),
        ],
        widget=forms.Select(attrs={"class": "w-full bg-transparent font-display text-lg italic focus:outline-none"}),
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-transparent font-display text-lg italic placeholder:text-bark/50 focus:outline-none",
            "placeholder": "Kathmandu, Pokhara",
        }),
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "w-full bg-transparent font-display text-lg italic placeholder:text-bark/50 focus:outline-none",
            "type": "date",
        }),
    )


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ["client_name", "client_email", "client_phone", "shoot_date", "package", "message"]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Your name"}),
            "client_email": forms.EmailInput(attrs={"class": FIELD_CLASS, "placeholder": "you@example.com"}),
            "client_phone": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "+977 ..."}),
            "shoot_date": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
            "package": forms.Select(attrs={"class": FIELD_CLASS}),
            "message": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 4, "placeholder": "Tell the photographer about the shoot"}),
        }
