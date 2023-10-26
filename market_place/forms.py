from django import forms
from .models import StorageBox

class StorageBoxForm(forms.ModelForm):
    class Meta:
        model = StorageBox
        fields = ['owner', 'storage_type', 'title', 'description', 'surface', 'street_number', 'route', 'additional_address', 'postal_code', 'city', 'image_1', 'image_2', 'image_3']
