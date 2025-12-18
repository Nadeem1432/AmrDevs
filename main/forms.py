from django import forms

class JsonUploadForm(forms.Form):
    """Form to handle the single JSON file upload."""
    json_file = forms.FileField(
        label='Select JSON Fixture File',
        help_text='Upload a Django fixture JSON file. Duplicates and missing foreign keys will be skipped.'
    )