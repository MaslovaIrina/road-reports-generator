from django import forms
from django.core.validators import FileExtensionValidator

class UploadExcelForm(forms.Form):
    file = forms.FileField(
        label="Excel файл (.xlsx)",
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx"})
    )