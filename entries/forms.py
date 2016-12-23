
from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = (
            'value_date',
            'label',
            'category',
            'supplier',
            'amount',
            # 'account', # automatically filled from the user
            'paid_by',
            'for_people',
            # 'num_people',
            'payment_type',
            # 'location', # automatically filled from geolocation API
        )


class FileUploadForm(forms.Form):
    """ file upload form to upload prospects file """
    uploaded_file = forms.FileField(
        label="L'export Boursorama",
        widget=forms.FileInput()
    )